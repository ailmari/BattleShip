'''
Created on 06.04.2018
Modified on 06.04.2018
@author: arttu
@author: timo
@author: niko
'''
import json

from urllib.parse import unquote

from flask import Flask, request, Response, g, _request_ctx_stack, redirect, send_from_directory
from flask_restful import Resource, Api, abort
from werkzeug.exceptions import NotFound,  UnsupportedMediaType

from battleship.utils import RegexConverter
from battleship import database

MASON = "application/vnd.mason+json"
JSON = "application/json"
BATTLESHIP_GAME_PROFILE = "/profiles/game-profile/"
BATTLESHIP_PLAYER_PROFILE = "/profiles/player-profile/"
ERROR_PROFILE = "/profiles/error-profile"

APIARY_PROJECT = "https://battleship.docs.apiary.io"
APIARY_PROFILES_URL = APIARY_PROJECT+"/#reference/profiles/"
APIARY_RELS_URL = APIARY_PROJECT+"/#reference/link-relations/"

PLAYER_SCHEMA_URL = "/battleship/schema/player/"
LINK_RELATIONS_URL = "/battleship/link-relations/"

app = Flask(__name__, static_folder="static", static_url_path="/.")
app.debug = True
app.config.update({"Engine": database.Engine()})
api = Api(app)

class MasonObject(dict):
    """
    A convenience class for managing dictionaries that represent Mason
    objects. It provides nice shorthands for inserting some of the more
    elements into the object but mostly is just a parent for the much more
    useful subclass defined next. This class is generic in the sense that it
    does not contain any application specific implementation details.
    """
    def add_error(self, title, details):
        self["@error"] = {
            "@message": title,
            "@messages": [details],
        }

    def add_namespace(self, ns, uri):
        if "@namespaces" not in self:
            self["@namespaces"] = {}

        self["@namespaces"][ns] = {
            "name": uri
        }

    def add_control(self, ctrl_name, **kwargs):
        if "@controls" not in self:
            self["@controls"] = {}

        self["@controls"][ctrl_name] = kwargs

# ERROR HANDLERS
def create_error_response(status_code, title, message=None):
    resource_url = None
    ctx = _request_ctx_stack.top
    if ctx is not None:
        resource_url = request.path
    envelope = MasonObject(resource_url=resource_url)
    envelope.add_error(title, message)

    return Response(json.dumps(envelope), status_code, mimetype=MASON+";"+ERROR_PROFILE)

@app.errorhandler(404)
def resource_not_found(error):
    return create_error_response(404, "Resource not found",
        "Thundering typhoons! This crooking resource url does not exist!")

@app.errorhandler(400)
def resource_not_found(error):
    return create_error_response(400, "Malformed input format",
        "Billions of bilious blue blistering barnacles! The heretic format of the input is incorrect!")

@app.errorhandler(500)
def unknown_error(error):
    return create_error_response(500, "Error",
        "Billions of blue blistering boiled and barbecued barnacles in a thundering typhoon! The bloodsucking system has failed!")

@app.before_request
def connect_db():
    g.con = app.config["Engine"].connect()

# HOOKS
@app.teardown_request
def close_connection(exc):
    if hasattr(g, "con"):
        g.con.close()

# RESOURCES
class Games(Resource):
    def get(self):
        games_db = g.con.get_games()

        envelope = MasonObject()
        envelope.add_namespace("battleship", LINK_RELATIONS_URL)
        envelope.add_control("self", href=api.url_for(Games))

        items = envelope["items"] = []

        for game in games_db:             
            item = MasonObject(id=game["id"])
            item.add_control("self", href=api.url_for(Game, gameid=game["id"]))
            item.add_control("profile", href=BATTLESHIP_GAME_PROFILE)
            items.append(item)

        return Response(json.dumps(envelope), 200, mimetype=MASON+";"+BATTLESHIP_GAME_PROFILE)

class Game(Resource):
    def get(self, gameid):
        game_db = g.con.get_game(gameid)

        if not game_db:
            abort(404, message="There is no game with id %s" % gameid,
                resource_type="Game",
                resource_url=request.path,
                resource_id=gameid)

class Players(Resource):
    def get(self, gameid):
        game_db = g.con.get_game(gameid)

        if not game_db:
            abort(404, message="There is no game with id %s" % gameid,
                resource_type="Game",
                resource_url=request.path,
                resource_id=gameid)

        players_db = g.con.get_players(gameid)

        if not players_db:
            abort(404, message="The game with id %s has no players" % gameid,
                resource_type="Game",
                resource_url=request.path,
                resource_id=gameid)
        
        envelope = MasonObject()
        envelope.add_namespace("battleship", LINK_RELATIONS_URL)
        envelope.add_control("self", href=api.url_for(Players, gameid=gameid))

        items = envelope["items"] = []

        for player in players_db:
            item = MasonObject(
                nickname=player["nickname"]
            )
            item.add_control("self", href=api.url_for(Player, playerid=player["id"], gameid=gameid))
            item.add_control("profile", href=BATTLESHIP_PLAYER_PROFILE)
            items.append(item)

        #RENDER
        return Response(json.dumps(envelope), 200, mimetype=MASON+";"+BATTLESHIP_PLAYER_PROFILE)
        
class Player(Resource):
    def get(self, playerid, gameid):
        player_db = g.con.get_player(playerid, gameid)

        if not player_db:
            abort(404, message="There is no player with id %s" % playerid,
                resource_type="Player",
                resource_url=request.path,
                resource_id=playerid)

# ROUTES
app.url_map.converters["regex"] = RegexConverter

api.add_resource(Games, "/battleship/api/games/",
    endpoint="games")
api.add_resource(Game, "/battleship/api/games/<gameid>/",
    endpoint="game")
api.add_resource(Players, "/battleship/api/games/<gameid>/players/",
    endpoint="players")
api.add_resource(Player, "/battleship/api/games/<gameid>/players/<playerid>/",
    endpoint="player")

if __name__ == '__main__':
    # Debug true activates automatic code reloading and improved error messages
    app.run(debug=True)
