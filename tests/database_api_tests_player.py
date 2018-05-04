'''
Created on 25.02.2018

Modified on 25.02.2018

Tests for the API access to player table.

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

# Constants for different tests


PLAYER1 = {
    'id': 1,
    'nickname': 'Fu1L_s41V0_n05CoP3_720',
    'game': 12345,
}

PLAYER2 = {
    'id': 2,
    'nickname': 'Captain Haddock',
    'game': 12345,
}
PLAYER3 = {
    'id': 3,
    'nickname': 'SUBMARINEGOD',
    'game': 12345,
}

GAME1_ID = 12345
GAME1_PLAYERS = [PLAYER1, PLAYER2, PLAYER3]


NEW_PLAYER = {
    'id': 4,
    'nickname': 'Im_new',
    'game': 12345,
}

NEW_PLAYER_INCORRECT_GAME = {
    'id': 1,
    'nickname': 'Im_new',
    'game': 999,
}


class PlayerDBTestCase(unittest.TestCase):
    '''
    Tests for methods that access the player-table.
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
    def test_get_player(self):
        '''
        Test get_player.
        '''
        player = self.connection.get_player(PLAYER1['id'], PLAYER1['game'])
        self.assertEqual(player, PLAYER1)

    @print_test_info
    def test_get_player_wrong_id(self):
        '''
        Test get_player with ID that does not exist.
        '''
        player = self.connection.get_player('NONEXISTENT', GAME1_ID)
        self.assertIsNone(player)

    @print_test_info
    def test_get_players(self):
        '''
        Test get_players
        '''
        players = self.connection.get_players(GAME1_ID)
        for player in players:
            self.assertIn(player, GAME1_PLAYERS)

    @print_test_info
    def test_get_players_wrong_id(self):
        '''
        Test get_players with nonexistent game ID.
        '''
        players = self.connection.get_players('NONEXISTENT')
        self.assertIsNone(players)

    @print_test_info
    def test_delete_player(self):
        '''
        Test delete_player.
        '''
        resp = self.connection.delete_player(PLAYER1['id'], PLAYER1['game'])
        self.assertTrue(resp)
        resp2 = self.connection.get_player(PLAYER1['id'], PLAYER1['game'])
        self.assertIsNone(resp2)

    @print_test_info
    def test_delete_player_wrong_id(self):
        '''
        Test delete_player with ID that does not exist.
        '''
        response = self.connection.delete_player('NONEXISTENT', GAME1_ID)
        self.assertFalse(response)

    @print_test_info
    def test_create_player(self):
        '''
        Test create_player with NEW_PLAYER.
        '''
        playerid = NEW_PLAYER['id']
        nickname = NEW_PLAYER['nickname']
        gameid = NEW_PLAYER['game']
        success = self.connection.create_player(
            nickname=nickname,
            gameid=gameid,
        )
        self.assertTrue(success)
        player = self.connection.get_player(playerid, gameid)
        self.assertEqual(player, NEW_PLAYER)

    @print_test_info
    def test_create_player_incorrect_gameid(self):
        '''
        Test creating player into a game that does not exist.
        '''
        playerid = NEW_PLAYER_INCORRECT_GAME['id']
        nickname = NEW_PLAYER_INCORRECT_GAME['nickname']
        gameid = NEW_PLAYER_INCORRECT_GAME['game']

        success = self.connection.create_player(
            nickname=nickname,
            gameid=gameid,
        )
        self.assertFalse(success)
        player = self.connection.get_player(playerid, gameid)
        self.assertIsNone(player)


if __name__ == "__main__":
    print("Starting database player tests...")
    unittest.main()
