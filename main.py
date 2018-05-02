from werkzeug.serving import run_simple
from werkzeug.wsgi import DispatcherMiddleware
from battleship.resources import app as battleship
from client.application import app as client

application = DispatcherMiddleware(battleship, {'/battleship/client': client})

if __name__ == '__main__':
    run_simple('0.0.0.0', 5000, application,
               use_reloader=True, use_debugger=True, use_evalex=True)