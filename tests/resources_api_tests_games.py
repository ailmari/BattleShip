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
BATTLESHIP_GAME_PROFILE = "/profiles/game-profile/"

resources.app.config["TESTING"] = True
resources.app.config["SERVER_NAME"] = "localhost:5000"
resources.app.config.update({"Engine": ENGINE})

url = "/battleship/api/games/"

class GamesResourceTestCase(unittest.TestCase):
    '''
    Tests for methods that access the Games resource.
    '''
    create_game_request_1 = {
        "x_size": "8",
        "y_size": "8",
        "turn_length": "3",
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
    def test_games_url(self):
        """
        Checks that the URL points to the right resource
        """
        with resources.app.test_request_context(url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEqual(view_point, resources.Games)

    @print_test_info
    def test_get_games_success_status(self):
        """
        Checks that GET Games returns correct status code
        """
        # Check that I receive status code 200
        resp = self.client.get(flask.url_for("games"))
        self.assertEqual(resp.status_code, 200)

    @print_test_info
    def test_get_games_headers(self):
        """
        Checks that GET Games returns correct headers
        """
        # Check thant headers are correct
        resp = self.client.get(flask.url_for("games"))
        self.assertEqual(resp.headers.get("Content-Type",None),
                          "{};{}".format(MASONJSON, BATTLESHIP_GAME_PROFILE))

    @print_test_info
    def test_get_games_namespaces(self):
        """
        Checks that GET Games returns correct namespaces
        """
        resp = self.client.get(flask.url_for("games"))
        data = json.loads(resp.data.decode("utf-8"))
        namespaces = data["@namespaces"]
        self.assertIn("battleship", namespaces)
        self.assertIn("name", namespaces["battleship"])

    @print_test_info
    def test_get_games_controls(self):
        """
        Checks that GET Games returns correct controls
        """
        resp = self.client.get(flask.url_for("games"))
        data = json.loads(resp.data.decode("utf-8"))
        controls = data["@controls"]
        self.assertIn("self", controls)
        self.assertIn("href", controls["self"])
        self.assertEqual(controls["self"]["href"], url)
        self.assertIn("create-game", controls)

    @print_test_info
    def test_get_games_items(self):
        """
        Checks that GET Games returns correct items
        """
        resp = self.client.get(flask.url_for("games"))
        data = json.loads(resp.data.decode("utf-8"))
        items = data["items"]
        for item in items:
            self.assertIn("id", item)
            self.assertIn("@controls", item)
            self.assertIn("self", item["@controls"])
            self.assertIn("href", item["@controls"]["self"])
            self.assertIn("profile", item["@controls"])

    @print_test_info
    def test_post_games_success_status(self):
        """
        Checks that POST Games (starting new game) returns correct status when success
        """
        resp = self.client.post(resources.api.url_for(resources.Games),
                                headers={"Content-Type": JSON},
                                data=json.dumps(self.create_game_request_1)
                               )
        self.assertTrue(resp.status_code == 201)

    @print_test_info
    def test_post_games_location_in_header(self):
        """
        Checks that POST Games (starting new game) returns location in header
        """
        resp = self.client.post(resources.api.url_for(resources.Games),
                                headers={"Content-Type": JSON},
                                data=json.dumps(self.create_game_request_1)
                               )
        url = resp.headers.get("Location")
        self.assertIsNotNone(url)

    @print_test_info
    def test_post_games_wrong_media(self):
        """
        Tests creating game with wrong content-type
        """
        resp = self.client.post(resources.api.url_for(resources.Games),
                                headers={"Content-Type": MASONJSON},
                                data=json.dumps(self.create_game_request_1)
                               )
        self.assertTrue(resp.status_code == 415)

    @print_test_info
    def test_game_url(self):
        """
        Checks that the URL points to the right resource
        """
        game_url = url + "0/"
        with resources.app.test_request_context(game_url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEqual(view_point, resources.Game)

    @print_test_info
    def test_get_game(self):
        """
        Checks that GET Game returns correct status code and data format
        """
        # Check that I receive status code 200
        resp = self.client.get(flask.url_for("game", gameid='0'))
        self.assertEqual(resp.status_code, 200)

        # Check thant headers are correct
        self.assertEqual(resp.headers.get("Content-Type",None),
                          "{};{}".format(MASONJSON, BATTLESHIP_GAME_PROFILE))

        # Check that body is correct
        data = json.loads(resp.data.decode("utf-8"))

        controls = data["@controls"]
        self.assertIn("self", controls)
        self.assertIn("profile", controls)
        self.assertIn("collection", controls)

        self.assertIn("id", data)
        self.assertIn("start_time", data)
        self.assertIn("end_time", data)
        self.assertIn("x_size", data)
        self.assertIn("y_size", data)
        self.assertIn("turn_length", data)

    @print_test_info
    def test_delete_game(self):
        """
        Checks that DELETE Game works
        """
        game_url = url + "0/"
        resp = self.client.delete(game_url)
        self.assertEqual(resp.status_code, 204)
        resp2 = self.client.get(game_url)
        self.assertEqual(resp2.status_code, 404)

    @print_test_info
    def test_delete_game_success_status(self):
        """
        Checks that DELETE Game returns correct status
        """
        game_url = url + "0/"
        resp = self.client.delete(game_url)
        self.assertEqual(resp.status_code, 204)

    @print_test_info
    def test_patch_game(self):
        """
        Checks that PATCH Game (end a game) works
        """
        resp = self.client.patch(flask.url_for("game", gameid='1'))
        self.assertEqual(resp.status_code, 204)

    @print_test_info
    def test_patch_game_already_ended(self):
        """
        Checks that PATCH Game (already ended) returns error status
        """
        resp = self.client.patch(flask.url_for("game", gameid='0'))
        self.assertEqual(resp.status_code, 409)

if __name__ == "__main__":
    print("Starting resources games tests...")
    unittest.main()
