'''
Created on 21.02.2018

Modified on 21.02.2018

Provides the database API to access the battleship persistent data.

Programmable Web Project course work by:

@author: arttu
@author: niko
@author: timo

Based on course exercises code by:

@author: ivan
@author: mika oja
'''

from datetime import datetime
import os
import re
import sqlite3
import time


# Default paths for .db and .sql files to create and populate the database.
DEFAULT_DB_PATH = 'db/battleship.db'
DEFAULT_SCHEMA = "db/battleship_schema_dump.sql"
DEFAULT_DATA_DUMP = "db/battleship_data_dump.sql"


class Engine(object):
    '''
    Abstraction of the database.

    It includes tools to create, configure,
    populate and connect to the sqlite file. You can access the Connection
    instance, and hence, to the database interface itself using the method
    :py:meth:`connection`.

    :Example:

    >>> engine = Engine()
    >>> con = engine.connect()

    :param db_path: The path of the database file (always with respect to the
        calling script. If not specified, the Engine will use the file located
        at *db/battleship.db*
    '''
    def __init__(self, db_path=None):
            '''
            '''

            super(Engine, self).__init__()
            if db_path is not None:
                self.db_path = db_path
            else:
                self.db_path = DEFAULT_DB_PATH

    def connect(self):
        '''
        Creates a connection to the database.

        :return: A Connection instance
        :rtype: Connection
        '''
        return Connection(self.db_path)

    def remove_database(self):
        '''
        Removes the database file from the filesystem.
        '''
        if os.path.exists(self.db_path):
            # THIS REMOVES THE DATABASE STRUCTURE
            os.remove(self.db_path)

    def clear(self):
        '''
        Purge the database removing all records from the tables. However,
        it keeps the database schema (meaning the table structure)
        '''
        keys_on = 'PRAGMA foreign_keys = ON'
        # THIS KEEPS THE SCHEMA AND REMOVE VALUES
        con = sqlite3.connect(self.db_path)
        # Activate foreing keys support
        cur = con.cursor()
        cur.execute(keys_on)
        with con:
            cur = con.cursor()
            cur.execute("DELETE FROM game")
            cur.execute("DELETE FROM player")
            cur.execute("DELETE FROM ship")
            cur.execute("DELETE FROM turn")
            cur.execute("DELETE FROM shot")
            # NOTE do we need to delete player, ship, turn and shot,
            # since they have ON DELETE CASCADE?

    # METHODS TO CREATE AND POPULATE A DATABASE USING DIFFERENT SCRIPTS
    def create_tables(self, schema=None):
        '''
        Create programmatically the tables from a schema file.

        :param schema: path to the .sql schema file. If this parmeter is
            None, then *db/battleship_schema_dump.sql* is utilized.
        '''
        con = sqlite3.connect(self.db_path)
        if schema is None:
            schema = DEFAULT_SCHEMA
        try:
            with open(schema, encoding="utf-8") as f:
                sql = f.read()
                cur = con.cursor()
                cur.executescript(sql)
        finally:
            con.close()

    def populate_tables(self, dump=None):
        '''
        Populate programmatically the tables from a dump file.

        :param dump:  path to the .sql dump file. If this parmeter is
            None, then *db/battleship_data_dump.sql* is utilized.
        '''
        keys_on = 'PRAGMA foreign_keys = ON'
        con = sqlite3.connect(self.db_path)
        # Activate foreing keys support
        cur = con.cursor()
        cur.execute(keys_on)
        # Populate database from dump
        if dump is None:
            dump = DEFAULT_DATA_DUMP
        with open(dump, encoding="utf-8") as f:
            sql = f.read()
            cur = con.cursor()
            cur.executescript(sql)


