import json
from pymongo import MongoClient
from bson.objectid import ObjectId

from ecommerce.eutil import sanitize

from PyV8 import JSContext

class Validator(object):

    def __init__(self, json, db, collection):
        self.json = json
        self.db = db
        self.ok = False
        self.message = "Unknown"

        schema_doc = self.db["%s_schema" % (collection,) ].find_one({"type" : "schema"})
        if schema_doc is not None:
            self.schema = schema_doc['schema']
            print "Following schema to validate input against!"
            print self.schema
            print type(self.schema)
        else:
            print "No schema to validate!"
            self.ok = True

    def success(self):
        self.ok = True

    def failure(self, message):
        self.ok = False
        self.message = message

    def type_check(self, v, t):
        print "Will check if %s conforms to %s" % (v, t)
        return True;
        #if t == "string(...)": and so on.....
 
    def valid(self, rv):

        if self.ok: return self.ok

        try:
            schema  = json.loads(self.schema)
         
            self.ok = True
 
            for k,v in self.json.items():
                if k in schema:
                    t = schema[k]
                    if not self.type_check(v, t):
                        self.message += "; field %s does not confirm to type %s: Given %s" % (k, t, v)
                        self.ok = False

        except Exception, e:
            print e
            self.ok = False
            self.message = e

        print " ***** Validator Execution complete"

        if not self.ok: rv['message'] = self.message
        return self.ok

    def log(self,msg):
        print msg
