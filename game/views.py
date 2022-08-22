import json
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from .serializers import ConnectorSerializer
from common.serializers import serialize_channel


class FetchChannelList(GenericAPIView):
    serializer_class = ConnectorSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        params = serializer.data.get('params')
        method = serializer.data.get('method')
        request_id = serializer.data.get('id')
        key = params['key']
        access_token = params['credentials']['access_token']

        client = WebClient(token=access_token)
        error_message = ''
        channels = []
        cursor = 'initial value'
        success = True

        try:
            while cursor:
                if cursor == 'initial value':
                    result = client.conversations_list(
                        limit=1000
                    )
                else:
                    result = client.conversations_list(
                        limit=1000,
                        cursor=cursor
                    )
                if result["ok"]:
                    success = True
                    for channel in result["channels"]:
                        channels.append({
                            **serialize_channel(channel)
                        })
                    if result["response_metadata"]["next_cursor"]:
                        cursor = result["response_metadata"]["next_cursor"]
                    else:
                        cursor = None
                else:
                    success = False
                    cursor = None
                    error_message = result["error"]
        except SlackApiError as e:
            success = False
            error_message = 'invalid request'

        if success:
            return Response(
                {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "inputFields": [
                            {
                                "key": "channel_id",
                                "label": "Channel",
                                "helpText": "",
                                "type": "string",
                                "required": True,
                                "placeholder": "Pick a channel...",
                                "choices": channels
                            },
                            {
                                "key": "message",
                                "label": "Message Text",
                                "helpText": "",
                                "type": "string",
                                "required": True,
                                "placeholder": "Enter text"
                            }
                        ]
                    }
                },
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    'error': {
                        'code': 1,
                        'message': error_message
                    }
                },
                status=status.HTTP_201_CREATED
            )
