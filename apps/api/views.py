import os
import signal
import subprocess
from django.conf import settings
from django.utils import timezone
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import APIException
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import ExecutionSerializer, RunSerializer
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from apps.main.models import Execution


if not settings.DEPLOYED:
    cmd = ['/home/ass04490/virtualenvs/easypy/bin/python',
           '/home/ass04490/whome/gitrepos/easypy/easypy/scripts/script.py']
    execution_content = 'logger2.log'
else:
    cmd = ['/home/easypy/venv/bin/python', '/home/easypy/brain/script.py']
    execution_content = '/home/easypy/brain/BACKTEST_METRICS'


current_executions = []


class Broadcast(APIView):
    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    def post(self, request, *args, **kwargs):
        if not request.data:
            return Response(
                {'error': 'data could not be procesed', 'detail': 'no data was provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            print(request.data)
            async_to_sync(get_channel_layer().group_send)('script-feedback', {
                'type': 'chat_message',
                'content': request.data
            })
        except Exception as e:
            raise APIException({'error': 'data could not be procesed', 'detail': str(e)})
        return Response(status=status.HTTP_200_OK)


class RunAPIView(CreateAPIView):
    serializer_class = RunSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def post(self, request, *args, **kwargs):
        serializer = RunSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        bitmex_id = '--id=' + request.data['id']
        secret = '--secret=' + request.data['secret']
        symbol = '--symbol=' + request.data['symbol']
        timeframe = '--timeframe=' + request.data['timeframe']
        _signal = '--signal=' + request.data['signal']
        environment = '--environment=' + settings.ENVIRONMENT

        arguments = [bitmex_id, secret, symbol, timeframe, _signal, environment]

        proc = subprocess.Popen(cmd + arguments, preexec_fn=os.setsid)
        current_executions.append(proc)
        __ = Execution.objects.create(pid=proc.pid)
        return Response({'pid': proc.pid})


class StopAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def post(self, request, *args, **kwargs):
        pid = request.data.get('pid')
        resume = request.data.get('resume', False)

        if pid == 'all':
            for obj in Execution.objects.filter(status=Execution.running):
                try:
                    os.kill(obj.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                finally:
                    obj.status = Execution.killed
                    obj.dt_end = timezone.now()
                    obj.save()
            return Response({'content': 'no content provided when requesting kill all pids'})

        # noinspection PyBroadException
        try:
            if not int(pid):
                raise Exception('invalid pid')
        except Exception:
            return Response(
                {'detail': 'if pid is not "all" you mut provide a valid pid to gather information'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            os.kill(int(pid), signal.SIGKILL)
        except ProcessLookupError:
            pass
        finally:
            execution = Execution.objects.get(pid=pid, status=Execution.running)
            execution.status = Execution.killed
            execution.dt_end = timezone.now()
            execution.save()

        if resume:
            with open(execution_content, 'r') as f:
                content = f.read()
        else:
            content = ''
        print(f'returning content: \n{content}')
        return Response({'content': content})


class ActivesAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = ExecutionSerializer

    def get_queryset(self):
        # get current executions this will also allow to remove zombie process on system
        current_executions[:] = [child for child in current_executions if child.poll() is None]

        # compare current active process on db vs current process on system
        queryset = Execution.objects.filter(status=Execution.running)
        missing_objs = [obj for obj in queryset if obj.pid not in [p.pid for p in current_executions]]

        # mark missing process on db
        for i in missing_objs:
            i.status = Execution.missing
            i.dt_end = timezone.now()
        Execution.objects.bulk_update(missing_objs, ['status', 'dt_end'])

        return Execution.objects.filter(status=Execution.running)
