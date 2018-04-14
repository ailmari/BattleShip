'''
Created on 25.02.2018

Modified on 25.02.2018

Tests for the API access to ship table.

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

SHIP1 = {
    'id': 1,
    'player': 1,
    'game': 12345,
    'stern_x': 2,
    'stern_y': 3,
    'bow_x': 2,
    'bow_y': 6,
    'ship_type': 'frigate'
}

SHIP2 = {
    'id': 2,
    'player': 1,
    'game': 12345,
    'stern_x': 3,
    'stern_y': 6,
    'bow_x': 6,
    'bow_y': 6,
    'ship_type': 'submarine'
}

SHIP3 = {
    'id': 3,
    'player': 1,
    'game': 12345,
    'stern_x': 3,
    'stern_y': 6,
    'bow_x': 4,
    'bow_y': 4,
    'ship_type': 'submarine'
}

SHIP4 = {
    'id': 4,
    'player': 1,
    'game': 12345,
    'stern_x': 9,
    'stern_y': 5,
    'bow_x': 9,
    'bow_y': 9,
    'ship_type': 'carrier'
}

GAME1_SHIPS = [SHIP1, SHIP2, SHIP3, SHIP4]
PLAYER1_SHIPS = [SHIP1, SHIP2]
PLAYER2_SHIPS = [SHIP3, SHIP4]

NEW_SHIP = {
    'id': 5,
    'player': 1,
    'game': 12345,
    'stern_x': 1,
    'stern_y': 2,
    'bow_x': 1,
    'bow_y': 4,
    'ship_type': 'default'
}

NEW_SHIP_INCORRECT_GAME = {
    'id': 6,
    'player': 1,
    'game': 999999,
    'stern_x': 5,
    'stern_y': 5,
    'bow_x': 4,
    'bow_y': 5,
    'ship_type': 'default'
}

NEW_SHIP_INCORRECT_PLAYER = {
    'id': 7,
    'player': 999999,
    'game': 999999,
    'stern_x': 2,
    'stern_y': 3,
    'bow_x': 2,
    'bow_y': 5,
    'ship_type': 'default'
}

NON_EXISTING_SHIP = {
    'id': 8,
    'player': 7,
    'game': 7,
    'stern_x': 0,
    'stern_y': 0,
    'bow_x': 0,
    'bow_y': 0,
    'ship_type': 'default'
}


class ShipDBTestCase(unittest.TestCase):
    '''
    Tests for methods that access the ship-table.
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
    def test_get_ship(self):
        '''
        Test get_ship.
        '''
        ship = self.connection.get_ship(
            SHIP1['id'],
            SHIP1['player'],
            SHIP1['game']
        )
        self.assertEqual(ship, SHIP1)

    @print_test_info
    def test_get_ship_wrong_id(self):
        '''
        Test get_ship with ID that does not exist.
        '''
        ship = self.connection.get_ship(
            NON_EXISTING_SHIP['id'],
            NON_EXISTING_SHIP['player'],
            NON_EXISTING_SHIP['game']
        )
        self.assertIsNone(ship)

    @print_test_info
    def test_get_ships(self):
        '''
        Test get_ships by game_id
        '''
        ships = self.connection.get_ships(GAME1_ID)
        for ship in ships:
            self.assertIn(ship, GAME1_SHIPS)

    @print_test_info
    def test_get_ships_by_player(self):
        '''
        Test get_ships by game_id and player_id
        '''
        ships = self.connection.get_ships_by_player(GAME1_ID, PLAYER1_ID)
        for ship in ships:
            self.assertIn(ship, PLAYER1_SHIPS)

    @print_test_info
    def test_get_ships_wrong_id(self):
        '''
        Test get_ships with nonexistent game ID.
        '''
        ships = self.connection.get_ships(9999)
        self.assertIsNone(ships)

    @print_test_info
    def test_get_ships_by_player_wrong_id(self):
        '''
        Test get_ships with nonexistent player ID.
        '''
        ships = self.connection.get_ships_by_player(GAME1_ID, 9999)
        self.assertIsNone(ships)

        # TODO : Do we delete ships?
    @print_test_info
    def test_delete_ship(self):
        '''
        Test delete_ship
        '''
        resp = self.connection.delete_ship(SHIP1['id'], SHIP1['player'], SHIP1['game'])
        self.assertTrue(resp)
        resp2 = self.connection.get_ship(SHIP1['id'], SHIP1['player'], SHIP1['game'])
        self.assertIsNone(resp2)

    @print_test_info
    def test_delete_ship_wrong_id(self):
        '''
        Test delete_ship with ID that does not exist.
        '''
        response = self.connection.delete_ship(NON_EXISTING_SHIP['id'], NON_EXISTING_SHIP['player'], NON_EXISTING_SHIP['game'])
        self.assertFalse(response)

    @print_test_info
    def test_create_ship(self):
        '''
        Test create_ship with NEW_SHIP.
        '''
        success = self.connection.create_ship(
            NEW_SHIP['id'],
            NEW_SHIP['player'],
            NEW_SHIP['game'],
            NEW_SHIP['stern_x'],
            NEW_SHIP['stern_y'],
            NEW_SHIP['bow_x'],
            NEW_SHIP['bow_y'],
            NEW_SHIP['ship_type']
        )
        self.assertTrue(success)
        ship = self.connection.get_ship(NEW_SHIP['id'], NEW_SHIP['player'], NEW_SHIP['game'])
        self.assertEqual(ship, NEW_SHIP)

    @print_test_info
    def test_create_ship_incorrect_game(self):
        '''
        Test creating ship into a game that does not exist.
        '''
        success = self.connection.create_ship(
            NEW_SHIP_INCORRECT_GAME['id'],
            NEW_SHIP_INCORRECT_GAME['player'],
            NEW_SHIP_INCORRECT_GAME['game'],
            NEW_SHIP_INCORRECT_GAME['stern_x'],
            NEW_SHIP_INCORRECT_GAME['stern_y'],
            NEW_SHIP_INCORRECT_GAME['bow_x'],
            NEW_SHIP_INCORRECT_GAME['bow_y'],
            NEW_SHIP_INCORRECT_GAME['ship_type']
        )

        self.assertFalse(success)
        ship = self.connection.get_ship(NEW_SHIP_INCORRECT_GAME['id'], NEW_SHIP_INCORRECT_GAME['player'], NEW_SHIP_INCORRECT_GAME['game'])
        self.assertIsNone(ship)

    @print_test_info
    def test_create_ship_same_id_player_and_game(self):
        '''
        Test that a game cannot contain two ships with same ID.
        '''
        success = self.connection.create_ship(
            SHIP1['id'],
            SHIP1['player'],
            SHIP1['game'],
            SHIP1['stern_x'],
            SHIP1['stern_y'],
            SHIP1['bow_x'],
            SHIP1['bow_y'],
            SHIP1['ship_type']
        )

        self.assertFalse(success)


if __name__ == "__main__":
    print("Starting database ship tests...")
    unittest.main()
