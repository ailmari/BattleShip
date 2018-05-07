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

LINK_RELATIONS_URL = "/battleship/link-relations/"

app = Flask(__name__, static_folder="static", static_url_path="/.")
app.debug = True
app.config.update({"Engine": database.Engine()})
api = Api(app)

class MasonObject(dict):
    '''
    Parent class for resources. Adds attributes.
    '''
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

    def add_control_create_game(self):
        if "@controls" not in self:
            self["@controls"] = {}

        self["@controls"]["create-game"] = {
            "href": api.url_for(Games),
            "title": "Create new game",
            "encoding": "json",
            "method": "POST",
            "schema": self._game_schema()
        }

    def add_control_end_game(self, gameid):
        if "@controls" not in self:
            self["@controls"] = {}

        self["@controls"]["end-game"] = {
            "href": api.url_for(Game, gameid=gameid),
            "title": "End this game",
            "method": "PATCH"
        }

    def add_control_delete_game(self, gameid):
        if "@controls" not in self:
            self["@controls"] = {}

        self["@controls"]["delete-game"] = {
            "href": api.url_for(Game, gameid=gameid),
            "title": "Delete this game",
            "method": "DELETE"
        }

    def _game_schema(self):
        schema = {
            "x_size": "Number of columns on the map",
            "y_size": "Number of rows on the map",
            "turn_length": "Time in seconds players have to play one turn"
        }

        return schema

    def add_control_create_player(self, gameid):
        if "@controls" not in self:
            self["@controls"] = {}

        self["@controls"]["create-player"] = {
            "href": api.url_for(Players, gameid=gameid),
            "title": "Create new player to this game",
            "encoding": "json",
            "method": "POST",
            "schema": self._player_schema()
        }

    def add_control_delete_player(self, gameid, playerid):
        if "@controls" not in self:
            self["@controls"] = {}

        self["@controls"]["delete-player"] = {
            "href": api.url_for(Player, gameid=gameid, playerid=playerid),
            "title": "Delete this player",
            "method": "DELETE"
        }

    def _player_schema(self):
        schema = {
            "nickname": "Player's name. Defaults to Anonymous Landlubber, if missing."
        }

        return schema

    def add_control_place_ship(self, gameid):
        if "@controls" not in self:
            self["@controls"] = {}

        self["@controls"]["place-ship"] = {
            "href": api.url_for(Ships, gameid=gameid),
            "title": "Place ship for this player",
            "encoding": "json",
            "method": "POST",
            "schema": self._ship_schema()
        }

    def _ship_schema(self):
        schema = {
            "playerid": "ID of the player who owns the ship",
            "stern_x": "Column of ships stern.",
            "stern_y": "Row of ships stern.",
            "bow_x": "Column of ships bow.",
            "bow_y": "Row of ships bow.",
            "ship_type": "Ship type can be defined by the application."
        }

        return schema

    def add_control_fire_shot(self, gameid):
        if "@controls" not in self:
            self["@controls"] = {}

        self["@controls"]["fire-shot"] = {
            "href": api.url_for(Shots, gameid=gameid),
            "title": "Fire shot to this game",
            "encoding": "json",
            "method": "POST",
            "schema": self._shot_schema()
        }

    def _shot_schema(self):
        schema = {
            "playerid": "Player who is firing.",
            "x": "Column where shot is fired.",
            "y": "Row where shot is fired.",
            "shot_type": "Shot type can be defined by the application."
        }

        return schema

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
    '''
    Games resource iplementation.
    '''
    def get(self):
        '''
        Get all Games which have not ended.

        INPUT PARAMETERS:
            None

        RESPONSE ENTITY BODY:
            * Media type: Mason
            https://github.com/JornWildt/Mason
            * Profile: Battleship_Game
            /profiles/game-profile
        '''
        games_db = g.con.get_games()

        envelope = MasonObject()
        envelope.add_namespace("battleship", LINK_RELATIONS_URL)
        envelope.add_control("self", href=api.url_for(Games))
        envelope.add_control_create_game()

        items = envelope["items"] = []

        for game in games_db:
            if game["end_time"] == None:
                item = MasonObject(id=game["id"])
                item.add_control("self", href=api.url_for(Game, gameid=game["id"]))
                item.add_control("profile", href=BATTLESHIP_GAME_PROFILE)
                items.append(item)

        return Response(json.dumps(envelope), 200, mimetype=MASON+";"+BATTLESHIP_GAME_PROFILE)

    def post(self):
        '''
        Creates a new Game.

        REQUEST ENTITY BODY:
            * Media type: JSON:
            * Profile: Battleship_Game
                /profiles/game-profile

        INPUT PARAMETERS:
            :param int x_size: Number of columns for the game map.
            :param int y_size: Number of rows for the game map.
            :param int turn_length: Turn length in seconds.

        RESPONSE ENTITY BODY:
            * Media type: Mason
                https://github.com/JornWildt/Mason
            * Profile: Battleship_Game
                /profiles/game_profile

        RESPONSE STATUS CODE:
            * Returns 201 if game was created succesfully.
                The Location header contains the path of the new game.
            * Returns 400 if the game is in wrong format, e.g. parameters are missing.
            * Returns 415 if the format of the request is not mason.
            * Returns 500 if the game could not be added to database.
        '''
        if JSON != request.headers.get("Content-Type",""):
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
    '''
    Game resource implementation.
    '''
    def get(self, gameid):
        '''
        Get id, start time, end time, map size and turn length of a single game.

        INPUT PARAMETERS:
            :param int gameid: ID of the game.

        RESPONSE STATUS CODE
            * Return status code 200 if game was retrieved succesfully.
            * Return status code 404 if the game was not found in the database.
        '''
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
        envelope.add_control("players", href=api.url_for(Players, gameid=gameid))
        envelope.add_control("shots", href=api.url_for(Shots, gameid=gameid))
        envelope.add_control("ships", href=api.url_for(Ships, gameid=gameid))
        envelope.add_control_end_game(gameid=gameid)
        envelope.add_control_delete_game(gameid=gameid)

        return Response(json.dumps(envelope), 200, mimetype=MASON+";"+BATTLESHIP_GAME_PROFILE)

    def patch(self, gameid):
        '''
        End a game.
        More specifically, patches a game's end time with timestamp of when this command was received.

        INPUT PARAMETERS:
            :param int gameid: ID of the game.

        RESPONSE STATUS CODE
            * Return status code 200 if game was found and ended succesfully.
            * Return status code 404 if the game was not found in the database.
            * Return status code 409 if the game has already ended.
        '''
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
        '''
        Delete a game from the database.

        INPUT PARAMETERS:
            :param int gameid: ID of the game.

        RESPONSE STATUS CODE
            * Return status code 204 if game was deleted succesfully.
            * Return status code 404 if the game was not found in the database.
        '''
        if g.con.delete_game(gameid):
            return Response(status=204)
        else:
            return create_error_response(404, "Unknown game", "There is no game with id %s" % gameid)

