import json
import os

import requests
from requests_toolbelt import MultipartEncoder
from enum import Enum

from pymessenger.graph_api import FacebookGraphApi
import pymessenger.utils as utils

class NotificationType(Enum):
    regular = "REGULAR"
    silent_push = "SILENT_PUSH"
    no_push = "NO_PUSH"

class Bot(FacebookGraphApi):

    def __init__(self, *args, **kwargs):
        super(Bot, self).__init__(*args, **kwargs)

    def send_text_message(self, recipient_id, message):
        '''Send text messages to the specified recipient.
        https://developers.facebook.com/docs/messenger-platform/send-api-reference/text-message
        Input:
            recipient_id: recipient id to send to
            message: message to send
        Output:
            Response from API as <dict>
        '''
        payload = {
            'recipient': {
                'id': recipient_id
            },
            'message': {
                'text': message
            }
        }
        return self.send_raw(payload)

    def send_message(self, recipient_id, message):
        '''Send text messages to the specified recipient.
        https://developers.facebook.com/docs/messenger-platform/send-api-reference/text-message
        Input:
            recipient_id: recipient id to send to
            message: raw message to send
        Output:
            Response from API as <dict>
        '''
        payload = {
            'recipient': {
                'id': recipient_id
            },
            'message': message
        }
        return self.send_raw(payload)

    def send_generic_message(self, recipient_id, elements):
        '''Send generic messages to the specified recipient.
        https://developers.facebook.com/docs/messenger-platform/send-api-reference/generic-template
        Input:
            recipient_id: recipient id to send to
            elements: generic message elements to send
        Output:
            Response from API as <dict>
        '''
        payload = {
            'recipient': {
                'id': recipient_id
            },
            'message': {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "generic",
                        "elements": elements
                    }
                }
            }
        }
        return self.send_raw(payload)

    def send_button_message(self, recipient_id, text, buttons):
        '''Send text messages to the specified recipient.
        https://developers.facebook.com/docs/messenger-platform/send-api-reference/button-template
        Input:
            recipient_id: recipient id to send to
            text: text of message to send
            buttons: buttons to send
        Output:
            Response from API as <dict>
        '''

        payload = {
            'recipient': {
                'id': recipient_id
            },
            'message': {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "button",
                        "text": text,
                        "buttons": buttons
                    }
                }
            }
        }
        return self.send_raw(payload)


    def send_image(self,
                   recipient_id,
                   image_path,
                   notification_type=NotificationType.regular):
        """Send an image to the specified recipient.
        Image must be PNG or JPEG or GIF (more might be supported).
        https://developers.facebook.com/docs/messenger-platform/send-api-reference/image-attachment
        Input:
            recipient_id: recipient id to send to
            image_path: path to image to be sent
        Output:
            Response from API as <dict>
        """
        return self.send_attachment(recipient_id, "image", image_path,
                                    notification_type)

    """ def send_image(self, recipient_id, image_path):
        '''Send an image to the specified recipient.
        Image must be PNG or JPEG or GIF (more might be supported).
        https://developers.facebook.com/docs/messenger-platform/send-api-reference/image-attachment
        Input:
            recipient_id: recipient id to send to
            image_path: path to image to be sent
        Output:
            Response from API as <dict>
        '''
        payload = {
            'recipient': json.dumps(
                {
                    'id': recipient_id
                }
            ),
            'message': json.dumps(
                {
                    'attachment': {
                        'type': 'image',
                        'payload': {}
                    }
                }
            ),
            'filedata': (image_path, open(image_path, 'rb'))
        }
        multipart_data = MultipartEncoder(payload)
        multipart_header = {
            'Content-Type': multipart_data.content_type
        }
        return requests.post(self.base_url, data=multipart_data, headers=multipart_header).json() """

    def send_image_url(self, recipient_id, image_url):
        '''Send an image to specified recipient using URL.
        Image must be PNG or JPEG or GIF (more might be supported).
        https://developers.facebook.com/docs/messenger-platform/send-api-reference/image-attachment
        Input:
            recipient_id: recipient id to send to
            image_url: url of image to be sent
        Output:
            Response from API as <dict>
        '''
        payload = {
            'recipient': json.dumps(
                {
                    'id': recipient_id
                }
            ),
            'message': json.dumps(
                {
                    'attachment': {
                        'type': 'image',
                        'payload': {
                            'url': image_url
                        }
                    }
                }
            )
        }
        return self.send_raw(payload)

    def send_action(self, recipient_id, action):
        '''Send typing indicators or send read receipts to the specified recipient.
        Image must be PNG or JPEG.
        https://developers.facebook.com/docs/messenger-platform/send-api-reference/sender-actions

        Input:
            recipient_id: recipient id to send to
            action: action type (mark_seen, typing_on, typing_off)
        Output:
            Response from API as <dict>
        '''
        payload = {
            'recipient': {
                'id': recipient_id
            },
            'sender_action': action
        }
        return self.send_raw(payload)
        
    def _send_payload(self, payload):
        ''' Deprecated, use send_raw instead '''
        return self.send_raw(payload)
        
    def send_raw(self, payload):
        request_endpoint = '{0}/me/messages'.format(self.graph_url)
        response = requests.post(
            request_endpoint,
            params=self.auth_args,
            json=payload
        )
        result = response.json()
        return result

    def send_audio(self, recipient_id, audio_path):
        '''Send audio to the specified recipient.
        Audio must be MP3 or WAV
        https://developers.facebook.com/docs/messenger-platform/send-api-reference/audio-attachment
        Input:
            recipient_id: recipient id to send to
            audio_path: path to audio to be sent
        Output:
            Response from API as <dict>
        '''
        payload = {
            'recipient': json.dumps(
                {
                    'id': recipient_id
                }
            ),
            'message': json.dumps(
                {
                    'attachment': {
                        'type': 'audio',
                        'payload': {}
                    }
                }
            ),
            'filedata': (audio_path, open(image_path, 'rb'))
        }
        multipart_data = MultipartEncoder(payload)
        multipart_header = {
            'Content-Type': multipart_data.content_type
        }
        return requests.post(self.base_url, data=multipart_data, headers=multipart_header).json()

    def send_audio_url(self, recipient_id, audio_url):
        '''Send audio to specified recipient using URL.
        Audio must be MP3 or WAV
        https://developers.facebook.com/docs/messenger-platform/send-api-reference/audio-attachment
        Input:
            recipient_id: recipient id to send to
            audio_url: url of audio to be sent
        Output:
            Response from API as <dict>
        '''
        payload = {
            'recipient': json.dumps(
                {
                    'id': recipient_id
                }
            ),
            'message': json.dumps(
                {
                    'attachment': {
                        'type': 'audio',
                        'payload': {
                            'url': audio_url
                        }
                    }
                }
            )
        }
        return self.send_raw(payload)

    def send_video(self, recipient_id, video_path):
        '''Send video to the specified recipient.
        Video should be MP4 or MOV, but supports more (https://www.facebook.com/help/218673814818907).
        https://developers.facebook.com/docs/messenger-platform/send-api-reference/video-attachment
        Input:
            recipient_id: recipient id to send to
            video_path: path to video to be sent
        Output:
            Response from API as <dict>
        '''
        payload = {
            'recipient': json.dumps(
                {
                    'id': recipient_id
                }
            ),
            'message': json.dumps(
                {
                    'attachment': {
                        'type': 'audio',
                        'payload': {}
                    }
                }
            ),
            'filedata': (video_path, open(image_path, 'rb'))
        }
        multipart_data = MultipartEncoder(payload)
        multipart_header = {
            'Content-Type': multipart_data.content_type
        }
        return requests.post(self.base_url, data=multipart_data, headers=multipart_header).json()

    def send_video_url(self, recipient_id, video_url):
        '''Send video to specified recipient using URL.
        Video should be MP4 or MOV, but supports more (https://www.facebook.com/help/218673814818907).
        https://developers.facebook.com/docs/messenger-platform/send-api-reference/video-attachment 
        Input:
            recipient_id: recipient id to send to
            video_url: url of video to be sent
        Output:
            Response from API as <dict>
        '''
        payload = {
            'recipient': json.dumps(
                {
                    'id': recipient_id
                }
            ),
            'message': json.dumps(
                {
                    'attachment': {
                        'type': 'audio',
                        'payload': {
                            'url': video_url
                        }
                    }
                }
            )
        }
        return self.send_raw(payload)


    def send_file(self, recipient_id, file_path):
        '''Send file to the specified recipient.
        https://developers.facebook.com/docs/messenger-platform/send-api-reference/file-attachment
        Input:
            recipient_id: recipient id to send to
            file_path: path to file to be sent
        Output:
            Response from API as <dict>
        '''
        payload = {
            'recipient': json.dumps(
                {
                    'id': recipient_id
                }
            ),
            'message': json.dumps(
                {
                    'attachment': {
                        'type': 'file',
                        'payload': {}
                    }
                }
            ),
            'filedata': (file_path, open(image_path, 'rb'))
        }
        multipart_data = MultipartEncoder(payload)
        multipart_header = {
            'Content-Type': multipart_data.content_type
        }
        return requests.post(self.base_url, data=multipart_data, headers=multipart_header).json()

    def send_file_url(self, recipient_id, file_url):
        '''Send file to the specified recipient.
        https://developers.facebook.com/docs/messenger-platform/send-api-reference/file-attachment
        Input:
            recipient_id: recipient id to send to
            file_url: url of file to be sent
        Output:
            Response from API as <dict>
        '''
        payload = {
            'recipient': json.dumps(
                {
                    'id': recipient_id
                }
            ),
            'message': json.dumps(
                {
                    'attachment': {
                        'type': 'file',
                        'payload': {
                            'url': file_url
                        }
                    }
                }
            )
        }
        return self.send_raw(payload)

    def send_attachment(self,
                        recipient_id,
                        attachment_type,
                        attachment_path,
                        notification_type=NotificationType.regular):
        """Send an attachment to the specified recipient using local path.
        Input:
            recipient_id: recipient id to send to
            attachment_type: type of attachment (image, video, audio, file)
            attachment_path: Path of attachment
        Output:
            Response from API as <dict>
        """
        with open(attachment_path, 'rb') as f:
            attachment_filename = os.path.basename(attachment_path)
            if attachment_type != 'file':
                attachment_ext = attachment_filename.split('.')[1]
                content_type = attachment_type + '/' + attachment_ext # eg: audio/mp3
            else:
                content_type = ''
            payload = {
                'recipient': json.dumps({
                    'id': recipient_id
                }),
                'notification_type': notification_type.value,
                'message': json.dumps({
                    'attachment': {
                        'type': attachment_type,
                        'payload': {}
                    }
                }),
                'filedata':
                (attachment_filename, f, content_type)
            }
            multipart_data = MultipartEncoder(payload)
            multipart_header = {'Content-Type': multipart_data.content_type}
            request_endpoint = '{0}/me/messages'.format(self.graph_url)
            return requests.post(
                request_endpoint,
                data=multipart_data,
                params=self.auth_args,
                headers=multipart_header).json()