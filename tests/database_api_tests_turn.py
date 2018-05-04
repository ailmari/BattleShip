'''
Created on 25.02.2018

Modified on 25.02.2018

Tests for the API access to turn table.

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

from battleship import database


ENGINE = database.Engine('db/battleship_test.db')

GAME1_ID = 12345
PLAYER1_ID = 1
PLAYER2_ID = 2
PLAYER3_ID = 3

P1TURN1 = {
    'turn_number': 1,
    'player': 1,
    'game': 12345,
}
P2TURN1 = {
    'turn_number': 1,
    'player': 2,
    'game': 12345,
}
P3TURN1 = {
    'turn_number': 1,
    'player': 3,
    'game': 12345,
}
P1TURN2 = {
    'turn_number': 2,
    'player': 1,
    'game': 12345,
}
P2TURN2 = {
    'turn_number': 2,
    'player': 2,
    'game': 12345,
}
P3TURN2 = {
    'turn_number': 2,
    'player': 3,
    'game': 12345,
}
NEW_TURN = {
    'turn_number': 3,
    'player': 1,
    'game': 12345,
}


GAME1_TURNS = [P1TURN1, P2TURN1, P3TURN1, P1TURN2, P2TURN2, P3TURN2]
PLAYER1_TURNS = [P1TURN1, P1TURN2]


class TurnDBTestCase(unittest.TestCase):
    '''
    Tests for methods that access the turn-table.
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
    def test_get_turns_by_player(self):
        '''
        Test get_turns_by_player.
        '''
        turns = self.connection.get_turns_by_player(PLAYER1_ID, GAME1_ID)
        for turn in turns:
            self.assertIn(turn, PLAYER1_TURNS)

    @print_test_info
    def test_get_turns_by_player_wrong_id(self):
        '''
        Test get_turns_by_player with wrong player and game ID.
        '''
        turns = self.connection.get_turns_by_player('NONEXISTENT', GAME1_ID)
        self.assertIsNone(turns)
        turns = self.connection.get_turns_by_player(PLAYER1_ID, 'NONEXISTENT')
        self.assertIsNone(turns)

    @print_test_info
    def test_get_turns(self):
        '''
        Test get_turns.
        '''
        turns = self.connection.get_turns(GAME1_ID)
        for turn in turns:
            self.assertIn(turn, GAME1_TURNS)
            
    @print_test_info
    def test_get_current_turn(self):
        '''
        Test get_current_turn.
        '''
        turns = self.connection.get_current_turn(GAME1_ID)
        self.assertEqual(turns[0]['turn_number'], 2)

    @print_test_info
    def test_get_turns_wrong_id(self):
        '''
        Test get_turns with wrong game ID.
        '''
        turns = self.connection.get_turns('NONEXISTENT')
        self.assertIsNone(turns)

    @print_test_info
    def test_create_turn(self):
        '''
        Test create_turn.
        '''
        success = self.connection.create_turn(
            NEW_TURN['turn_number'],
            NEW_TURN['player'],
            NEW_TURN['game'],
        )
        self.assertTrue(success)
        turns = self.connection.get_turns(GAME1_ID)
        new_turns = GAME1_TURNS[:]
        new_turns.append(NEW_TURN)
        self.assertEqual(turns, new_turns)

    @print_test_info
    def test_create_turn_same_twice(self):
        '''
        Test creating_turn with same IDs that already exists.
        '''
        success = self.connection.create_turn(
            P1TURN1['turn_number'],
            P1TURN1['player'],
            P1TURN1['game'],
        )
        self.assertFalse(success)


if __name__ == "__main__":
    print("Starting database turn tests...")
    unittest.main()
