from bottle import Bottle, run, template, install, request,response, route
from util.config import config

import time
import parser

import json

import sys
import traceback
import logging

from pymongo import MongoClient
from bson.objectid import ObjectId

import datetime
from ecommerce.eutil import *

from trigger import BeforePOST

app = Bottle()

client = MongoClient(config.get('objectstore', 'mongo_host'), int(config.get('objectstore', 'mongo_port')))
db = client.ecommerce

@app.route('/ecommerce/<name>/<id>', 'PATCH')
def update(name, id):

    print "*** id = %s" % (id,)

    rv = { 'code' : 400, 'message': 'Unknown Error', 'link' : "%s/ecommerce/%s/%s" % (config.get("app", "prefix"), name, id) }

    try:
        req_json = request.json
        if req_json is None:
            raise Exception("Empty json or no proper content-type to recognize as json")
    except Exception, e:
        rv['message'] = 'Could not parse json'
        response.status = rv['code']
        return rv

    try:
    
        objects = db[name]
        obj_id = ObjectId(id)
        obj = objects.find_one({"_id":obj_id})

        if obj is None:
            rv['code'] = 404
            rv['message'] = 'not found'
        else:
            for k in req_json.keys():
                obj[k] = req_json[k]

            print obj
            del obj["_id"]

            obj["lastUpdateDate"] = datetime.datetime.utcnow()
            obj["self"] = "%s/ecommerce/%s/%s" % (config.get("app", "prefix"), name, id)
            x = objects.update({'_id':obj_id}, {"$set": obj}, upsert=False)
            print "Update result:", 
            print x
            rv['code'] = 200
            rv['message'] = 'Updated'

    except Exception, e:
        print e
        rv['code'] = 400

    response.status = rv['code']
    response.location = rv['link']
    return rv

@app.post('/ecommerce/<name>/')
def create(name):

    try:
        req_json = request.json
        req_raw = request.body.getvalue()
        if req_json is None:
            raise Exception("Empty json or no proper content-type to recognize as json")
    except Exception, e:
        response.status = 400
        status = "syntaxError"
        return {'code': 400, 'message' : 'Could not parse json' }

    try:
        objects = db[name]

        # if there is a trigger, fire it
        print "Invoking trigger"
        trigger = BeforePOST(req_raw, db, name)
        trigger.execute()
        if not trigger.ok:
            raise Exception(trigger.message)
        req_json["creationDate"] = datetime.datetime.utcnow()

        obj_id = objects.insert(req_json)
        obj = objects.find_one({"_id":obj_id})
        obj["self"] = "%s/ecommerce/%s/%s" % (config.get("app", "prefix"), name, str(obj_id))
        x = objects.update({'_id':obj_id}, obj, upsert=False)
        response.status = 201
        response.location = '/ecommerce/%s/%s' % (name, obj_id) 

    except Exception, e:
        print e
        response.status = 400
        status = "unknownError"
        return {'code': 400, 'message' : 'Error: %s' % (str(e)) }

    return {'code': 201, 'message' : 'Created' , 'link': '%s/ecommerce/%s/%s' % (config.get("app", "prefix"), name, obj_id) }

@app.get('/ecommerce/<name>/<id>')
def get_one(name, id):

    print "*** id = %s" % (id,)

    rv = { 'code' : 400, 'message': 'Unknown Error', 'link' : "%s/ecommerce/%s/%s" % (config.get("app", "prefix"), name, id) }

    try:
    
        objects = db[name]
        obj_id = ObjectId(id)
        obj = objects.find_one({"_id":obj_id})

        if obj is None:
            rv['code'] = 404
            rv['message'] = 'not found'
        else:
            obj = sanitize(obj)
            rv['data'] = obj
            rv['code'] = 200
            rv['message'] = 'successful'

    except Exception, e:
        print e
        rv['code'] = 400

    response.status = rv['code']
    print rv
    if rv['code'] == 200: return rv['data']
    else: return None

@app.get('/ecommerce/<name>')
def get_all(name):

    rv = { 'code' : 400, 'message': 'Unknown Error', 'link' : "%s/ecommerce/%s" % (config.get("app", "prefix"), name) }

    try:
    
        objects = db[name]
        objs = list(objects.find())

        if objs is None or len(objs) == 0:
            rv['code'] = 200
            rv['message'] = 'no content'
            rv['data'] = None
        else:
            for obj in objs:
                sanitize(obj)

            rv['data'] = {name : objs }
            rv['code'] = 200
            rv['message'] = 'successful'

    except Exception, e:
        print e
        rv['code'] = 400

    print rv
    response.status = rv['code']
    return rv['data']


@app.put('/ecommerce/<name>/<id>')
def replace(name, id):

    print "*** id = %s" % (id,)

    rv = { 'code' : 400, 'message': 'Unknown Error', 'link' : "%s/ecommerce/%s/%s" % (config.get("app", "prefix"), name, id) }

    try:
        req_json = request.json
        if req_json is None:
            raise Exception("Empty json or no proper content-type to recognize as json")
    except Exception, e:
        response.status = rv['code']
        return rv

    try:
        objects = db[name]
        obj_id = ObjectId(id)
        obj = objects.find_one({"_id":obj_id})

        if obj is None:
            rv['code'] = 404
            rv['message'] = 'not found'
        else:
            try:
                req_json["creationDate"] = obj['creationDate']
                req_json["_id"] = obj_id
                req_json["lastUpdateDate"] = datetime.datetime.utcnow()
                req_json["self"] = "%s/ecommerce/%s/%s" % (config.get("app", "prefix"), name, id)
                x = objects.update({'_id':obj_id}, req_json, upsert=False)
                print "**** new id",
                print x
                rv['code'] = 200
            except Exception, e:
                print e
                rv['message'] = 'Error while saving'

    except Exception, e:
        print e
        response.status = 400
        rv['message'] = 'Error while reading'

    response.status = rv['code']
    return rv

@app.delete('/ecommerce/<name>/<id>')
def delete(name, id):
    rv = { 'code' : 400, 'message': 'Unknown Error', 'link' : "%s/ecommerce/%s/%s" % (config.get("app", "prefix"), name, id) }

    try:
        objects = db[name]
        obj_id = ObjectId(id)
        qry = {"_id":obj_id}
        obj = objects.find_one(qry)

        if obj is None:
            rv['code'] = 404
            rv['message'] = 'not found'
        else:
            try:
                x = objects.remove(qry)
                rv['code'] = 200
                rv['message'] = 'successfully deleted'
            except Exception, e:
                print e
                rv['message'] = 'Error while deleting'

    except Exception, e:
        print e
        response.status = 400
        rv['message'] = 'Error while reading'

    response.status = rv['code']
    return rv

