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
            print('(' + function.__name__ + ')', function.__doc__)
            function(self)
        return wrapped_function

    def _test_table_schema(self, table_name, real_table_name_and_type, real_foreign_keys):
        '''
        Test logic for testing table schemas.
        :param str table_name: Name of the table which is tested.
        :param list real_table_name_and_type: List of items in the form of (name, type),
            These are the real name and type of each field of the table.
        :param list real_foreign_keys: List of the foreign keys the table is supposed to contain.
        '''
        con = self.connection.con
        with con:
            c = con.cursor()
            c.execute('PRAGMA TABLE_INFO({})'.format(table_name))
            result = c.fetchall()
            # Check Name and Type
            sql_results = ((items[1], items[2]) for items in result)
            for real_result, sql_result in zip(real_table_name_and_type, sql_results):
                self.assertEqual(real_result, sql_result)
            # Check foreign keys
            c.execute('PRAGMA FOREIGN_KEY_LIST({})'.format(table_name))
            result = c.fetchall()
            # Foreign_keys_list fields: id, seq, table, from, to, on_update, on_delete, match
            result_filtered = [(item[2], item[3], item[4]) for item in result]
            self.assertEqual(result_filtered, real_foreign_keys)

    @print_test_info
    def test_game_table_schema(self):
        '''
        Checks that the game-table has right schema.
        '''
        table_name = 'game'
        real_results = [
            ('id', 'INTEGER'),
            ('start_time', 'DATETIME'),
            ('end_time', 'DATETIME'),
            ('x_size', 'INTEGER'),
            ('y_size', 'INTEGER'),
            ('turn_length', 'INTEGER'),
        ]
        foreign_keys = []
        self._test_table_schema(table_name, real_results, foreign_keys)

    @print_test_info
    def test_player_table_schema(self):
        '''
        Checks that the player-table has right schema.
        '''
        table_name = 'player'
        real_results = [
            ('id', 'INTEGER'),
            ('nickname', 'TEXT'),
            ('game', 'INTEGER'),
        ]
        foreign_keys = [('game', 'game', 'id')]
        self._test_table_schema(table_name, real_results, foreign_keys)

    @print_test_info
    def test_ship_table_schema(self):
        '''
        Checks that the ship-table has right schema.
        '''
        table_name = 'ship'
        real_results = [
            ('id', 'INTEGER'),
            ('player', 'INTEGER'),
            ('game', 'INTEGER'),
            ('stern_x', 'INTEGER'),
            ('stern_y', 'INTEGER'),
            ('bow_x', 'INTEGER'),
            ('bow_y', 'INTEGER'),
            ('ship_type', 'TEXT'),
        ]
        foreign_keys = [
            ('player', 'player', 'id'),
            ('player', 'game', 'game'),
        ]
        self._test_table_schema(table_name, real_results, foreign_keys)

    @print_test_info
    def test_turn_table_schema(self):
        '''
        Checks that the turn-table has right schema.
        '''
        table_name = 'turn'
        real_results = [
            ('turn_number', 'INTEGER'),
            ('player', 'INTEGER'),
            ('game', 'INTEGER'),
        ]
        foreign_keys = [
            ('player', 'player', 'id'),
            ('player', 'game', 'game'),
        ]
        self._test_table_schema(table_name, real_results, foreign_keys)

    @print_test_info
    def test_shot_table_schema(self):
        '''
        Checks that the shot-table has right schema.
        '''
        table_name = 'shot'
        real_results = [
            ('turn', 'INTEGER'),
            ('player', 'INTEGER'),
            ('game', 'INTEGER'),
            ('x', 'INTEGER'),
            ('y', 'INTEGER'),
            ('shot_type', 'TEXT'),
        ]
        foreign_keys = [
            ('turn', 'turn', 'turn_number'),
            ('turn', 'player', 'player'),
            ('turn', 'game', 'game'),
        ]
        self._test_table_schema(table_name, real_results, foreign_keys)


if __name__ == "__main__":
    print("Starting database table tests...")
    unittest.main()
