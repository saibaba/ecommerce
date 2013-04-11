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

app = Bottle()

client = MongoClient()
db = client.ecommerce

@app.put('/ecommerce/<name>/triggers/beforePOST')
def create(name):

    try:
        if request.headers['CONTENT_TYPE'] != 'application/javascript' :
            raise Exception("Content type must be application/javascript")
        code = request.body
        if code is None:
            raise Exception("Empty code or no proper content-type to recognize as json")
    except Exception, e:
        response.status = 400
        status = "syntaxError"
        return {'code': 400, 'message' : 'Could not get code' }

    try:
        objects = db[name + "_triggers"]
        content = {}
        content["creationDate"] = datetime.datetime.utcnow()
        content["type"] = "beforePOST"
        content["code"] = code.getvalue()
        obj = objects.remove({"type":"beforePOST"})
        obj_id = objects.insert(content)
        response.status = 201
        response.location = '/ecommerce/%s/triggers/beforePOST' % (name,) 

    except Exception, e:
        print e
        response.status = 400
        status = "unknownError"
        return {'code': 400, 'message' : 'Error: %s' % (str(e)) }

    return {'code': 201, 'message' : 'Created' , 'link': '/ecommerce/%s/triggers/beforePOST' % (name,) }

@app.get('/ecommerce/<name>/triggers/beforePOST')
def get_bi(name):

    rv = { 'code' : 400, 'message': 'Unknown Error', 'link' : "/ecommerce/%s/triggers/beforePOST" % (name, ), 'data': None }

    try:
    
        objects = db[name +"_triggers"]
        obj_id = ObjectId(id)
        obj = objects.find_one({"type":"beforePOST"})

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
    return rv['data']

