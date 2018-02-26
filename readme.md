# BattleShip

## Description

Battleships Web API offers an interface to create varied versions of battleships games. The API provides core components for a battleship game: placement of ships, entry for players, firing of shots and evaluation of the game state. In addition, the API keeps logs and saves the history of all played games.

The API can be called for an instance of a battleships game. Ship data, e.g. their coordinates, are also retained in the instance. The instance takes shots as input through the API and keeps track of which coordinates have been hit. With this data, the API can calculate and return the current state of a game instance. Players fire shots until only one player remains alive and the game ends. After one instance of a game has ended, its logs are stored in the game history. The game history can also be accessed to see all the moves made, and who won the game.

There are many previous implementations for battleships games, but creating a Web API enables clients to implement their own games with varying designs and rulesets. This is useful as currently there is a knowledge gap in determining the optimal designs for battleships games. With Battleships Web API, different combinations of designs and rules can be evaluated with less effort, accelerating the innovation of this beloved game. The API can also be used to develop machine learning in the context of battleships games. In addition, game history provides data for statistical analysis regarding tactics and player behaviour in battleships games. And ofcourse, one of the main usages of this API is to have fun with your friends.

## Depencies

There are no other than standard Python modules used. Project have been tested to work with Python 3.5 and Python 3.6

## Setup and populate database

Creating database schema is done by calling *create_tables()* from battlsehip.database.Engine*

When function is called without argument function creates database with test schema *db/battleship_schema_dump.sql*

Populating database is done by calling *populate_tables()* from *battleship.database.Engine*

When function is called without argument function populates database with test data *db/battleship_data_dump.sql*

## Tests

Unit tests are implemented for each component of API, and they can be found under *tests* folder 

To run all tests:
```
py -m unittest discover -s "tests" -p "database_api_tests*"
```