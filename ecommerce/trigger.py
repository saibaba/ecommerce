from PyV8 import JSClass
from urlparse import urlparse

from pymongo import MongoClient
from bson.objectid import ObjectId

from ecommerce.eutil import sanitize

from PyV8 import JSContext

# http://andrewwilkinson.wordpress.com/2012/01/23/integrating-python-and-javascript-with-pyv8/

class JS(JSContext):
    def __enter__(self):
        super(JS, self).enter()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        super(JS, self).leave()

class BeforePOST(JSClass):

    def __init__(self, json, db, collection):
        self.json = json
        self.db = db
        self.ok = False
        self.message = "Unknown"

        trigger = self.db["%s_triggers" % (collection,) ].find_one({"type" : "beforePOST"})
        if trigger is not None:
            self.trigger_code = str(trigger['code'])
            print "Following trigger code to execute!"
            print self.trigger_code
            print type(self.trigger_code)

        else:
            print "No trigger code to execute!"
            self.ok = True

    def new_json(self):
        return self.json

    def success(self):
        self.ok = True

    def failure(self, message):
        self.ok = False
        self.message = message

    def get(self, link):
        #/ecommerce/promotions/<id>

        o = urlparse(link)
        p = o.path.split("/") 
        c = p[-2]
        id = p[-1]
        try:
            objects = self.db[c]
            obj_id = ObjectId(id)
            obj = objects.find_one({"_id":obj_id})

            if obj is None:
                return None
            else:
                return sanitize(obj)
        except Exception, e:
            print e
            return None

    def execute(self):

        if self.ok: return 

        glob = self

        try:
            with JS(glob) as ctxt:
                ctxt.eval(self.trigger_code)

        except Exception, e:
            print e
            self.ok = False
            self.message = e

        print " ***** Execution complete"
    def log(self,msg):
        print msg