class History(Resource):
    '''
    History resource implementation.
    '''
    def get(self):
        '''
        Get IDs of all Games which have ended.

        INPUT PARAMETERS:
            None

        RESPONSE ENTITY BODY:
            * Media type: Mason
            https://github.com/JornWildt/Mason
            * Profile: Battleship_History
            /profiles/history-profile
        '''
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
    '''
    Player resource implementation.
    '''
    def get(self, gameid):
        '''
        Get all Players in a Game.

        INPUT PARAMETERS:
            :param int gameid: ID of the Game.

        REQUEST ENTITY BODY:
            * Media type: MASON

        OUTPUT:
            * Returns 200 if the game was found and players retrieved succesfully.
            * Returns 404 if there is no game with gameid or the game has no players.

        RESPONSE ENTITY BODY:
            * Media type: Mason
            https://github.com/JornWildt/Mason
            * Profile: Battleship_Player
            /profiles/player-profile
        '''
        game_db = g.con.get_game(gameid)

        if not game_db:
            abort(404, message="There is no game with id %s" % gameid,
                resource_type="Game",
                resource_url=request.path,
                resource_id=gameid)

        players_db = g.con.get_players(gameid)

        if players_db is None:
            players_db = []

        envelope = MasonObject()
        envelope.add_namespace("battleship", LINK_RELATIONS_URL)
        envelope.add_control("self", href=api.url_for(Players, gameid=gameid))
        envelope.add_control("game", href=api.url_for(Game, gameid=gameid))
        envelope.add_control_create_player(gameid=gameid)

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
        '''
        Creates a new Player and adds it to a Game.

        REQUEST ENTITY BODY:
            * Media type: JSON:
            * Profile: Battleship_Player
                /profiles/player-profile

        INPUT PARAMETERS:
            :param int gameid: ID of the Game to join.
            :param str nickname: Nickname for the Player. If empty, defaults to Anonymous Landlubber.

        RESPONSE ENTITY BODY:
            * Media type: Mason
                https://github.com/JornWildt/Mason
            * Profile: Battleship_Player
                /profiles/player-profile

        RESPONSE STATUS CODE:
            * Returns 201 if the Player was created succesfully.
                The Location header contains the path of the new Player.
            * Returns 400 if the game has ended, thus cannot be joined.
            * Returns 415 if the format of the request is not json or the body is not in correct format.
            * Returns 404 if the game cannot be found in the database.
            * Returns 500 if the player could not be added to database.
        '''
        if JSON != request.headers.get("Content-Type", ""):
            abort(415)

        game_db = g.con.get_game(gameid)
        if not game_db:
            abort(404, message="There is no game with id %s" % gameid,
                resource_type="Game",
                resource_url=request.path,
                resource_id=gameid)

        if game_db["end_time"] != None:
            abort(400, message="Cannot join game which has ended!")

        request_body = request.get_json(force=True)
        if not request_body:
            return create_error_response(415, "Unsupported Media Type", "Use a JSON compatible format")
        
        try:
            nickname = request_body["nickname"]
        except KeyError:
            return create_error_response(415, "Unsupported Media Type", "Check the schema for create-player")

        if nickname == "":
            nickname = "Anonymous landlubber"

        playerid = g.con.create_player(nickname, gameid)
        if playerid is None:
            return create_error_response(500, "Problem with the database",
                "Thousand thundering typhoons! Cannot access the database!")
        else:
            url = api.url_for(Player, playerid=playerid, gameid=gameid)
            return Response(status=201, headers={"Location": url})
    
