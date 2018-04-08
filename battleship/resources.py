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
BATTLESHIP_SHIP_PROFILE = "/profiles/ship-profile/"
BATTLESHIP_SHOT_PROFILE = "/profiles/shot-profile/"
ERROR_PROFILE = "/profiles/error-profile/"

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
            if game["end_time"] == None:
                item = MasonObject(id=game["id"])
                item.add_control("self", href=api.url_for(Game, gameid=game["id"]))
                item.add_control("profile", href=BATTLESHIP_GAME_PROFILE)
                items.append(item)

        return Response(json.dumps(envelope), 200, mimetype=MASON+";"+BATTLESHIP_GAME_PROFILE)

    def post(self):
        if MASON != request.headers.get("Content-Type",""):
            return create_error_response(415, "UnsupportedMediaType",
                                         "Macrocephalic baboon! Use a JSON compatible format!")
        request_body = request.get_json(force=True)

        try:
            x_size = request_body["x_size"]
            y_size = request_body["y_size"]
            turn_length = request_body["turn_length"]
        except KeyError:
            return create_error_response(400, "Wrong request format",
                "Toffee-nose! Include x_size, y_size and turn_length for the game!")

        gameid = g.con.create_game(x_size, y_size, turn_length)
        if not gameid:
            return create_error_response(500, "Problem with the database",
                "Thousand thundering typhoons! Cannot access the database!")

        url = api.url_for(Game, gameid=gameid)

        return Response(status=201, headers={"Location": url})

class Game(Resource):
    def get(self, gameid):
        game_db = g.con.get_game(gameid)

        if not game_db:
            abort(404, message="There is no game with id %s" % gameid,
                resource_type="Game",
                resource_url=request.path,
                resource_id=gameid)

        envelope = MasonObject(
            id=game_db["id"],
            start_time=game_db["start_time"],
            end_time=game_db["end_time"],
            x_size=game_db["x_size"],
            y_size=game_db["y_size"],
            turn_length=game_db["turn_length"]
        )
        envelope.add_namespace("battleship", LINK_RELATIONS_URL)
        envelope.add_control("profile", href=BATTLESHIP_GAME_PROFILE)
        envelope.add_control("self", href=api.url_for(Game, gameid=gameid))
        envelope.add_control("collection", href=api.url_for(Games))

        return Response(json.dumps(envelope), 200, mimetype=MASON+";"+BATTLESHIP_GAME_PROFILE)

    def patch(self, gameid):
        game_db = g.con.get_game(gameid)

        if not game_db:
            abort(404, message="Vegetarian! There is no game with id %s!" % gameid,
                resource_type="Game",
                resource_url=request.path,
                resource_id=gameid)

        if g.con.insert_game_end_time(gameid):
            url = api.url_for(Game, gameid=gameid)
            return Response(status=204)
        else:
            abort(409, message="Baboon! The game has already ended!",
                resource_type="Game",
                resource_url=request.path,
                resource_id=gameid)

    def delete(self, gameid):
        if g.con.delete_game(gameid):
            return Response(status=204)
        else:
            return create_error_response(404, "Unknown game", "There is no game with id %s" % gameid)

