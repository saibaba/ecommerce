from bottle import Bottle, run, template, install, request,response, route
#from config import config

#import util
import time
import parser

import json

import sys
import traceback
import logging

from pymongo import MongoClient
from bson.objectid import ObjectId

import datetime
from util import MyEncoder

app = Bottle()

client = MongoClient()
db = client.ecommerce

@app.route('/ecommerce/<name>/<id>', 'PATCH')
def update(name, id):

    print "*** id = %s" % (id,)

    rv = { 'code' : 400, 'message': 'Unknown Error', 'link' : "/ecommerce/%s/%s" % (name, id) }

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
        if req_json is None:
            raise Exception("Empty json or no proper content-type to recognize as json")
    except Exception, e:
        response.status = 400
        status = "syntaxError"
        return {'code': 400, 'message' : 'Could not parse json' }

    try:
        objects = db[name]
        req_json["creationDate"] = datetime.datetime.utcnow()
        obj_id = objects.insert(req_json)
        response.status = 201
        response.location = '/ecommerce/%s/%s' % (name, obj_id) 

    except Exception, e:
        print e
        response.status = 400
        status = "unknownError"
        return {'code': 400, 'message' : 'Error: %s' % (str(e)) }

    return {'code': 201, 'message' : 'Created' , 'link': '/ecommerce/%s/%s' % (name, obj_id) }

@app.get('/ecommerce/<name>/<id>')
def get(name, id):

    print "*** id = %s" % (id,)

    rv = { 'code' : 400, 'message': 'Unknown Error', 'link' : "/ecommerce/%s/%s" % (name, id) }

    try:
    
        objects = db[name]
        obj_id = ObjectId(id)
        obj = objects.find_one({"_id":obj_id})

        if obj is None:
            rv['code'] = 404
            rv['message'] = 'not found'
        else:
            if 'lastUpdateDate' in obj:
                obj['lastUpdateDate'] = obj['lastUpdateDate'].isoformat()
            if 'creationDate' in obj:
                obj['creationDate'] = obj['creationDate'].isoformat()
            if '_id' in obj:
                obj['_id'] = str(obj['_id'])
            rv['data'] = obj
            rv['code'] = 200
            rv['message'] = 'successful'

    except Exception, e:
        print e
        rv['code'] = 400

    response.status = rv['code']
    response.location = rv['link']
    print rv
    return rv['data']

@app.put('/ecommerce/<name>/<id>')
def replace(name, id):

    print "*** id = %s" % (id,)

    rv = { 'code' : 400, 'message': 'Unknown Error', 'link' : "/ecommerce/%s/%s" % (name, id) }

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