class Player(Resource):
    '''
    Player resource iplementation.
    '''
    def get(self, playerid, gameid):
        '''
        Get id, nickname of a player.
        Get also the gameid which the player belongs to.

        INPUT PARAMETERS:
            :param int playerid: ID of the player.
            :param int gameid: ID of the game.

        RESPONSE STATUS CODE
            * Return status code 200 if player was retrieved succesfully.
            * Return status code 404 if the player was not found in database.
        '''
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
        envelope.add_control_delete_player(gameid=gameid, playerid=playerid)
        envelope.add_control_fire_shot(gameid=gameid)
        envelope.add_control_place_ship(gameid=gameid)

        return Response(json.dumps(envelope), 200, mimetype=MASON+";"+BATTLESHIP_PLAYER_PROFILE)

    def delete(self, playerid, gameid):
        '''
        Delete a player from the database.

        INPUT PARAMETERS:
            :param int playerid: ID of the player.
            :param int gameid: ID of the game.

        RESPONSE STATUS CODE
            * Return status code 204 if player was deleted succesfully.
            * Return status code 404 if the player or the game were not found in the database.
        '''
        game_db = g.con.get_game(gameid)
        if not game_db:
            abort(404, message="There is no game with id %s" % gameid,
                resource_type="Game",
                resource_url=request.path,
                resource_id=gameid)

        if game_db["end_time"] != None:
            abort(400, message="Cannot delete player from game that has ended!")

        if g.con.delete_player(playerid, gameid):
            return Response(status=204)
        else:
            return create_error_response(404, "Unknown player")