class History(Resource):
    def get(self):
        games_db = g.con.get_games()

        envelope = MasonObject()
        envelope.add_namespace("battleship", LINK_RELATIONS_URL)
        envelope.add_control("self", href=api.url_for(History))

        items = envelope["items"] = []

        for game in games_db:
            if game["end_time"] != None:
                item = MasonObject(id=game["id"])
                item.add_control("self", href=api.url_for(Game, gameid=game["id"]))
                item.add_control("profile", href=BATTLESHIP_GAME_PROFILE)
                items.append(item)

        return Response(json.dumps(envelope), 200, mimetype=MASON+";"+BATTLESHIP_GAME_PROFILE)

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
        envelope.add_control("game", href=api.url_for(Game, gameid=gameid))

        items = envelope["items"] = []

        for player in players_db:
            item = MasonObject(
                id=player["id"],
                nickname=player["nickname"],
                game=player["game"]
            )
            item.add_control("self", href=api.url_for(Player, playerid=player["id"], gameid=gameid))
            item.add_control("profile", href=BATTLESHIP_PLAYER_PROFILE)
            item.add_control("game", href=api.url_for(Game, gameid=gameid))
            items.append(item)

        return Response(json.dumps(envelope), 200, mimetype=MASON+";"+BATTLESHIP_PLAYER_PROFILE)
    
    def post(self, gameid):
        if JSON != request.headers.get("Content-Type", ""):
            abort(415)

        game_db = g.con.get_game(gameid)
        if not game_db:
            abort(404, message="There is no game with id %s" % gameid,
                resource_type="Game",
                resource_url=request.path,
                resource_id=gameid)

        request_body = request.get_json(force=True)
        if not request_body:
            return create_error_response(415, "Unsupported Media Type", "Use a JSON compatible format")

        try:
            playerid = request_body["id"]
        except KeyError:
            return create_error_response(400, "Wrong request format", "Player id is missing from the request!")
        
        try:
            nickname = request_body["nickname"]
        except KeyError:
            nickname = "Anonymous landlubber"

        if g.con.create_player(playerid, nickname, gameid):
            url = api.url_for(Player, playerid=playerid, gameid=gameid)
            return Response(status=201, headers={"Location": url})
        else:
            return create_error_response(500, "Problem with the database",
                "Thousand thundering typhoons! Cannot access the database!")
    
class Player(Resource):
    def get(self, playerid, gameid):
        player_db = g.con.get_player(playerid, gameid)

        if not player_db:
            abort(404, message="There is no player with id %s" % playerid,
                resource_type="Player",
                resource_url=request.path,
                resource_id=playerid)

        envelope = MasonObject(
            id=player_db["id"],
            nickname=player_db["nickname"],
            game=player_db["game"]
        )
        envelope.add_namespace("battleship", LINK_RELATIONS_URL)
        envelope.add_control("self", href=api.url_for(Player, playerid=playerid, gameid=gameid))
        envelope.add_control("profile", href=BATTLESHIP_PLAYER_PROFILE)
        envelope.add_control("collection", href=api.url_for(Players, gameid=gameid))
        envelope.add_control("game", href=api.url_for(Game, gameid=gameid))

        return Response(json.dumps(envelope), 200, mimetype=MASON+";"+BATTLESHIP_PLAYER_PROFILE)

    def delete(self, playerid, gameid):
        if g.con.delete_player(playerid, gameid):
            return Response(status=204)
        else:
            return create_error_response(404, "Unknown player or game")

class Ships(Resource):
    def get(self, playerid, gameid):
        game_db = g.con.get_game(gameid)

        if not game_db:
            abort(404, message="There is no game with id %s" % gameid,
                resource_type="Game",
                resource_url=request.path,
                resource_id=gameid)

        player_db = g.con.get_player(playerid, gameid)

        if not player_db:
            abort(404, message="There is no player with id %s" % playerid,
                resource_type="Player",
                resource_url=request.path,
                resource_id=playerid)

        ships_db = g.con.get_ships_by_player(gameid, playerid)

        if not ships_db:
            abort(404, message="There are no ships owned by player with id %s" % playerid,
                resource_type="Ships",
                resource_url=request.path,
                resource_id=playerid)

        envelope = MasonObject()
        envelope.add_namespace("battleship", LINK_RELATIONS_URL)
        envelope.add_control("self", href=api.url_for(Ships, playerid=playerid, gameid=gameid))
        envelope.add_control("game", href=api.url_for(Game, gameid=gameid))
        envelope.add_control("player", href=api.url_for(Player, playerid=playerid, gameid=gameid))

        items = envelope["items"] = []

        for ship in ships_db:
            item = MasonObject(
                id=ship["id"],
                player=ship["player"],
                game=ship["game"],
                stern_x=ship["stern_x"],
                stern_y=ship["stern_y"],
                bow_x=ship["bow_x"],
                bow_y=ship["bow_y"],
                ship_type=ship["ship_type"]
            )
            item.add_control("self", href=api.url_for(Ships, playerid=playerid, gameid=gameid))
            item.add_control("profile", href=BATTLESHIP_SHIP_PROFILE)
            items.append(item)

        return Response(json.dumps(envelope), 200, mimetype=MASON+";"+BATTLESHIP_SHIP_PROFILE)

    def put(self, playerid, gameid):
        if JSON != request.headers.get("Content-Type", ""):
            abort(415)

        game_db = g.con.get_game(gameid)
        if not game_db:
            abort(404, message="There is no game with id %s" % gameid,
                resource_type="Game",
                resource_url=request.path,
                resource_id=gameid)

        request_body = request.get_json(force=True)
        if not request_body:
            return create_error_response(415, "Unsupported Media Type", "Use a JSON compatible format")

        try:
            shipid=request_body["shipid"]
            stern_x=request_body["stern_x"]
            stern_y=request_body["stern_y"]
            bow_x=request_body["bow_x"]
            bow_y=request_body["bow_y"]
            ship_type=request_body["ship_type"]
        except KeyError:
            return create_error_response(400, "Wrong request format", "Include all parameters in the request!")

        if g.con.create_ship(shipid, playerid, gameid, stern_x, stern_y, bow_x, bow_y, ship_type):
            return Response(status=204)
        else:
            return create_error_response(500, "Problem with the database",
                "Thousand thundering typhoons! Cannot access the database!")

