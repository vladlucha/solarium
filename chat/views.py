from django.shortcuts import render


def chat_room(request, label):
    # We want to show the last 50 messages, ordered most-recent-last
    sent_messages = reversed(request.user.sent_messages.order_by('-timestamp'))
    received_messages = reversed(request.user.received_messages.order_by('-timestamp'))

    return render(request, "chat/room.html", {'sent_messages': sent_messages, 'received_messages': received_messages})