class Ships(Resource):
    '''
    Ships resource implementation.
    '''
    def get(self, gameid):
        '''
        Get list of ships in a game.

        INPUT PARAMETERS:
            :param int playerid: ID of the player.
            :param int gameid: ID of the game.

        RESPONSE STATUS CODE
            * Return status code 200 if player was retrieved succesfully.
            * Return status code 404 if the player or the game was not found in the database
                or the player has no ships.
        '''
        game_db = g.con.get_game(gameid)

        if not game_db:
            abort(404, message="There is no game with id %s" % gameid,
                resource_type="Game",
                resource_url=request.path,
                resource_id=gameid)

        ships_db = g.con.get_ships(gameid)

        if ships_db is None:
            ships_db = []

        envelope = MasonObject()
        envelope.add_namespace("battleship", LINK_RELATIONS_URL)
        envelope.add_control("self", href=api.url_for(Ships, gameid=gameid))
        envelope.add_control("game", href=api.url_for(Game, gameid=gameid))

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
            item.add_control("self", href=api.url_for(Ships, gameid=gameid))
            item.add_control("profile", href=BATTLESHIP_SHIP_PROFILE)
            item.add_control("player", href=api.url_for(Player, gameid=gameid, playerid=ship["player"]))
            items.append(item)

        return Response(json.dumps(envelope), 200, mimetype=MASON+";"+BATTLESHIP_SHIP_PROFILE)

    def post(self, gameid):
        '''
        Place a ship for a player in a game.
        TODO add logic to place all / multiple ships etc.

        INPUT PARAMETERS:
            :param int playerid: Players id.
            :param int stern_x: Column of the ship stern.
            :param int stern_y: Row of the ship stern.
            :param int bow_x: Column of the ship bow.
            :param int bow_y: Row of the ship bow.
            :param str ship_type: Type of the ship. Can be used to implement ship specific gameplay mechanics.

        RESPONSE STATUS CODE
            * Return status code 204 if ship was created succesfully.
            * Return status code 415 if the request is not JSON or the request format is incorrect.
            * Return status code 400 if parameters are missing.
            * Return status code 500 if the ship could not be created in the database.
        '''
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
            playerid=request_body["playerid"]
            stern_x=request_body["stern_x"]
            stern_y=request_body["stern_y"]
            bow_x=request_body["bow_x"]
            bow_y=request_body["bow_y"]
            ship_type=request_body["ship_type"]
        except KeyError:
            return create_error_response(400, "Wrong request format", "Include all parameters in the request!")

        if g.con.create_ship(playerid, gameid, stern_x, stern_y, bow_x, bow_y, ship_type):
            return Response(status=204)
        else:
            return create_error_response(500, "Problem with the database",
                "Thousand thundering typhoons! Cannot access the database!")

