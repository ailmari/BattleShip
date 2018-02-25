'''
Created on 22.02.2018

Modified on 22.02.2018

Testing of the tables of the Battleships program.

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


class TestTableSchemas(unittest.TestCase):
    '''
    Tests for the correction of the created tables.
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
            print('('+function.__name__+')', function.__doc__)
            function(self)
        return wrapped_function

    @print_test_info
    def test_game_table_schema(self):
        '''
        Checks that the game-table has right schema.
        '''
        pass

    @print_test_info
    def test_player_table_schema(self):
        '''
        Checks that the player-table has right schema.
        '''
        pass

    @print_test_info
    def test_ship_table_schema(self):
        '''
        Checks that the ship-table has right schema.
        '''
        pass

    @print_test_info
    def test_turn_table_schema(self):
        '''
        Checks that the turn-table has right schema.
        '''
        pass

    @print_test_info
    def test_shot_table_schema(self):
        '''
        Checks that the shot-table has right schema.
        '''
        pass


if __name__ == "__main__":
    print("Starting database table tests...")
    unittest.main()
