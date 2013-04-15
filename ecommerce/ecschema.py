from bottle import Bottle, run, template, install, request,response, route
from util.config import config

import time
import parser

import json

import sys
import traceback
import logging

from bson.objectid import ObjectId

import datetime
from ecommerce.eutil import *

from storage import mongo

app = Bottle()

@app.put('/ecommerce/<name>/metadata/schema')
def create_schema(name):

    rv = { 'code' : 400, 'message': 'Unknown Error', 'link' : "%s/ecommerce/%s/metadata/schema" % (config.get("app", "prefix"), name, ), 'data': None }

    code = None
    try:
        if request.headers['CONTENT_TYPE'] != 'application/json' :
            raise Exception("Content type must be application/json")
        code = request.body.getvalue()

        if code is None:
            raise Exception("Empty code or no proper content-type to recognize as json")
    except Exception, e:
        response.status = 400
        rv['data'] =  {'code': 400, 'message' : 'Could not retrieve script: %s' % (str(e),)  }

    if code is not None:   
        try:
            objects = mongo.db[name + "_schema"]
            content = {}
            content["creationDate"] = datetime.datetime.utcnow()
            content["schema"] = code
            content["type"] = "schema"
            obj = objects.remove({"type":"schema"})
            obj_id = objects.insert(content)
            rv['code'] = 201
            rv['link'] = '%s/ecommerce/%s/metadata/schema' % (config.get("app", "prefix"), name,) 
            rv['data']  = { 'code' : 201, 'message' : 'Created' }

        except Exception, e:
            rv['code'] = 400
            rv['data'] = {'code': 400, 'message' : 'Error: %s' % (str(e)) }

    response.status = rv['code']
    response.location  = rv['link']
    return rv['data']

@app.get('/ecommerce/<name>/metadata/schema')
def get_schema(name):

    rv = { 'code' : 400, 'message': 'Unknown Error', 'link' : "%s/ecommerce/%s/metadata/schema" % (config.get("app", "prefix"), name, ), 'data': None }

    try:
    
        objects = mongo.db[name +"_schema"]
        obj = objects.find_one({"type":"schema"})

        if obj is None:
            rv['code'] = 404
            rv['data'] = { 'code' : 404, 'message': 'not found' }
        else:
            obj = sanitize(obj)
            obj["self"] = "%s/ecommerce/%s/metadata/schema" % (config.get("app", "prefix"), name)
            rv['code'] = 200
            rv['data'] = obj

    except Exception, e:
        rv['code'] = 400
        rv['data'] = { 'code': 400, 'message' : 'Error: %s' % (str(e), ) }

    response.status = rv['code']
    return rv['data']
