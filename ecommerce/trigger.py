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

        trigger = db["%s_triggers" % (collection,) ].find_one({"type" : "beforePOST"})
        if trigger is not None:
            self.trigger_code = str(trigger['code'])
            self.trigger_code = "{   var threshold = 10;   function getQuantity(link) {       return link['quantity'];   }   function getTotalQuantity(links) {       var total_quantity = 0;       for (var i = 0; i < links.length; i++) {           total_quantity += getQuantity(links[i]);       }       return total_quantity;   }   function acceptable(qty) {       return qty <= threshold;   }   req = JSON.parse(new_json());   links = req['promotion']['links'];   total_quantity = getTotalQuantity(links);   if (acceptable(total_quantity)) {       success();   } else {       failure(\"You cannot exceed 10, you have \" + total_quantity);  }   }"
            self.trigger_code = "{   var threshold = 10; function getQuantity(link) {       return link['quantity'];   } function getTotalQuantity(links) {       var total_quantity = 0;       for (var i = 0; i < links.length; i++) {           total_quantity += getQuantity(links[i]);       }       return total_quantity;   }   function acceptable(qty) {       return qty <= threshold;   }  var x = new_json(); log(x); var req = JSON.parse(x); success();  }"
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
            objects = db[c]
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
