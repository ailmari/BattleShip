'''
Created on 14.04.2018

Modified on 15.04.2018

Tests for the API access to game table.

Programmable Web Project course work by:

@author: arttu
@author: niko
@author: timo

Based on course exercises code by:

@author: ivan
@author: mika oja
'''

import unittest
import flask
import json
from battleship import database
from battleship import resources

ENGINE = database.Engine('db/battleship_test.db')

MASONJSON = "application/vnd.mason+json"
JSON = "application/json"
BATTLESHIP_PLAYER_PROFILE = "/profiles/player-profile/"

resources.app.config["TESTING"] = True
resources.app.config["SERVER_NAME"] = "localhost:5000"
resources.app.config.update({"Engine": ENGINE})

class PlayersResourceTestCase(unittest.TestCase):
    '''
    Tests for methods that access the Players resource.
    '''
    create_player_request = {
        "nickname": "Jack Sparrow"
    }

    @classmethod
    def setUpClass(cls):
        ''' Creates the database structure. Removes first any preexisting
            database file
        '''
        print("Testing ", cls.__name__)
        ENGINE.remove_database()
        ENGINE.create_tables()

    @classmethod
    def tearDownClass(cls):
        '''Remove the testing database'''
        print("\nTesting ENDED for ", cls.__name__)
        ENGINE.remove_database()

    def setUp(self):
        '''
        Populates the database
        '''
        try:
            ENGINE.populate_tables()
            self.connection = ENGINE.connect()
            self.app_context = resources.app.app_context()
            self.app_context.push()
            self.client = resources.app.test_client()
        except Exception as e:
            print("error at setUp:", e)
            ENGINE.clear()

    def tearDown(self):
        '''
        Close underlying connection and remove all records from database
        '''
        self.connection.close()
        ENGINE.clear()
        self.app_context.pop()

    def print_test_info(function):
        def wrapped_function(self):
            print('\n(' + function.__name__ + ')', function.__doc__)
            function(self)
        return wrapped_function

    @print_test_info
    def test_players_url(self):
        """
        Checks that the URL points to the right resource
        """
        url = "/battleship/api/games/0/players/"
        with resources.app.test_request_context(url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEqual(view_point, resources.Players)

    @print_test_info
    def test_get_players(self):
        """
        Checks that GET Players returns correct status code and data format
        """
        resp = self.client.get(flask.url_for("players", gameid='0'))
        self.assertEqual(resp.status_code, 200)

        # Check thant headers are correct
        self.assertEqual(resp.headers.get("Content-Type",None),
                          "{};{}".format(MASONJSON, BATTLESHIP_PLAYER_PROFILE))

        # Check that I receive a collection and adequate href
        data = json.loads(resp.data.decode("utf-8"))

        # Check namespaces
        namespaces = data["@namespaces"]
        self.assertIn("battleship", namespaces)
        self.assertIn("name", namespaces["battleship"])

        # Check controls
        controls = data["@controls"]
        self.assertIn("self", controls)
        self.assertIn("href", controls["self"])
        self.assertEqual(controls["self"]["href"], "/battleship/api/games/0/players/")

        items = data["items"]
        for item in items:
            self.assertIn("id", item)
            self.assertIn("@controls", item)
            self.assertIn("self", item["@controls"])
            self.assertIn("href", item["@controls"]["self"])
            self.assertIn("profile", item["@controls"])

    @print_test_info
    def test_get_players_none_game(self):
        """
        Checks that GET Players for non-existing game returns error
        """
        resp = self.client.get(flask.url_for("players", gameid='99999'))
        self.assertEqual(resp.status_code, 404)

    @print_test_info
    def test_post_player(self):
        """
        Checks that POST Players (join game) works
        """
        resp = self.client.post(flask.url_for("players", gameid='1'),
            headers={"Content-Type": JSON,
                "Accept": MASONJSON},
            data=json.dumps(self.create_player_request))
        self.assertEqual(resp.status_code, 201)

        self.assertIn("Location", resp.headers)
        url = resp.headers["Location"]
        resp2 = self.client.get(url)
        self.assertEqual(resp2.status_code, 200)

    @print_test_info
    def test_post_player_ended_game(self):
        """
        Checks that POST Players to ended game returns error
        """
        resp = self.client.post(flask.url_for("players", gameid='0'),
            headers={"Content-Type": JSON,
                "Accept": MASONJSON},
            data=json.dumps(self.create_player_request))
        self.assertEqual(resp.status_code, 400)

    @print_test_info
    def test_get_player(self):
        """
        Checks that GET Player returns correct status code and data format
        """
        resp = self.client.get(flask.url_for("player", gameid="0", playerid="0"))
        self.assertEqual(resp.status_code, 200)

        data = json.loads(resp.data.decode("utf-8"))

        # Check controls
        controls = data["@controls"]
        self.assertIn("self", controls)
        self.assertIn("href", controls["self"])
        self.assertIn("collection", controls)
        self.assertEqual(controls["self"]["href"], "/battleship/api/games/0/players/0/")

        self.assertIn("id", data)
        self.assertIn("nickname", data)
        self.assertIn("game", data)

    @print_test_info
    def test_delete_player(self):
        """
        Checks that DELETE Player works
        """
        url = "/battleship/api/games/0/players/0/"
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, 204)
        resp2 = self.client.get(url)
        self.assertEqual(resp2.status_code, 404)

if __name__ == "__main__":
    print("Starting resources players tests...")
    unittest.main()