class Shots(Resource):
    '''
    Shots resource implementation.
    '''
    def get(self, gameid):
        '''
        Get list of shots fired in a game.

        INPUT PARAMETERS:
            :param int gameid: ID of the game.

        RESPONSE STATUS CODE
            * Return status code 200 if shots were retrieved succesfully.
            * Return status code 404 if the game was not found in the database
                or the game has no shots fired.
        '''
        game_db = g.con.get_game(gameid)

        if not game_db:
            abort(404, message="There is no game with id %s" % gameid,
                resource_type="Game",
                resource_url=request.path,
                resource_id=gameid)

        shots_db = g.con.get_shots(gameid)

        if shots_db is None:
            shots_db = []

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
        '''
        Fire a shot in a game.

        INPUT PARAMETERS:
            :param int playerid: ID of the player.
            :param int x: Row where the shot is fired.
            :param int y: Column where the shot is fired.
            :param str shot_type: Shot type can be used to introduce shot specific gameplay mechanics.

        RESPONSE STATUS CODE
            * Return status code 204 if shot was fired succesfully.
            * Return status code 415 if the request is not JSON or the request format is incorrect.
            * Return status code 404 if the game or player were not found in the database.
            * Return status code 403 if not users turn
            * Return status code 400 if parameters are missing.
            * Return status code 500 if the shot or turn could not be created in the database.
        '''
        # Check content type
        if JSON != request.headers.get("Content-Type", ""):
            abort(415)

        # Check game exists
        game_db = g.con.get_game(gameid)
        if not game_db:
            abort(404, message="There is no game with id %s" % gameid,
                resource_type="Game",
                resource_url=request.path,
                resource_id=gameid)

        request_body = request.get_json(force=True)
        if not request_body:
            return create_error_response(415, "Unsupported Media Type", "Use a JSON compatible format")

        # Check body is correct
        try:
            playerid = request_body["playerid"]
            x = request_body["x"]
            y = request_body["y"]
            shot_type = request_body["shot_type"]
        except KeyError:
            return create_error_response(400, "Wrong request format", "Include all parameters in the request!")

        # Check player exists
        player_db = g.con.get_player(playerid, gameid)
        if not player_db:
            abort(404, message="There is no player with id %s" % playerid,
                resource_type="Player",
                resource_url=request.path,
                resource_id=playerid)

        # Shoot!
        latest_turn = g.con.get_current_turn(gameid)

        if not latest_turn: # No shots have been fired yet in this game.
            success = g.con.create_turn(turn_number=0, playerid=playerid, gameid=gameid)
            success = g.con.create_shot(turn=0, playerid=playerid, gameid=gameid, x=x, y=y, shot_type=shot_type) # If create_turn fails, this should fail too.
            if success:
                return Response(status=204)
            else:
                return create_error_response(500, "Problem with the database.",
                    "Thousand thundering typhoons! Cannot access the database!")
        else:
            latest_turn_number = latest_turn[0]['turn_number']

            players_who_have_shot = []
            for shot in g.con.get_shots_by_turn(gameid=gameid, turn=latest_turn_number):
                players_who_have_shot.append(shot['player'])

            players_in_game = []
            for player in g.con.get_players(gameid=gameid):
                players_in_game.append(player['id'])

            if playerid not in players_who_have_shot: # This player has not fired this turn. Fire this turn.
                success = g.con.create_turn(turn_number=latest_turn_number, playerid=playerid, gameid=gameid)
                success = g.con.create_shot(turn=latest_turn_number, playerid=playerid, gameid=gameid, x=x, y=y, shot_type=shot_type)
                if success:
                    return Response(status=204)
                else:
                    return create_error_response(500, "Problem with the database.",
                        "Thousand thundering typhoons! Cannot access the database!")
            elif set(players_who_have_shot) == set(players_in_game): # All players have fired this turn. Create next turn and fire.
                next_turn_number = latest_turn_number + 1
                success = g.con.create_turn(turn_number=next_turn_number, playerid=playerid, gameid=gameid)
                success = g.con.create_shot(turn=next_turn_number, playerid=playerid, gameid=gameid, x=x, y=y, shot_type=shot_type)
                if success:
                    return Response(status=204)
                else:
                    return create_error_response(500, "Problem with the database.",
                        "Thousand thundering typhoons! Cannot access the database!")
            else: # This player has fired but someone else has not. Wait.
                return create_error_response(403, "Forbidden", "Not this player's turn.")

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
api.add_resource(Ships, "/battleship/api/games/<gameid>/ships/",
    endpoint="ships")
api.add_resource(Shots, "/battleship/api/games/<gameid>/shots/",
    endpoint="shots")

@app.route("/profiles/<profile_name>/")
def redirect_to_profile(profile_name):
    return redirect(APIARY_PROFILES_URL + profile_name)

@app.route("/battleship/link-relations/<rel_name>/")
def redirect_to_rels(rel_name):
    return redirect(APIARY_RELS_URL + rel_name)

@app.route("/battleship/schema/<schema_name>/")
def send_json_schema(schema_name):
    return send_from_directory(app.static_folder, "schema/{}.json".format(schema_name))

if __name__ == '__main__':
    # Debug true activates automatic code reloading and improved error messages
    app.run(debug=True)
