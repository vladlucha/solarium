import re
import json
import logging
from channels import Group
from channels.auth import channel_session_user, channel_session_user_from_http
from channels.handler import AsgiHandler
from channels.sessions import channel_session
from django.core import serializers
from django.http import HttpResponse

from chat.models import Message
from customer.models import Customer
from salarium.utils import parse_int


def http_consumer(message):
    # Make standard HTTP response - access ASGI path attribute directly
    response = HttpResponse("Hello world! You asked for %s" % message.content['path'])
    # Encode that response into message format (ASGI)
    for chunk in AsgiHandler.encode_response(response):
        message.reply_channel.send(chunk)


@channel_session_user_from_http
def ws_connect(message):
    prefix, _, author_pk, _, recipient_pk = message['path'].strip('/').split('/')
    message.reply_channel.send({"accept": True})
    chat_pk = recipient_pk if type(parse_int(recipient_pk)) == int else author_pk
    Group('chat-' + chat_pk).add(message.reply_channel)
    message.channel_session['chat_pk'] = chat_pk
    message.channel_session['author'] = author_pk
    if type(parse_int(recipient_pk)) == int:
        message.channel_session['recipient'] = recipient_pk


@channel_session_user
def ws_receive(message):
    recipient = None
    author = Customer.objects.get(pk=message.channel_session.get('author', None))

    if 'recipient' in message.channel_session:
        recipient = Customer.objects.get(pk=message.channel_session.get('recipient', None))

    data = json.loads(message['text'])

    if data and author:
        data['author'] = author
        data['recipient'] = recipient
        m = Message.objects.create(**data)
        m.save()

        data = {
            'thumbnail': author.thumbnail.get_high_res_src if author.thumbnail else '',
            'author_pk': author.pk,
            'username': author.username,
            'date': m.timestamp.strftime('%Y.%m.%d %H:%M:%S'),
            'message': m.message
        }

        # See above for the note about Group
        Group('chat-' + message.channel_session['chat_pk']).send({
            'text': json.dumps(data)
        })


@channel_session
def ws_disconnect(message):
    Group('chat-' + message.channel_session['chat_pk'], channel_layer=message.channel_layer).discard(message.reply_channel)
