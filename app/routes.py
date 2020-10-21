from app.messenger import *
from app.sgriffle import sg_edit_images
from app import app
from flask import request
import pprint


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
            for message_data in messaging:
                timestamp = message_data['timestamp']

                # return if no text message is send
                pprint.pprint(message_data)
                if 'message' in message_data:
                    input_message = message_data['message']['text']
                    recipient_id = message_data['sender']['id']
                elif 'postback' in message_data:
                    input_message = message_data['postback']['payload']
                    recipient_id = message_data['sender']['id']
                elif 'policy_enforcement' in message_data:
                    action = message_data['policy_enforcement']['action']
                    reason = message_data['policy_enforcement']['reason']
                    insert_policy(action, reason, timestamp)
                    return "Policy"
                else:
                    return "No valid message"

                message_check = check_input_message(
                    recipient_id, input_message, timestamp)

                if message_check['type'] != 'invalide':
                    insert_user(recipient_id, input_message,
                                timestamp)

                if message_check['type'] == 'edit_images':
                    sg_edit_images(recipient_id, input_message)
                    # print(bot.send_button_message(recipient_id, 'What to do next?', [{
                    #    "type": "postback",
                    #    "payload": f"""{os.getenv('MESSAGE_COMMAND')}quote""",
                    #    "title": "Custom Quote"
                    # },
                    #    {
                    #    "type": "postback",
                    #    "payload": f"""{os.getenv('MESSAGE_COMMAND')}background""",
                    #    "title": "Background"
                    # },
                    #    {
                    #    "type": "postback",
                    #    "payload": f"""{os.getenv('MESSAGE_COMMAND')}align""",
                    #    "title": "Align Text"
                    # }
                    # ]))

                if message_check['callback_message']:
                    send_message(
                        recipient_id, message_check['callback_message'])

    return "Message Processed"


def verify_fb_token(token_sent):
    # take token sent by facebook and verify it matches the verify token you sent
    # if they match, allow the request, else return an error
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'
