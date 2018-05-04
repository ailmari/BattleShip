'''
A quick example on how randomize_ships works.
'''

from logic import draw_map
from textclient import randomize_ships, StartingShip


if __name__ == '__main__':
    starting_ships = [StartingShip(5, "a"), StartingShip(7, "b")]
    rs = randomize_ships((10, 10), starting_ships)
    print(rs)
    draw_map(10, 10, [], rs)
