'''
This is a text based client for the battleship.
It is designed to be extremely simple.
'''

from logic import ship_in_xy, Ship, ship_squares, draw_map
from random import randint, choice
from itertools import chain
from collections import namedtuple


def ask_for_number(question):
    while True:
        input_ = input(question)
        try:
            input_ = float(input_)
        except ValueError:
            print("Not a valid input!")
            continue
        return input_


def randomize_ships(map_size, starting_ships):
    '''
    Return a list of randomized ships
    '''
    ships = list()
    for ship in starting_ships:
        while True:
            width = map_size[0] - 1
            length = map_size[1] - 1
            sq = (randint(0, width), randint(0, length))
            direction = choice(['up', 'down', 'left', 'right'])
            new_ship = ship_to_direction(sq, ship.length, direction, ship.type)
            squares = ship_squares(new_ship)
            ship_within_map = all((xy_in_map(xy, map_size) for xy in squares))
            if not ship_within_map:
                continue
            other_ship_squares = [ship_squares(ship) for ship in ships]
            collision = any([s in chain(*other_ship_squares) for s in squares])
            if not collision:
                ships.append(new_ship)
                break
    return ships


def ship_to_direction(start, length, direction, type):
    x, y = start
    if direction == 'up':
        bow = (x, y - length + 1)
    elif direction == 'down':
        bow = (x, y + length - 1)
    elif direction == 'left':
        bow = (x - length + 1, y)
    elif direction == 'right':
        bow = (x + length - 1, y)
    else:
        raise ValueError('Got wrong direction', direction)
    return Ship(start, bow, type)


def xy_in_map(xy, map_size):
    '''
    Return True if xy is in map, else False.

    Inputs are both tuples with two numbers.
    xy has (x,y) coordinates.
    map_size has (x, y) width and length.

    0 is considered to be part of the map.
    So a (10, 10) map would contain (0-9, 0-9)
    '''
    mx, my = map_size
    x, y, = xy
    return (0 <= x < mx) and (0 <= y < my)


class TextClient():
    '''
    The client class
    '''
    def __init__(self, starting_ships):
        '''
        starting_ships should be a list of ships.
        Ships need a length and a type variables.
        '''
        self.games = list()
        self.map_size = (10, 10)
        self.starting_ships = starting_ships

    def main(self):
        print('Welcome to text based Battleship client!')
        print('select what do to:')
        print('1) Find game')
        print('2) Create game')
        print('3)exit')
        selection = ask_for_number('>')
        if selection == 1:
            pass  # do something
        return

    def find_game(self):
        print('Find game...')
        self._search_games()
        for game in self.games:
            print(game)
        print('Select game:')
        while True:
            selection = ask_for_number('>')
            if selection in [g.id for g in self.games]:
                self.join_game(selection)
                return
            else:
                print('Choose a game ID')

    def _search_games(self):
        '''
        Search for games from the server.
        Save games to variable games.
        '''
        pass  # HTTP METHOD FOR FINDING GAMES HERE!

    def join_game(self, selection):
        '''
        Join the selected game.
        '''
        self.joined = self._join(selection)
        if self.joined:
            pass
        else:
            print('Cannot join game', selection)

    def _join(self, selection):
        '''
        Handle the HTTP connection here.
        return True if success, else False
        '''
        # ADD NETWORK LOGIC HERE!
        ships = self._randomize_ships(self.map_size, self.starting_ships)
        # TODO: send selected ships to the server
        return True


if __name__ == '__main__':
    ship = namedtuple('Ship', ['length', 'type'])
    starting_ships = [ship(5, "a"), ship(7, "b")]
    #client = TextClient(starting_ships)
    #client.main()
    rs = randomize_ships((10, 10), starting_ships)
    print(rs)
    draw_map(10, 10, [], rs)
