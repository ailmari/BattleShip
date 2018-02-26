'''
Created on 25.02.2018

Modified on 25.02.2018

Tests for the API access to shot table.

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
PLAYER1_ID = 1919
PLAYER2_ID = 1918

SHOT1P1 = {
    'turn': 1,
    'player': PLAYER1_ID,
    'game': GAME1_ID,
    'x': 4,
    'y': 4,
    'shot_type': 'single',
}
SHOT1P2 = {
    'turn': 1,
    'player': PLAYER2_ID,
    'game': GAME1_ID,
    'x': 3,
    'y': 3,
    'shot_type': 'single',
}
SHOT2P1 = {
    'turn': 2,
    'player': PLAYER1_ID,
    'game': GAME1_ID,
    'x': 5,
    'y': 4,
    'shot_type': 'single',
}
NEW_SHOT = {
    'turn': 2,
    'player': PLAYER2_ID,
    'game': GAME1_ID,
    'x': 6,
    'y': 7,
    'shot_type': 'single',
}

GAME1_SHOTS = [SHOT1P1, SHOT1P2, SHOT2P1]
PLAYER1_SHOTS = [SHOT1P1, SHOT2P1]
PLAYER2_SHOTS = [SHOT1P2]
TURN1_SHOTS = [SHOT1P1, SHOT1P2]
TURN2_SHOTS = [SHOT2P1]


class ShotDBTestCase(unittest.TestCase):
    '''
    Tests for methods that access the shot-table.
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
    def test_get_shots(self):
        '''
        Test get_shots.
        '''
        shots = self.connection.get_shots(GAME1_ID)
        for shot in shots:
            self.assertIn(shot, GAME1_SHOTS)

    @print_test_info
    def test_get_shots_wrong_id(self):
        '''
        Test get_shots from nonexistent game.
        '''
        shots = self.connection.get_shots('NONEXISTENT')
        self.assertIsNone(shots)

    @print_test_info
    def test_get_shots_by_player(self):
        '''
        Test get_shots_by_player.
        '''
        shots = self.connection.get_shots_by_player(PLAYER1_ID, GAME1_ID)
        for shot in shots:
            self.assertIn(shot, PLAYER1_SHOTS)

    @print_test_info
    def test_get_shots_by_player_wrong_id(self):
        '''
        Test get_shots_by_player with wrong ids.
        '''
        shots = self.connection.get_shots_by_player('NONEXISTENT', GAME1_ID)
        self.assertIsNone(shots)
        shots2 = self.connection.get_shots_by_player(PLAYER1_ID, 'NONEXISTENT')
        self.assertIsNone(shots2)

    @print_test_info
    def test_get_shots_by_turn(self):
        '''
        Test get_shots_by_turn.
        '''
        shots = self.connection.get_shots_by_turn(GAME1_ID, 1)
        for shot in shots:
            self.assertIn(shot, TURN1_SHOTS)
        shots2 = self.connection.get_shots_by_turn(GAME1_ID, 2)
        for shot in shots2:
            self.assertIn(shot, TURN2_SHOTS)

    @print_test_info
    def test_get_shots_by_turn_wrong_id(self):
        '''
        Test get_shots_by_turn with wrong ids.
        '''
        shots = self.connection.get_shots_by_turn('NONEXISTENT', 1)
        self.assertIsNone(shots)
        shots2 = self.connection.get_shots_by_turn(GAME1_ID, 'NONEXISTENT')
        self.assertIsNone(shots2)

    def test_create_shot(self):
        '''
        Test create_shot.
        '''
        turn = NEW_SHOT['turn']
        playerid = NEW_SHOT['player']
        gameid = NEW_SHOT['game']
        x = NEW_SHOT['x']
        y = NEW_SHOT['y']
        shot_type = NEW_SHOT['shot_type']
        success = self.connection.create_shot(
            turn,
            playerid,
            gameid,
            x,
            y,
            shot_type,
        )
        self.assertTrue(success)
        new_turn2_shots = TURN2_SHOTS[:]
        new_turn2_shots.append(NEW_SHOT)
        shots = self.connection.get_shots_by_turn(GAME1_ID, 2)
        for shot in shots:
            self.assertIn(shot, new_turn2_shots)


if __name__ == "__main__":
    print("Starting database shot tests...")
    unittest.main()
