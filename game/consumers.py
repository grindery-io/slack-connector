import json
import logging
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from .request_prefix import REQUEST_PREFIX


class SocketAdapter(AsyncJsonWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.background_tasks = set()
        self.connected = False

    async def connect(self):
        self.connected = True
        await self.accept()

    async def disconnect(self, close_code):
        self.connected = False
        print('-----socket disconnected-----')

    async def receive(self, text_data=None, bytes_data=None, **kwargs):
        request = json.loads(text_data)
        method = request.get("method", None)
        if method == 'ping':
            response = {
                'jsonrpc': '2.0',
                'result': {},
                'id': id
            }
            await self.send_json(response)
            return

        params = request.get("params", None)
        id = request.get("id", None)
        key = ''
        fields = ''
        session_id = ''
        access_token = ''
        channel_id = ''
        message = ''

        if params:
            if 'key' in params:
                key = params['key']
            if 'sessionId' in params:
                session_id = params['sessionId']
            if 'fields' in params:
                fields = params['fields']
                if 'channel_id' in fields:
                    channel_id = fields['channel_id']
                if 'message' in fields:
                    message = str(fields['message'])
            access_token = params['authentication']

        if method == 'runAction':
            error_message = ''
            client = WebClient(token=access_token, base_url=REQUEST_PREFIX + 'www.slack.com/api/')
            logger = logging.getLogger(__name__)

            try:
                client.conversations_join(
                    channel=channel_id
                )
                result = client.chat_postMessage(
                    channel=channel_id,
                    text=message
                )
                if result["ok"]:
                    success = True
                else:
                    success = False
                    error_message = result["error"]
            except SlackApiError as e:
                success = False
                error_message = 'invalid request'
            if success:
                run_action_response = {
                    'jsonrpc': '2.0',
                    'result': {
                        'key': key,
                        'sessionId': session_id,
                        'payload': fields
                    },
                    'id': id
                }
            else:
                run_action_response = {
                    'jsonrpc': '2.0',
                    'error': {
                        'code': 1,
                        'message': error_message
                    },
                    'id': id
                }
            await self.send_json(run_action_response)
