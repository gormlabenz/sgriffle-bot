import random
import time
from app.sgriffle import *
from app.models import *
from app.database import *
from app.messenger import *
from app import app
from flask import request


font = 'Ubuntu-Medium.ttf'
font_author = 'Ubuntu-RegularItalic.ttf'
font_size = 64
font_color = (200, 200, 200)
text_place = 'center'
quote_command = 'paste-quotes'


VERIFY_TOKEN = os.getenv('VERIFY_TOKEN')

# We will receive messages that Facebook sends our bot at this endpoint


@app.route("/", methods=['GET', 'POST'])
def receive_message():
    try:
        if request.method == 'GET':
            """Before allowing people to message your bot, Facebook has implemented a verify token
            that confirms all requests that your bot receives came from Facebook."""
            token_sent = request.args.get("hub.verify_token")
            return verify_fb_token(token_sent)
        # if the request was not get, it must be POST and we can just proceed with sending a message back to user
        else:
            # get whatever message a user sent the bot
            output = request.get_json()
            for event in output['entry']:
                messaging = event['messaging']
                print(messaging)
                for message_object in messaging:
                    if message_object.get('message'):
                        # Facebook Messenger ID for user so we know where to send response back to
                        recipient_id = message_object['sender']['id']
                        if message_object['message'].get('text'):
                            message = message_object['message'].get('text')

                            # check for duplicate request and instert do databse
                            request_validation = check_request(
                                recipient_id, message_object.get('timestamp'))

                            if request_validation:
                                print("Duplicate request")
                                return "Duplicate Request"

                            add_user(recipient_id,
                                     message, message_object.get('timestamp'))

                            # Welcomes message
                            send_message(
                                recipient_id, """Hurray, I got a message. One moment, I'm processing. :D""")

                            # check User in database
                            user_validation = check_user(recipient_id)
                            if user_validation:
                                print("Too many requests")
                                send_message(
                                    recipient_id, """Sorry, you requested too much images… 😭  Try it in three days! If you want more images, you can visit https://sgriffle.com/ ☺️""")
                                return "Too many requests"

                            if quote_command in message:
                                # check for avaiable images

                                topic = get_topic(recipient_id)

                                if topic:
                                    path = Path.cwd() / 'pics' / str(recipient_id)
                                    image_paths = path.glob('**/*')
                                    quotes = sg_get_quotes(topic)

                                    if quotes:
                                        # paste quote into images
                                        quotes_image_path = []

                                        for image_path, quote in zip(path.glob('**/*'), quotes):
                                            sg_paste_quote(str(image_path), 'left', quote, font_size,
                                                           font, font_author, font_color)
                                            quotes_image_path.append(
                                                image_path)

                                        # send new images
                                        try:
                                            for image_path in quotes_image_path:
                                                send_image(
                                                    recipient_id, str(image_path))
                                                print('sending quote image')

                                        except Exception as e:
                                            print('Error: {e}')
                                            return "Error"

                                        return "Sended images"

                                    else:
                                        send_message(
                                            recipient_id, """Sorry, I didn't found enough quotes for your topic… :/""")
                                        return "Error"
                                else:
                                    send_message(
                                        recipient_id, """Sorry, I couldn't find any images that you generated. Please start with a new topic. :)""")
                                    return "No avaiable images"

                            # check if message message conaints one word
                            if ' ' in message or len(message) > 100:
                                send_message(
                                    recipient_id, 'Please send one general message, like art, love or human… :)')
                                return "Error"
                            else:
                                image_paths = sg_download_imgages(
                                    message, recipient_id)

                                # check if enough images
                                if image_paths:
                                    sg_images_resize(image_paths, 1080)
                                    # send images
                                    for image_path in image_paths:
                                        send_image(
                                            recipient_id, str(image_path))
                                        print('sended Image')

                                    send_message(
                                        recipient_id, f"""Should I paste suitable quotes on the images? 👩‍💻 Then write: {quote_command}""")

                                    logging.info(msg='sended images')

                                    return "sended images"
                                else:
                                    send_message(
                                        recipient_id, """Sorry, I didn't found enough images for your topic… :(""")
                                    return "not enough images"

                            return "end of process"
                        # if user sends us a GIF, photo,video, or any other non-text item
                        if message_object['message'].get('attachments'):
                            return "non-text item"
        return "Message Processed"
    except:
        return "Error"


@app.route("/test", methods=['GET', 'POST'])
def receive_message_test():
    print(f'Output: {request}')

    if request.method == 'GET':
        """Before allowing people to message your bot, Facebook has implemented a verify token
        that confirms all requests that your bot receives came from Facebook."""
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(token_sent)
    # if the request was not get, it must be POST and we can just proceed with sending a message back to user
    else:
        # get whatever message a user sent the bot
        output = request.get_json()
        for event in output['entry']:
            messaging = event['messaging']
            for message in messaging:
                input_message = message['message']['text']
                recipient_id = message['recipient']['id']

                message_check = check_input_message(
                    recipient_id, input_message)

                if message_check['callback_message']:
                    send_message(
                        recipient_id, message_check['callback_message'])

                if message_check['type'] == 'valid':
                    sg_edit_images(recipient_id, input_message)

                print(message_check, flush=True)
    return "Message Processed"


def verify_fb_token(token_sent):
    # take token sent by facebook and verify it matches the verify token you sent
    # if they match, allow the request, else return an error
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'
