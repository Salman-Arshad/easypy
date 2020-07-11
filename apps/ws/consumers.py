from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer


class OnlyBroadcastConsumer(JsonWebsocketConsumer):
    # Receive message from WebSocket
    def receive(self, text_data=None, bytes_data=None, **kwargs):
        # we expect no info from client, this is just a broadcast type socket
        self.base_send({"type": "websocket.close", "code": 1007})


# noinspection SpellCheckingInspection
class TradingViewConsumer(OnlyBroadcastConsumer):

    # noinspection PyAttributeOutsideInit
    def connect(self):
        try:
            # always accept otherwise we would not be able to gracefully close socket
            self.accept()
            # if not self.scope['user'].is_authenticated:
            #    self.base_send({"type": "websocket.close", "code": 4003})

            # create as array because self.websocket_disconnect expects an iterable
            self.groups = ['TradingView']

            # Join room group
            async_to_sync(self.channel_layer.group_add)(
                self.groups[0],
                self.channel_name
            )
        except Exception as e:
            print(e)
            raise

    # Receive message from group
    def chat_message(self, event):
        try:
            # Send message to WebSocket
            self.send_json({'content': event['content']})
        except Exception as e:
            print(e)
            raise


class PIDConsumer(OnlyBroadcastConsumer):

    # noinspection PyAttributeOutsideInit
    def connect(self):
        try:
            # always accept otherwise we would not be able to gracefully close socket
            self.accept()
            # if not self.scope['user'].is_authenticated:
            #    self.base_send({"type": "websocket.close", "code": 4003})

            # create as array because self.websocket_disconnect expects an iterable
            self.groups = ['script-feedback']

            # Join room group
            async_to_sync(self.channel_layer.group_add)(
                str(self.groups[0]),
                self.channel_name
            )
        except Exception as e:
            print(e)
            raise

    # Receive message from group
    def chat_message(self, payload):
        try:
            # Send message to WebSocket
            self.send_json(payload['content'])
        except Exception as e:
            print(e)
            raise
