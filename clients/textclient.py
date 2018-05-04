'''
This is a text based client for the battleship.
It is designed to be extremely simple.
'''

import requests
from logic import Ship, ship_squares
from random import randint, choice
from itertools import chain
from collections import namedtuple


StartingShip = namedtuple('StartingShip', ['length', 'type'])


def ask_for_number(question):
    while True:
        input_ = input(question)
        try:
            input_ = int(input_)
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
    def __init__(self, starting_ships, url):
        '''
        starting_ships should be a list of ships.
        Ships need a length and a type variables.
        '''
        self.games = list()
        self.map_size = (10, 10)
        self.starting_ships = starting_ships
        self.nickname = ""
        self.url = url

    def main(self):
        print('Welcome to text based Battleship client!')
        while True:
            print('\nMAIN MENU')
            print('1) Find game')
            print('2) Create game')
            print('3)exit')
            selection = ask_for_number('>')
            if selection == 1:
                self.find_game()
            elif selection == 2:
                print('Create game WIP')
            elif selection == 3:
                print('bye bye')
                return
            else:
                print('Invalid input:', selection)

    def find_game(self):
        print('\nFIND GAME')
        while True:
            print('Searching...')
            games = self._search_games()
            if not games:
                print('No games found')
                print('1) Retry')
                print('2) Quit')
                selection = ask_for_number('>')
                if selection == 1:
                    continue
                else:
                    return
            else:
                self.games = games
                break

        print('Found games!')
        for game in self.games:
            print(game)
        print('Select game')
        while True:
            selection = ask_for_number('>')
            if selection in games:
                self.join_game(selection)
                return
            else:
                print('Choose a game ID')

    def _search_games(self):
        '''
        Search for games from the server.
        Return a list of games.
        '''
        try:
            response = requests.get('{0}/battleship/api/games/'.format(self.url))
        except Exception as e:
            print('Error while searching for games:', e)
            return []
        if response.status_code == 200:
            games = [i.get('id') for i in response.json().get('items')]
            return games
        else:
            print('Could not get games.')
            print(response.text)
            return []

    def join_game(self, selection):
        '''
        Join the selected game.
        '''
        print('Select nickname, or leave empty for default nickname.')
        self.nickname = input().strip()
        while True:
            print('Trying to join game:', selection)
            self.joined = self._join(selection)
            if self.joined:
                break
            else:
                print('Joining failed')
                print('1) Retry')
                print('2) Quit')
                selection = ask_for_number('>')
                if selection == 1:
                    continue
                else:
                    return

        print('Joined the game!')
        self.play_game()

    def _join(self, selection):
        '''
        Join the selected game with current nickname,
        and randomize the starting ships.
        return True if success, else False
        '''
        # Try joining as a new player

        # Send randomized ships to the server
        ships = randomize_ships(self.map_size, self.starting_ships)
        return True

    def play_game(self):
        '''
        Handle the gameplay here.
        The players first choose where to shoot,
        and the shot is sent to server.
        Between shots, data is fetched from the server to display the map.
        '''
        pass

if __name__ == '__main__':
    # Just quick test ships
    starting_ships = [StartingShip(5, "a"), StartingShip(7, "b")]
    URL = 'http://localhost:5000'
    client = TextClient(starting_ships, URL)
    client.main()
