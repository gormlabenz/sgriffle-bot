from app import db
from app.models import *
import time


def add_user(recipient_id, message, tim):
    user = User(id=recipient_id,
                topic=message, time=tim)
    db.session.add(user)
    db.session.commit()


def check_request(recipient_id, time):
    query = User.query.filter_by(id=recipient_id, time=time).all()
    if query:
        return True


def check_user(recipient_id):
    user_requests = User.query.filter_by(
        id=recipient_id).all()
    if user_requests:
        new_requests = []
        for user_request in user_requests:
            if time.time() - user_request.time < 259200:
                new_requests.append(user_request)
        if len(new_requests) > 8:
            return True


def get_topic(recipient_id):
    user_requests = User.query.filter_by(
        id=recipient_id).order_by(User.time.desc()).all()
    for user_request in user_requests:
        topic = user_request.topic
        print(f'Topic: {topic}')
        if 'paste-quotes' not in topic:
            return topic
