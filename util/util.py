import json
import datetime
import time

class MyEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return int(time.mktime(obj.timetuple()))

        return json.JSONEncoder.default(self, obj)


class ContentTypeCheckerMiddleware(object):

    def __init__(self, content_type, app):
        self.app = app
        self.content_type = content_type


    def __call__(self,  env, start):
        if 'HTTP_CONTENT_TYPE' not in env or env['HTTP_CONTENT_TYPE'] != self.content_type:
            s("401 Unauthorized", headers , sys.exc_info())
            return [ json.dumps({ 'code' : 401, 'message' :  "Expecting %s content-type header" % (self.content_type,) }) ]
        else:
            return self.app(e,s)
