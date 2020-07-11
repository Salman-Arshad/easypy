import os
from datetime import datetime

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rest_framework.generics import CreateAPIView

from django.views import View
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse, HttpResponsePermanentRedirect

from .tree import get_tree, get_csv
from .serializers import HookNotificationSerializer
from .actions import run_code, read_plain_file, write_plain_file
from .storage import tmp_storage, this_storage, root_location, ContentFile
from .templatetags.custom_templatetags import directory, simple_file


class IndexView(View):
    # noinspection PyUnusedLocal
    @staticmethod
    def get(request, *args, **kwargs):
        return render(request, 'fm/index.html', {'tree': get_tree()})

    # noinspection PyUnusedLocal
    @staticmethod
    def post(request, *args, **kwargs):
        print(request.POST)
        response = ''
        if request.POST.get('operation', '') == 'run':
            file = tmp_storage.save('tmp_execute.py', ContentFile(request.POST.get('content', '')))
            response = run_code(file)
            tmp_storage.delete(file)
            return JsonResponse({'stdout': response})
        elif request.POST.get('operation', '') == 'save':
            file = request.POST.get('file', '')
            if not file:
                return JsonResponse({'description': 'no file was provided', 'content': ''}, status=400)
            return write_plain_file(this_storage, file, ContentFile(request.POST.get('content', '')))
        return JsonResponse({'description': 'no operation was provided', 'content': ''}, status=400)

class SocketIndexView(View):
    # noinspection PyUnusedLocal
    @staticmethod
    def get(request, *args, **kwargs):
        return render(request, 'fm/index2.html', {'tree': get_tree(), 'csv':get_csv()})


class ContentView(View):
    # noinspection PyUnusedLocal
    @staticmethod
    def post(request, *args, **kwargs):
        file = ''
        # noinspection PyBroadException
        try:
            file = request.POST.get('file', '')
            if not file:
                return JsonResponse({'description': 'no file was provided', 'content': ''}, status=400)
            return read_plain_file(this_storage, file)
        except Exception as e:
            return JsonResponse({'description': 'can not read this file', 'content': ''}, status=500)


class RMView(View):
    # noinspection PyUnusedLocal
    @staticmethod
    def post(request, *args, **kwargs):
        try:
            file = request.POST.get('file', '')
            if not file:
                return JsonResponse({'description': 'no file was provided', 'content': ''}, status=400)
            this_storage.delete(file)
            return JsonResponse({'description': 'ok', 'content': ''})
        except Exception as e:
            if 'Directory not empty' in str(e):
                return JsonResponse(
                    {'description': 'can not delete directory cause is not empty', 'content': ''},
                    status=400
                )
            return JsonResponse(
                {'description': '%s unhandled exception %s' % (e.__class__.__name__, str(e)), 'content': ''},
                status=500
            )


class UploadView(View):
    # noinspection PyUnusedLocal
    @staticmethod
    def post(request, *args, **kwargs):
        upload_location = request.POST.get('upload_location', '')
        for file in request.FILES.getlist('files'):
            this_storage.save(os.path.join(upload_location, file.name), file)
        return HttpResponsePermanentRedirect(reverse_lazy('fm:index'))


class CreateFileView(View):
    # noinspection PyUnusedLocal
    @staticmethod
    def post(request, *args, **kwargs):
        f_type, parent, name = request.POST.get('type'), request.POST.get('parent'), request.POST.get('name')
        if f_type not in ('dir', 'file', 'rename') or not parent or not name:
            return JsonResponse({'description': 'information provided is not ok', 'content': ''}, status=400)

        try:
            name = name.replace('/', '')
            abs_path = os.path.join(parent, name)
            file_info = {'name': name, 'abs_path': abs_path, 'html_children': ''}

            if f_type == 'dir':
                os.makedirs(os.path.join(root_location, abs_path))
                return JsonResponse({'description': 'ok', 'content': directory % file_info})
            if f_type == 'file':
                this_storage.save(abs_path, ContentFile(''))
                return JsonResponse({'description': 'ok', 'content': simple_file % file_info})
            if f_type == 'rename':
                src = os.path.join(root_location, parent)
                dir_name, __ = os.path.split(parent)
                dst = os.path.join(root_location, dir_name, name)
                os.rename(src, dst)
                return JsonResponse(
                    {'description': 'ok', 'content': {'name': name, 'abs_path': os.path.join(dir_name, name)}}
                )
        except Exception as e:
            return JsonResponse(
                {'description': '%s unhandled exception %s' % (e.__class__.__name__, str(e)), 'content': ''},
                status=500
            )


# this is a test view not the main one
class WebHook(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    # noinspection PyMethodMayBeStatic,SpellCheckingInspection,PyUnusedLocal
    def post(self, request, *args, **kwargs):
        with open('webhook.log', 'a') as f:
            data = f'--BEGIN REQUEST {datetime.now()}--\n{request}\n{request.body}\n--END REQUEST--\n'
            f.write(data)
        return JsonResponse({})


class WebHookAPIView(CreateAPIView):
    serializer_class = HookNotificationSerializer

    def perform_create(self, serializer):
        serializer.save()
        try:
            async_to_sync(get_channel_layer().group_send)(
                'TradingView',
                {'type': 'chat_message', 'content': serializer.data}
            )
        except Exception as e:
            # noinspection SpellCheckingInspection
            print(f'Error {e} when send payload to webhook')
