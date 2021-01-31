__author__ = 'nahla.errakik'

import os
import sqlite3
import requests
import configparser

from pathlib import Path
from datetime import datetime
from http import HTTPStatus


class Twitter:
    def __init__(self, config):
        self._token_url = 'https://api.twitter.com/oauth2/token'
        self._server = 'https://api.twitter.com/1.1/'
        self._key = config['key']
        self._secret = config['secret']

    def __get_token__(self):
        res = requests.post(self._token_url,
                            auth=(self._key, self._secret),
                            data={'grant_type': 'client_credentials'},
                            verify=False)

        self.token = res.json()['access_token']

        self.headers = {'Accept': 'application/json',
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer ' + self.token}

    def search_tweets(self, q):
        self.__get_token__()
        url = '{server}search/tweets.json?q={q}'.format(server=self._server, q=q)
        response = requests.get(url, headers=self.headers, verify=False)
        if response.status_code != HTTPStatus.OK:
            raise Exception('Error while calling external service')

        self.json = response.json()
        response = self.json
        return response
