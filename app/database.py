from app import db
from app.models import *
import time
import os


def insert_user(recipient_id, input_message, timestamp):

    user = User(id=recipient_id,
                topic=input_message, timestamp=timestamp)
    db.session.add(user)
    db.session.commit()


def check_request(recipient_id, timestamp):
    query = User.query.filter_by(id=recipient_id, timestamp=timestamp).all()
    if query:
        return True


def check_user(recipient_id):
    user_requests = User.query.filter_by(
        id=recipient_id).all()
    if user_requests:
        new_requests = []
        for user_request in user_requests:
            if time.time() - user_request.timestamp < int(os.getenv('TIME_TILL_RESET')):
                new_requests.append(user_request)
        if len(new_requests) > int(os.getenv('MAX_REQUESTS')):
            return True
    return False


def get_topic(recipient_id):
    user_requests = User.query.filter_by(
        id=recipient_id).order_by(User.time.desc()).all()
    for user_request in user_requests:
        topic = user_request.topic
        print(f'Topic: {topic}')
        if 'paste-quotes' not in topic:
            return topic