class Shots(Resource):
    def get(self, gameid):
        game_db = g.con.get_game(gameid)

        if not game_db:
            abort(404, message="There is no game with id %s" % gameid,
                resource_type="Game",
                resource_url=request.path,
                resource_id=gameid)

        shots_db = g.con.get_shots(gameid)

        if not shots_db:
            abort(404, message="There are no shots in game with id %s" % gameid,
                resource_type="Shots",
                resource_url=request.path,
                resource_id=gameid)

        envelope = MasonObject()
        envelope.add_namespace("battleship", LINK_RELATIONS_URL)
        envelope.add_control("self", href=api.url_for(Shots, gameid=gameid))
        envelope.add_control("game", href=api.url_for(Game, gameid=gameid))

        items = envelope["items"] = []

        for shot in shots_db:
            item = MasonObject(
                turn=shot["turn"],
                player=shot["player"],
                game=shot["game"],
                x=shot["x"],
                y=shot["y"],
                shot_type=shot["shot_type"]
            )
            item.add_control("self", href=api.url_for(Shots, gameid=gameid))
            item.add_control("profile", href=BATTLESHIP_SHOT_PROFILE)
            items.append(item)

        return Response(json.dumps(envelope), 200, mimetype=MASON+";"+BATTLESHIP_SHOT_PROFILE)

    def post(self, gameid):
        if JSON != request.headers.get("Content-Type", ""):
            abort(415)

        game_db = g.con.get_game(gameid)
        if not game_db:
            abort(404, message="There is no game with id %s" % gameid,
                resource_type="Game",
                resource_url=request.path,
                resource_id=gameid)

        request_body = request.get_json(force=True)
        if not request_body:
            return create_error_response(415, "Unsupported Media Type", "Use a JSON compatible format")

        try:
            turn = request_body["turn"]
            playerid = request_body["playerid"]
            x = request_body["x"]
            y = request_body["y"]
            shot_type = request_body["shot_type"]
        except KeyError:
            return create_error_response(400, "Wrong request format", "Include all parameters in the request!")

        if g.con.create_shot(turn, playerid, gameid, x, y, shot_type):
            return Response(status=204)
        else:
            return create_error_response(500, "Problem with the database",
                "Thousand thundering typhoons! Cannot access the database!")

# ROUTES
app.url_map.converters["regex"] = RegexConverter

api.add_resource(Games, "/battleship/api/games/",
    endpoint="games")
api.add_resource(Game, "/battleship/api/games/<gameid>/",
    endpoint="game")
api.add_resource(History, "/battleship/api/history/",
    endpoint="history")
api.add_resource(Players, "/battleship/api/games/<gameid>/players/",
    endpoint="players")
api.add_resource(Player, "/battleship/api/games/<gameid>/players/<playerid>/",
    endpoint="player")
api.add_resource(Ships, "/battleship/api/games/<gameid>/players/<playerid>/ships/",
    endpoint="ships")
api.add_resource(Shots, "/battleship/api/games/<gameid>/shots/",
    endpoint="shots")

if __name__ == '__main__':
    # Debug true activates automatic code reloading and improved error messages
    app.run(debug=True)
