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
from battleship import database
from battleship import resources

ENGINE = database.Engine('db/battleship_test.db')

MASONJSON = "application/vnd.mason+json"
JSON = "application/json"

resources.app.config["TESTING"] = True
resources.app.config["SERVER_NAME"] = "localhost:5000"
resources.app.config.update({"Engine": ENGINE})

class GameResourceTestCase(unittest.TestCase):
    '''
    Tests for methods that access the Games and Games resources.
    '''
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
        print("Testing ENDED for ", cls.__name__)
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
            print('(' + function.__name__ + ')', function.__doc__)
            function(self)
        return wrapped_function

    @print_test_info
    def test_url(self):
        """
        Checks that the URL points to the right resource
        """
        url = "/battleship/api/games/12345/"
        print("("+self.test_url.__name__+")", self.test_url.__doc__, end=' ')
        with resources.app.test_request_context(url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEqual(view_point, resources.Game)

    @print_test_info
    def test_get_game(self):
        """
        Checks that GET Game return correct status code and data format
        """
        #Check that I receive status code 200
        resp = self.client.get(flask.url_for("game"))
        self.assertEqual(resp.status_code, 200)

if __name__ == "__main__":
    print("Starting resources game tests...")
    unittest.main()
