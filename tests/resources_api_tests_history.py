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

url = "/battleship/api/history/"

class HistoryResourceTestCase(unittest.TestCase):
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
    def test_history_url(self):
        """
        Checks that the URL points to the right resource
        """
        with resources.app.test_request_context(url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEqual(view_point, resources.History)

    @print_test_info
    def test_get_history_success_status(self):
        """
        Checks that GET History returns correct status code
        """
        # Check that I receive status code 200
        resp = self.client.get(flask.url_for("history"))
        self.assertEqual(resp.status_code, 200)

    @print_test_info
    def test_get_history_headers(self):
        """
        Checks that GET History returns correct headers
        """
        resp = self.client.get(flask.url_for("history"))
        # Check thant headers are correct
        self.assertEqual(resp.headers.get("Content-Type",None),
                          "{};{}".format(MASONJSON, BATTLESHIP_GAME_PROFILE))

    @print_test_info
    def test_get_history_body(self):
        """
        Checks that GET History returns correct body
        """
        resp = self.client.get(flask.url_for("history"))

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
        self.assertEqual(controls["self"]["href"], url)

        items = data["items"]
        for item in items:
            self.assertIn("id", item)
            self.assertIn("@controls", item)
            self.assertIn("self", item["@controls"])
            self.assertIn("href", item["@controls"]["self"])
            self.assertIn("profile", item["@controls"])

if __name__ == "__main__":
    print("Starting resources games tests...")
    unittest.main()
