from datetime import datetime
from django.conf import settings
import re

from django.utils.decorators import method_decorator
from lazysignup.decorators import allow_lazy_user

from customer.models import UserActivity

compiledLists = {}


class LastActivityMiddleware(object):
    @method_decorator(allow_lazy_user)
    def process_request(self, request):
        if not request.user.is_authenticated():
            return
        urlsModule = __import__(settings.ROOT_URLCONF, {}, {}, [''])
        skipList = getattr(urlsModule, 'skip_last_activity_date', None)
        skippedPath = request.path
        if skippedPath.startswith('/'):
            skippedPath = skippedPath[1:]
        if skipList:
            for expression in skipList:
                compiledVersion = None
                if not compiledLists.has_key(expression):
                    compiledLists[expression] = re.compile(expression)
                compiledVersion = compiledLists[expression]
                if compiledVersion.search(skippedPath):
                    return
        activity = None
        try:
            activity = request.user.useractivity
        except:
            activity = UserActivity()
            activity.user = request.user
            activity.last_activity_date = datetime.now()
            activity.last_activity_ip = request.META['REMOTE_ADDR']
            activity.save()
            return
        activity.last_activity_date = datetime.now()
        activity.last_activity_ip = request.META['REMOTE_ADDR']
        activity.save()