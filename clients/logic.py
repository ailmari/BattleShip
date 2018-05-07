from collections import namedtuple

Ship = namedtuple("Ship", ["stern", "bow", "type"])


def ship_stern_bow_xy(ship):
    sx, sy = ship.stern
    bx, by = ship.bow
    return sx, sy, bx, by


def smaller_bigger_xy(ship):
    sx, sy, bx, by = ship_stern_bow_xy(ship)
    bigger_x = sx if sx > bx else bx
    smaller_x = sx if sx < bx else bx
    bigger_y = sy if sy > by else by
    smaller_y = sy if sy < by else by
    return smaller_x, bigger_x, smaller_y, bigger_y


def ship_in_xy(ship, x, y):
    sx, sy, bx, by = ship_stern_bow_xy(ship)
    smaller_x, bigger_x, smaller_y, bigger_y = smaller_bigger_xy(ship)
    return (smaller_x <= x <= bigger_x) and (smaller_y <= y <= bigger_y)


def ship_squares(ship):
    smaller_x, bigger_x, smaller_y, bigger_y = smaller_bigger_xy(ship)
    squares = list()
    for x in range(smaller_x, bigger_x + 1):
        for y in range(smaller_y, bigger_y + 1):
            squares.append((x, y))
    return squares


def all_ships_sunk(ships, shots):
    '''
    Return True if all ships in the list have been sunk by shots.
    Otherwise, return False.
    shots should be a list with (x, y), where x and y are int.
    '''
    squares = list()
    for ship in ships:
        squares.extend(ship_squares(ship))
    squares_left = set(squares) - set(shots)
    if squares_left:
        return False
    else:
        return True


def draw_map(width, length, shots, ships, drawships=True):
    print(" " + "".join([str(x) for x in range(width)]))
    for y in range(length):
        line = ""
        for x in range(width):
            square = "o" if (x, y) in shots else "."
            for ship in ships:
                if ship_in_xy(ship, x, y) and drawships:
                    square = 'X' if (x, y) in shots else ship.type[0]
                elif ship_in_xy(ship, x, y) and not drawships:
                    square = 'X' if (x, y) in shots else "."
            line += square
        print("{0}{1}".format(chr(ord("A")+y), line))


def map_coord(x, y):
    return ("{0}{1}".format(chr(ord("A")+y), x))


def map_coords(xy_list):
    return [map_coord(*xy) for xy in xy_list]


def test1():
    cruiser = Ship((1, 0), (1, 3), "c")
    ships = [cruiser, ]
    shots = [(0, 0), (1, 0), (1, 1), (1, 2), (1, 3)]
    draw_map(10, 10, shots, ships)
    print('Cruiser squares:', map_coords(ship_squares(cruiser)))
    print('Shots:', map_coords(shots))
    print('Ships sunk:', all_ships_sunk(ships, shots))


if __name__ == '__main__':
    test1()
