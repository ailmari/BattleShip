'''
Created on 25.02.2018

Modified on 25.02.2018

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
import sqlite3
from datetime import datetime
from battleship import database


ENGINE = database.Engine('db/battleship_test.db')

GAME1_ID = 0
GAME2_ID = 1

GAME1 = {
    'id': 0,
    'start_time': "2018-2-21 13:40:36.877952",
    'end_time': "2018-2-25 13:40:36.877952",
    'x_size': 10,
    'y_size': 10,
    'turn_length': 5,
}
GAME2 = {
    'id': 1,
    'start_time': "2018-2-22 12:40:36.877952",
    'end_time': None,
    'x_size': 10,
    'y_size': 10,
    'turn_length': 5,
}
GAME3 = {
    'id': 2,
    'start_time': "2018-2-23 12:40:36.877952",
    'end_time': None,
    'x_size': 12,
    'y_size': 12,
    'turn_length': 10,
}

GAMES = [GAME1, GAME2, GAME3]

NEW_GAME = {
    'id': 3,
    'end_time': None,
    'x_size': 10,
    'y_size': 10,
    'turn_length': 5,
}

class GameDBTestCase(unittest.TestCase):
    '''
    Tests for methods that access the game-table.
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
        except Exception as e:
            print("error at setUp:", e)
            ENGINE.clear()

    def tearDown(self):
        '''
        Close underlying connection and remove all records from database
        '''
        self.connection.close()
        ENGINE.clear()

    def print_test_info(function):
        def wrapped_function(self):
            print('(' + function.__name__ + ')', function.__doc__)
            function(self)
        return wrapped_function

    @print_test_info
    def test_get_game(self):
        '''
        Test get_game.
        '''
        game = self.connection.get_game(GAME1_ID)
        self.assertEqual(game, GAME1)
        game2 = self.connection.get_game(GAME2_ID)
        self.assertEqual(game2, GAME2)

    @print_test_info
    def test_get_games(self):
        '''
        Test get_games.
        '''
        games = self.connection.get_games()
        for game in games:
            self.assertIn(game, GAMES)

    @print_test_info
    def test_get_game_wrong_id(self):
        '''
        Test get_game with nonexistent ID.
        '''
        game = self.connection.get_game('NONEXISTENT')
        self.assertIsNone(game)

    @print_test_info
    def test_delete_game(self):
        '''
        Test delete_game.
        '''
        deleted = self.connection.delete_game(GAME1['id'])
        self.assertTrue(deleted)
        game = self.connection.get_game(GAME1['id'])
        self.assertIsNone(game)

    @print_test_info
    def test_delete_game_wrong_id(self):
        '''
        Test delete_game with nonexistent ID.
        '''
        deleted = self.connection.delete_game('NONEXISTENT')
        self.assertFalse(deleted)

    @print_test_info
    def test_create_game(self):
        '''
        Test create_game.
        '''
        kwargs = NEW_GAME.copy()
        kwargs.pop('id')
        kwargs.pop('end_time')
        new_id = self.connection.create_game(**kwargs)
        game = self.connection.get_game(new_id)
        for key, value in NEW_GAME.items():
            self.assertEqual(value, game.get(key))
        # Test that the timeformat is correct. Raises error if not.
        datetime.strptime(game['start_time'], '%Y-%m-%d %H:%M:%S.%f')

    @print_test_info
    def test_insert_game_end_time(self):
        '''
        Test game_insert_end_time.
        '''
        end_time = self.connection.insert_game_end_time(GAME2_ID)
        # Test that the timeformat is correct. Raises error if not.
        datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S.%f')
        game = self.connection.get_game(GAME2_ID)
        for key, value in GAME2.items():
            if key == 'end_time':
                # Test that the timeformat is correct. Raises error if not.
                datetime.strptime(game['end_time'], '%Y-%m-%d %H:%M:%S.%f')
            else:
                self.assertEqual(value, game.get(key))

    @print_test_info
    def test_insert_game_end_time_wrong_id(self):
        '''
        Test game_insert_end_time with nonexistent ID.
        '''
        end_time = self.connection.insert_game_end_time('NONEXISTENT')
        self.assertFalse(end_time)

    @print_test_info
    def test_insert_game_end_time_twice(self):
        '''
        Test that you can't insert end_time twice into same game.
        '''
        end_time = self.connection.insert_game_end_time(GAME1_ID)
        self.assertFalse(end_time)


if __name__ == "__main__":
    print("Starting database game tests...")
    unittest.main()
