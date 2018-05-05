'''
This file is for different HTTP requests,
that can be used to access the server.
'''

import requests


def enter_games(url):
    response = requests.get('{0}/battleship/api/games/'.format(url))
    return response


def search_games(url):
    response = enter_games(url)
    if response.status_code != 200:
        return
    games = response.json().get('items')
    output = list()
    for game in games:
        info = use_link('self', game.get('@controls'), url)
        output.append(info.json())
    return output


def use_link(link_name, controls, url, kwargs={}):
    link = controls.get(link_name)
    if link is None:
        raise ValueError('Could not find link: "', link, '" from controls!')
    href = link.get('href')
    link_url = '{0}{1}'.format(url, href)
    method = link.get('method', 'GET')  # Default to GET
    response = requests.request(method, link_url, **kwargs)
    return response
