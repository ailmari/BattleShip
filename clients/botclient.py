import requests
import sys


def create_game(host, games_url):
    '''
    Starts from API endpoint Games.
    Follows link-relations to create a game.
    Returns URL to the created game.
    '''

    # Get information how to create a game.
    try:
        response = requests.get(games_url)
    except Exception as e:
        print(e)
        return None

    if response.status_code == 200:
        data = response.json()
        create_game_uri = data['@controls']['create-game']['href']
        create_game_schema = data['@controls']['create-game']['schema']
    else:
        print(response.status_code)
        return None

    # Create a game.
    try:
        create_game_url = '{}{}'.format(host, create_game_uri)
        body = create_game_schema
        body['x_size'] = 3
        body['y_size'] = 3
        body['turn_length'] = 1
        response = requests.post(create_game_url, json=body)
    except Exception as e:
        print(e)
        return None

    if response.status_code == 201:
        game_url = response.headers['Location']
        return game_url
    else:
        print(response.status_code)
        return None

def join_game(host, game_url, nickname):
    '''
    Starts from endpoint for a Game.
    Follows link-relations to create a new player.
    Returns URL to the player.
    '''

    # Get information how to join a game.
    try:
        response = requests.get(game_url)
    except Exception as e:
        print(e)
        return None

    if response.status_code == 200:
        data = response.json()
        players_uri = data['@controls']['players']['href']
    else:
        print(response.status_code)
        return None

    try:
        players_url = '{}{}'.format(host, players_uri)
        response = requests.get(players_url)
    except Exception as e:
        print(e)
        return None

    if response.status_code == 200:
        data = response.json()
        create_player_uri = data['@controls']['create-player']['href']
        create_player_schema = data['@controls']['create-player']['schema']
    else:
        print(response.status_code)
        return None

    # Create player.
    try:
        create_player_url = '{}{}'.format(host, create_player_uri)
        body = create_player_schema
        body['nickname'] = nickname
        response = requests.post(create_player_url, json=body)
    except Exception as e:
        print(e)
        return None

    if response.status_code == 201:
        player_url = response.headers['Location']
        return player_url
    else:
        print(response.status_code)
        return None

def create_ships(host, game_url, player_url):
    '''
    Starts from endpoint for a Player.
    Follows link-relations to create ships.
    Returns URL to the ships.
    '''

    # Get player id.
    try:
        response = requests.get(player_url)
    except Exception as e:
        print(e)
        return None
    if response.status_code == 200:
        data = response.json()
        playerid = data['id']
    else:
        print(response.status_code)
        return None

    # Get information how to create ships.
    try:
        response = requests.get(game_url)
    except Exception as e:
        print(e)
        return None
    if response.status_code == 200:
        data = response.json()
        ships_uri = data['@controls']['ships']['href']
        place_ships_uri = data['@controls']['place-ship']['href']
        place_ships_schema = data['@controls']['place-ship']['schema']
    else:
        print(response.status_code)
        return None

    # Place ship.
    try:
        place_ships_url = '{}{}'.format(host, place_ships_uri)
        body = place_ships_schema
        body['playerid'] = playerid
        body['stern_x'] = 3
        body['stern_y'] = 3
        body['bow_x'] = 3
        body['bow_y'] = 3
        body['ship_type'] = 'frigate'
        response = requests.post(place_ships_url, json=body)
    except Exception as e:
        print(e)
        return None
    if response.status_code == 204:
        ships_url = '{}{}'.format(host, ships_uri)
        return ships_url
    else:
        print(response.status_code)
        return None

def fire(host, game_url, player_url):
    '''
    Starts from endpoint for a Game.
    Follows link-relations to fire a shot.
    Returns URL to the Game's shots.
    '''

    # Get information how to fire shots.
    try:
        response = requests.get(game_url)
    except Exception as e:
        print(e)
        return None

    if response.status_code == 200:
        data = response.json()
        shots_uri = data['@controls']['shots']['href']
        fire_shots_uri = data['@controls']['fire-shot']['href']
        fire_shots_schema = data['@controls']['fire-shot']['schema']
    else:
        print(response.status_code)
        return None

    # Get information who is firing.
    try:
        response = requests.get(player_url)
    except Exception as e:
        print(e)
        return None

    if response.status_code == 200:
        data = response.json()
        playerid = data['id']
        player_nickname = data['nickname']
    else:
        print(response.status_code)
        return None

    # Fire a shot.
    try:
        fire_shots_url = '{}{}'.format(host, fire_shots_uri)
        body = fire_shots_schema
        body['playerid'] = playerid
        body['x'] = 3
        body['y'] = 3
        body['shot_type'] = 'single'
        response = requests.post(fire_shots_url, json=body)
    except Exception as e:
        print(e)

    if response.status_code == 204:
        print('{} fired a shot!'.format(player_nickname))
        shots_url = '{}{}'.format(host, shots_uri)
        return shots_url
    else:
        print(response.status_code)
        return None

def all_ships_destroyed(host, shots_url, ships_url, player_url):
    '''
    Get all shots and ships.
    Check if all ships have been shot.
    Return True if yes, False if no.
    '''

    # Get player id.
    try:
        response = requests.get(player_url)
    except Exception as e:
        print(e)
        return None
    if response.status_code == 200:
        data = response.json()
        playerid = data['id']
    else:
        print(response.status_code)
        return None

    # Get ships.
    try:
        response = requests.get(ships_url)
    except Exception as e:
        print(e)
        sys.exit(0)
    if response.status_code == 200:
        data = response.json()
        ships = data['items']
    else:
        print(response.status_code)
        sys.exit(0)

    # Get shots.
    try:
        response = requests.get(shots_url)
    except Exception as e:
        print(e)
        sys.exit(0)
    if response.status_code == 200:
        data = response.json()
        shots = data['items']
    else:
        print(response.status_code)
        sys.exit(0)

    # Compare ships and shots.
    player_shots = []
    for shot in shots:
        if shot['player'] == playerid:
            player_shots.append(shot)

    other_ships = []
    for ship in ships:
        if ship['player'] != playerid:
            other_ships.append(ship)

    whatever = True
    if whatever:
        return True
    else:
        return False

def end_game(host, game_url):
    '''
    Ends the game.
    '''

    try:
        response = requests.patch(game_url)
    except Exception as e:
        print(e)
        sys.exit(0)
    if response.status_code == 204:
        return True
    else:
        return False


if __name__ == '__main__':
    host = 'http://localhost:5000'
    games_uri = '/battleship/api/games/'

    print('Creating a new game...')
    games_url = '{}{}'.format(host, games_uri)
    game_url = create_game(host, games_url)
    if game_url is None:
        print('Failed to create a game!')
        sys.exit(0)

    print('Creating bots...')
    bot1_url = join_game(host, game_url, 'Boten Ett')
    bot2_url = join_game(host, game_url, 'Boten Två')
    if bot1_url is None or bot2_url is None:
        print('Failed to create bots!')
        sys.exit(0)

    print('Placing ships...')
    ships_url = create_ships(host, game_url, bot1_url)
    ships_url = create_ships(host, game_url, bot2_url)
    if ships_url is None:
        print('Failed to place ships!')
        sys.exit(0)

    shots_url = fire(host, game_url, bot1_url)
    shots_url = fire(host, game_url, bot2_url)

    if all_ships_destroyed(host, shots_url, ships_url, bot1_url):
        if end_game(host, game_url):
            print('Somebody won wohoo!')
