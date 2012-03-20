import sys
import cProfile
import pstats
from cStringIO import StringIO
from django.conf import settings

class ProfileDumpMiddleware(object):
    def process_view(self, request, callback, callback_args, callback_kwargs):
        if settings.DEBUG and 'debugprofile' in request.GET:
            self.profiler = cProfile.Profile()
            args = (request,) + callback_args
            return self.profiler.runcall(callback, *args, **callback_kwargs)

    def process_response(self, request, response):
        if settings.DEBUG and 'debugprofile' in request.GET:
            self.profiler.create_stats()
            out = StringIO()
            stats = pstats.Stats(self.profiler, stream=out)
            # Values for stats.sort_stats():
            # - calls call count
            # - cumulative cumulative time
            # - file file name
            # - module file name
            # - pcalls primitive call count
            # - line line number
            # - name function name
            # - nfl name/file/line
            # - stdname standard name
            # - time internal time
            stats.sort_stats('time').print_stats(.2)
            response.content = out.getvalue()
            response['Content-type'] = 'text/plain'
        return response
