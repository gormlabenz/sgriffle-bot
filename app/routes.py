from app.messenger import *
from app import app
from flask import request

VERIFY_TOKEN = os.getenv('VERIFY_TOKEN')

# We will receive messages that Facebook sends our bot at this endpoint


@app.route("/", methods=['GET', 'POST'])
def receive_message_test():

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

                if message_check['type'] != 'invalide':
                    insert_user(recipient_id, input_message,
                                message['timestamp'])

                if message_check['callback_message']:
                    send_message(
                        recipient_id, message_check['callback_message'])

                if message_check['type'] == 'valide':
                    sg_edit_images(recipient_id, input_message)

    return "Message Processed"


def verify_fb_token(token_sent):
    # take token sent by facebook and verify it matches the verify token you sent
    # if they match, allow the request, else return an error
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'
