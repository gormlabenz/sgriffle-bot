from app.database import *
from app.sgriffle import *
from app import app, bot
import os
import pprint


def send_message(recipient_id, response):
    # sends user the text message provided via input response parameter
    if response:
        pprint.pprint(bot.send_text_message(recipient_id, response))
    return "success"


def send_image(recipient_id, image_path):
    # sends user the text message provided via input response parameter
    with app.app_context():
        bot.send_image(
            recipient_id, str(image_path))
    return "success"


def check_input_message(recipient_id, input_message, timestamp):
    """Returns the response message and the type of the input message in a dict
        eg. {'type': 'invalide', 
            'callback_message': 
            'Hey, if you want to use Sgriffle to generate images, please send me a one general topic, like art, love or human… :)'}

        If the callback_message is none, a function  should be used to generate images

        :param input_message:
            Must be a string, is the message send to the bot.
        """

    type = 'invalide'
    callback_message = 'Hey, please send me a one general topic, like art, love or human… :)'

    if ' ' not in input_message or len(input_message) > 100:

        type = 'edit_images'
        callback_message = f"""Here are the images I generated for you :)"""

    if check_timestamp(recipient_id):

        type = 'expired'
        callback_message = """Sorry, you requested too much images… 😭  Try it in three days! If you want more images, you can visit https://sgriffle.com/ ☺️"""

    if os.getenv('MESSAGE_COMMAND') in input_message:

        type = 'command'
        callback_message = None

        if "welcome" in input_message:
            type = 'welcome command'
            callback_message = 'Hey, please send me a one general topic, like art, love or human… :)'

    if check_request(recipient_id, timestamp):
        type = 'invalide'
        callback_message = None

    return {'type': type, 'callback_message': callback_message}
