from gevent import monkey
monkey.patch_all()       #socket()

import sys
from bottle import Bottle, run, ServerAdapter

from multiprocessing import Process, current_process, cpu_count

from util.config import configure, config
# do immediately so that other modules can see config data
configure(sys.argv)

from ecommerce import ecapp
from ecommerce import eccode
from ecommerce import ecschema
#from auth import CloudAuthMiddleware

class GEventServerAdapter(ServerAdapter):
    def run(self, handler):
        from gevent.pywsgi import WSGIServer
        server = WSGIServer((self.host, self.port), handler)
        server.serve_forever()

main_app = Bottle()

main_app.merge(ecapp.app)
main_app.merge(eccode.app)
main_app.merge(ecschema.app)

@main_app.get('/')
def index():
    return {"greeting" : "Hello World!" }

if __name__ == "__main__":
    run(main_app, host='0.0.0.0', 
        port=8080,
        server=GEventServerAdapter, 
        reloader=True,
        debug=True)
