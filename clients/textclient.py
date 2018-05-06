'''
This is a text based client for the battleship.
It is designed to be extremely simple.
'''

from pprint import pprint
import requests
from logic import Ship, ship_squares, draw_map
from hyperlink_controls import enter_games, search_games, use_link
from random import randint, choice
from itertools import chain
from collections import namedtuple


StartingShip = namedtuple('StartingShip', ['length', 'type'])


def ship_as_dict(ship):
    '''
    Convert namedtuple Ship items into correct from,
    so that they can be sent to the server.
    '''
    correct_ship = dict()
    correct_ship['stern_x'] = ship.stern[0]
    correct_ship['stern_y'] = ship.stern[1]
    correct_ship['bow_x'] = ship.bow[0]
    correct_ship['bow_y'] = ship.bow[1]
    correct_ship['ship_type'] = ship.type
    return correct_ship


def as_ship(ship_dict):
    '''
    Convert the server response into a Ship namedtuple.
    '''
    stern = (ship_dict['stern_x'], ship_dict['stern_y'])
    bow = (ship_dict['bow_x'], ship_dict['bow_y'])
    _type = ship_dict['ship_type']
    ship = Ship(stern, bow, _type)
    return ship


def ask_for_number(question):
    while True:
        input_ = input(question)
        try:
            input_ = int(input_)
        except ValueError:
            print("Not a valid input!")
            continue
        return abs(input_)


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
        self.game = None
        self.gameid = None
        self.player = None
        self.playerid = None
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
                break

        print('Found games!')
        for number, game in enumerate(games):
            print(number+1)
            info = {k: i for k, i in game.items() if k[0] != '@'}
            for key, value in info.items():
                print('\t{0}: {1}'.format(key, value))
        print('Select game')
        while True:
            selection = ask_for_number('>')
            try:
                game = games[selection-1]
            except IndexError:
                print('Choose a game from the list.')
                continue
            self.join_game(game)
            return

    def _search_games(self):
        '''
        Search for games from the server.
        Return a list of games.
        '''
        try:
            games = search_games(self.url)
        except Exception as e:
            print('Error while searching for games:', e)
            return []
        return games

    def join_game(self, game):
        '''
        Join the selected game.
        '''
        print('Select nickname, or leave empty for default nickname.')
        self.nickname = input('>').strip()
        while True:
            print('Trying to join...')
            player = self._join(game)
            if player:
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
        self.game = game
        self.player = player
        self.play_game(game, player)

    def _join(self, game):
        '''
        Join the selected game with current nickname,
        and randomize the starting ships.
        return True if success, else False
        '''
        # Try joining as a new player
        try:
            players = use_link('players', game.get('@controls'), self.url)
            creation_response = use_link(
                link_name='create-player',
                controls=players.json().get('@controls'),
                url=self.url,
                kwargs={'json': {'nickname': self.nickname}}
            )
        except Exception as e:
            print('Error while sending Post request:', e)
            return False
        if creation_response.status_code != 201:
            print('Player creation error!')
            print('status code', creation_response.status_code)
            print(creation_response.text)
            return False

        # Send randomized ships to the server
        player_url = creation_response.headers.get('Location')
        response = requests.get(player_url)
        player = response.json()
        map_size = (int(game.get('x_size')), int(game.get('y_size')))
        ships = randomize_ships(map_size, self.starting_ships)
        try:
            for ship in ships:
                json_args = ship_as_dict(ship)
                json_args['playerid'] = player.get('id')
                response = use_link(
                    'place-ship',
                    player.get('@controls'),
                    self.url,
                    kwargs={'json': json_args},
                )
                if response.status_code != 204:
                    print('Ship creation error!')
                    print('Status code', response.status_code)
                    print(response.text)
                    return False
        except Exception as e:
            print('Error while sending Post request:', e)
            return False

        self.playerid = player.get('id')
        return player

    def play_game(self, game, player):
        '''
        Handle the gameplay here.
        The players first choose where to shoot,
        and the shot is sent to server.
        Between shots, data is fetched from the server to display the map.
        '''
        print('PLAYER')
        pprint(player)
        print('GAME')
        pprint(game)
        while True:
            # 1) Update Map
            hostile_shots = self._get_hostile_shots()
            my_ships = self._get_my_ships()
            print('HOSTILE SHOTS')
            pprint(hostile_shots)
            print('MY SHIPS')
            pprint(my_ships)

            # Conversions to fir draw_map
            shots_xy = [(shot['x'], shot['y']) for shot in hostile_shots]
            my_ships_as_ship = [as_ship(ship) for ship in my_ships]
            draw_map(
                width=game.get('x_size'),
                length=game.get('y_size'),
                shots=shots_xy,
                ships=my_ships_as_ship,
            )
            # 2) Shoot
            x, y = self._ask_for_coordinate()
            print('Shooting at:', (x, y))
            # 3) Check end state

    def _get_shots(self):
        '''
        Get shots of a game.
        '''
        if self.game is None:
            print('No game in memory')
            return False
        try:
            response = use_link('shots', self.game.get('@controls'), self.url)
        except Exception as e:
            print('Error while getting shots:', e)
            return list()
        if response.status_code != (200):
            print('get shot error!')
            print('status code', response.status_code)
            print(response.text)
            return list()
        return response.json()

    def _get_hostile_shots(self):
        '''
        '''
        response = self._get_shots()
        if not response:
            return False
        shots = response.get('items')
        hostile_shots = list()
        for shot in shots:
            if shot.get('player') != self.playerid:
                hostile_shots.append(shot)
        return hostile_shots

    def _get_ships(self):
        '''
        Get ships of a game made by player.
        Default to the current ones in memory.
        '''
        if self.game is None:
            print('No game in memory')
            return False
        try:
            response = use_link(
                link_name='ships',
                controls=self.game.get('@controls'),
                url=self.url,
            )
        except Exception as e:
            print('Error while getting ships:', e)
            return list()
        if response.status_code != 200:
            print('get ship error!')
            print('status code', response.status_code)
            print(response.text)
            return list()
        return response.json()

    def _get_my_ships(self):
        '''
        '''
        ships_response = self._get_ships()
        if not ships_response:
            return False
        ships = ships_response.get('items')
        my_ships = list()
        for ship in ships:
            if ship.get('player') == self.playerid:
                my_ships.append(ship)
        return my_ships

    def _ask_for_coordinate(self):
        '''
        Ask for a proper coordinates to shoot at.
        Returns x and y coordinates as a (x, y) tuple.
        '''
        print('Fire at Letter-Number coordinates (e.g. e5)')
        while True:
            target = input('>').strip()
            if len(target) < 2:
                print('Improper coordinates, try again!')
                continue
            y, x = target[0], target[1:]  # letter is y, number is x
            if not y.isalpha():
                print('First character must be a letter!')
                continue
            if not x.isdigit():
                print('Second character(s) must be a number!')
                continue
            map_x = int(self.game.get('x_size'))
            if not 0 <= int(x) < map_x:
                print('Number must be 0 <= x < {}!'.format(map_x))
                continue
            y_number = ord(y.capitalize()) - 65  # ord('A') starts at 65
            map_y = int(self.game.get('y_size'))
            if not 0 <= y_number < map_y:
                y_letter = chr(64+map_y)
                print('Letter must be A-{}!'.format(y_letter))
                continue
            return int(x), y_number


if __name__ == '__main__':
    # Just quick test ships
    starting_ships = [StartingShip(5, "a"), StartingShip(7, "b")]
    URL = 'http://localhost:5000'
    client = TextClient(starting_ships, URL)
    client.main()