class Connection(object):
    '''
    API to access the BattleShip database.

    The sqlite3 connection instance is accessible to all the methods of this
    class through the :py:attr:`self.con` attribute.

    An instance of this class should not be instantiated directly using the
    constructor. Instead use the :py:meth:`Engine.connect`.

    Use the method :py:meth:`close` in order to close a connection.
    A :py:class:`Connection` **MUST** always be closed once when it is not going to be
    utilized anymore in order to release internal locks.

    :param db_path: Location of the database file.
    :type dbpath: str
    '''
    def __init__(self, db_path):
        super(Connection, self).__init__()
        self.con = sqlite3.connect(db_path)

    def close(self):
        '''
        Closes the database connection, commiting all changes.
        '''
        if self.con:
            self.con.commit()
            self.con.close()

    # FOREIGN KEY STATUS
    def check_foreign_keys_status(self):
        '''
        Check if the foreign keys has been activated.

        :return: ``True`` if  foreign_keys is activated and ``False`` otherwise.
        :raises sqlite3.Error: when a sqlite3 error happen. In this case the
            connection is closed.
        '''
        try:
            # Create a cursor to receive the database values
            cur = self.con.cursor()
            # Execute the pragma command
            cur.execute('PRAGMA foreign_keys')
            # We know we retrieve just one record: use fetchone()
            data = cur.fetchone()
            is_activated = data == (1,)
            print("Foreign Keys status: %s" % 'ON' if is_activated else 'OFF')
        except sqlite3.Error as excp:
            print("Error %s:" % excp.args[0])
            self.close()
            raise excp
        return is_activated

    def set_foreign_keys_support(self):
        '''
        Activate the support for foreign keys.

        :return: ``True`` if operation succeed and ``False`` otherwise.
        '''
        keys_on = 'PRAGMA foreign_keys = ON'
        try:
            # Get the cursor object.
            # It allows to execute SQL code and traverse the result set
            cur = self.con.cursor()
            # execute the pragma command, ON
            cur.execute(keys_on)
            return True
        except sqlite3.Error as excp:
            print("Error %s:" % excp.args[0])
            return False

    def unset_foreign_keys_support(self):
        '''
        Deactivate the support for foreign keys.

        :return: ``True`` if operation succeed and ``False`` otherwise.
        '''
        keys_on = 'PRAGMA foreign_keys = OFF'
        try:
            # Get the cursor object.
            # It allows to execute SQL code and traverse the result set
            cur = self.con.cursor()
            # execute the pragma command, OFF
            cur.execute(keys_on)
            return True
        except sqlite3.Error as excp:
            print("Error %s:" % excp.args[0])
            return False

    # The API
    # Game table API
    def get_game(self, gameid):
        '''
        Extracts a game with given id from the database.

        :param int gameid: The id of the game.
        :return: A dictionary with the game data
            or None if game with the id does not exist.
        '''
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Create the SQL Query
        query = 'SELECT * FROM game WHERE id = ?'
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Execute main SQL Statement
        pvalue = (gameid,)
        cur.execute(query, pvalue)
        #Process the response.
        #Just one row is expected
        row = cur.fetchone()
        if row is None:
            return None
        #Build the return object
        return {'id': row['id'],
                'start_time': row['start_time'],
                'end_time': row['end_time'],
                'x_size': row['x_size'],
                'y_size': row['y_size'],
                'turn_length': row['turn_length']}

    def delete_game(self, gameid):
        '''
        Deletes a game with given id from the database.

        :param int gameid: The id of the game.
        :return: True if the game has been deleted, False otherwise.
        '''
        #Create the SQL Statement
        stmnt = 'DELETE FROM game WHERE id = ?'
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        pvalue = (gameid,)
        try:
            cur.execute(stmnt, pvalue)
            #Commit the message
            self.con.commit()
        except sqlite3.Error as e:
            print("Error %s:" % (e.args[0]))
        return bool(cur.rowcount)

    def create_game(self, x_size, y_size, turn_length):
        '''
        Creates a new game into the database. Id is autoincremented.

        :param int x_size: The desired number of columns on the board (or the 'ocean').
        :param int y_size; The desired number of rows on the board.
        :param int turn_size: The desired length of one turn in seconds.
        '''
        #Create the SQL Statement
        stmnt = 'INSERT INTO game (id, start_time, end_time, x_size, y_size, turn_length) \
                 VALUES (?, ?, ?, ?, ?, ?)'
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Generate the values for SQL statement
        start_time = str(datetime.today())
        pvalue = (None, start_time, '', x_size, y_size, turn_length)
        #Execute the statement
        cur.execute(stmnt, pvalue)
        self.con.commit()
        #Extract the game id
        id = cur.lastrowid
        #Return the game id
        return id if id is not None else None

    # Player table API
    def get_player(self, playerid):
        '''
        Extracts a player with given id from the database.

        :param int playerid: The id of the player.
        :return: A dictionary with the player data
            or None if player with given id does not exist.
        '''
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Create the SQL Query
        query = 'SELECT * FROM player WHERE id = ?'
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Execute main SQL Query
        pvalue = (playerid,)
        cur.execute(query, pvalue)
        #Process the response.
        #Just one row is expected
        row = cur.fetchone()
        if row is None:
            return None
        #Build the return object
        return {'id': row['id'],
                'nickname': row['nickname'],
                'game': row['game']}

    def delete_player(self, playerid):
        '''
        Deletes a player with given id from the database.

        :param int playerid: The id of the player.
        :return: True if the player has been deleted, False otherwise.
        '''
        #Create the SQL Statement
        stmnt = 'DELETE FROM player WHERE id = ?'
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        pvalue = (playerid,)
        try:
            cur.execute(stmnt, pvalue)
            #Commit the message
            self.con.commit()
        except sqlite3.Error as e:
            print("Error %s:" % (e.args[0]))
        return bool(cur.rowcount)

    def create_player(self, playerid, nickname, gameid):
        '''
        Creates a new player into the database.

        :param int playerid: The id of the player.
        :param string nickname; The nicknameo of the player.
        :param int gameid: The id of the game player is joining.
        '''
        #Create the SQL Statement
        stmnt = 'INSERT INTO player (id, nickname, game) \
                 VALUES (?, ?, ?)'
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Generate the values for SQL statement
        start_time = str(datetime.today())
        pvalue = (playerid, nickname, gameid)
        #Execute the statement
        cur.execute(stmnt, pvalue)
        self.con.commit()

    # Ship API
    def get_ship(self, shipid):
        '''
        Extracts a ship with given id from the database.

        :param int shipid: The id of the ship.
        :return: A dictionary with the ship data
            or None if ship with given id does not exist.
        '''
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Create the SQL Query
        query = 'SELECT * FROM ship WHERE id = ?'
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Execute main SQL Query
        pvalue = (shipid,)
        cur.execute(query, pvalue)
        #Process the response.
        #Just one row is expected
        row = cur.fetchone()
        if row is None:
            return None
        #Build the return object
        return {'shipid': row['id'],
                'player': row['player'],
                'game': row['game'],
                'stern_x': row['stern_x'],
                'stern_y': row['stern_y'],
                'bow_x': row['bow_x'],
                'bow_y': row['bow_y'],
                'ship_type': row['ship_type']}

    def delete_ship(self, shipid):
        '''
        Deletes a ship with given id from the database.

        :param int shipid: The id of the ship.
        :return: True if the ship has been deleted, False otherwise.
        '''
        #Create the SQL Statement
        stmnt = 'DELETE FROM ship WHERE id = ?'
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        pvalue = (shipid,)
        try:
            cur.execute(stmnt, pvalue)
            #Commit the message
            self.con.commit()
        except sqlite3.Error as e:
            print("Error %s:" % (e.args[0]))
        return bool(cur.rowcount)

    def create_ship(self, shipid, playerid, gameid, stern_x, stern_y, bow_x, bow_y, ship_type):
        '''
        Creates a new ship into the database.

        :param int shipid: The id of the ship.
        :param int player; The id of the player who owns the ship.
        :param int gameid: The id of the game ship belongs to.
        :param int stern_x: Ship stern's x-coordinate.
        :param int stern_y: Ship stern's y-coordinate.
        :param int bow_x: Ship bow's x-coordinate.
        :param int bow_y: Ship bow's y-coordinate.
        :param string ship_type: String to determine custom type of ship.
        '''
        #Create the SQL Statement
        stmnt = 'INSERT INTO ship (id, player, game, stern_x, stern_y, bow_x, bow_y, ship_type) \
                 VALUES (?, ?, ?, ?, ?, ?, ? ,?)'
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Generate the values for SQL statement
        pvalue = (shipid, playerid, gameid, stern_x, stern_x, bow_x, bow_y, ship_type)
        #Execute the statement
        cur.execute(stmnt, pvalue)
        self.con.commit()

    # Turn API
    def get_turn(self):
        '''
        What should we do with turns?
        Return all the turns of game,
        and/or all the turns of player?
        Individual turn?
        '''
        return "Not implemented"

    def create_turn(self, turn_number, playerid, gameid):
        '''
        Creates a new turn into a game.

        :param int turn_number: The number of the turn.
        :param int playerid; The id of the player who played the turn.
        :param int gameid: The id of the game turn was played in.
        '''
        #Create the SQL Statement
        stmnt = 'INSERT INTO turn (turn_number, player, game) \
                 VALUES (?, ?, ?)'
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Generate the values for SQL statement
        start_time = str(datetime.today())
        pvalue = (turn_number, playerid, gameid)
        #Execute the statement
        cur.execute(stmnt, pvalue)
        self.con.commit()

    # Shot API
    def get_shot(self):
        '''
        '''
        return "Not implemented"

    def create_shot(self, turnid, playerid, gameid, x, y, shot_type):
        '''
        Creates a new shot into a game.

        :param int turnid: The number of the turn shot was fired.
        :param int playerid; The id of the player who fired the shot.
        :param int gameid: The id of the game turn shot was fired in.
        :param int x: The x-coordinate of the shot.
        :param int y: The y-coordinate of the shot.
        :param shot_type: Customizable type of the shot (e.g. single or area-of-effect).
        '''
        #Create the SQL Statement
        stmnt = 'INSERT INTO shot (turn, player, game, x, y, shot_type) \
                 VALUES (?, ?, ?, ?, ?, ?)'
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Generate the values for SQL statement
        pvalue = (turnid, playerid, gameid, x, y, shot_type)
        #Execute the statement
        cur.execute(stmnt, pvalue)
        self.con.commit()
