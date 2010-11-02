#!/usr/bin/env python
# Cli-twi
# Copyright (C) 2010 Honza Pokorny <me@honza.ca>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import simplejson as json
from oauth import oauth
from oauthtwitter import OAuthApi
import config

__version__ = '1.0'


class CliTwi:

    consumer_key = config.consumer_key
    consumer_secret = config.consumer_secret
    cli_twi_path = os.path.expanduser('~') + '/.clitwi'

    token = None
    secret = None

    latest = 0
    mention_latest = 0

    config_ok = False

    def __init__(self):
        os.chdir(self.cli_twi_path)
        # Figure out the action
        self.read_action()
        # Verify we have all of the necessary config files
        self.check_config()
        self.read_config()
        # And the power button...
        self.run()

    def read_action(self):
        l = len(sys.argv)
        if l == 1:
            self.action = 'list'
        elif l == 2:
            arg = sys.argv[1]
            if arg == 'setup':
                self.action = 'setup'
            elif arg == '-m':
                self.action = 'mentions'
            elif arg == '--help':
                self.action = 'help'
            else:
                self.action = 'update'

    def check_config(self):
        # _config, _latest, _mention_latest
        self.config_ok = True
        if not os.path.isfile('_config'):
            print 'Missing _config'
            self.config_ok = False
        if not os.path.isfile('_latest'):
            print 'Missing _latest'
            self.config_ok = False
        if not os.path.isfile('_mention_latest'):
            print 'Missing _mention_latest'
            self.config_ok = False

    def read_config(self):
        if self.action == 'setup' or self.action == 'help':
            return
        if not self.config_ok:
            return
        # Read the config files
        l = open('_latest', 'r')
        v = l.readline()
        self.latest = str(v)
        l.close()

        m = open('_mention_latest', 'r')
        v = m.readline()
        self.mention_latest = str(v)
        m.close()

        c = open('_config', 'r')
        v = c.readline()
        j = json.loads(v)
        self.token = j['token']
        self.secret = j['secret']
        c.close()

    def setup(self):
        os.system('clear')

        twitter = OAuthApi(self.consumer_key, self.consumer_secret)

        # Get the temporary credentials for our next few calls
        temp_credentials = twitter.getRequestToken()

        # User pastes this into their browser to bring back a pin number
        print(twitter.getAuthorizationURL(temp_credentials))

        # Get the pin # from the user and get our permanent credentials
        oauth_verifier = raw_input('What is the PIN? ')
        access_token = twitter.getAccessToken(temp_credentials, oauth_verifier)

        self.token = access_token['oauth_token']
        self.secret = access_token['oauth_token_secret']

        f = open(os.getcwd() + '/_config', 'w')
        d = "{ \"token\": \"%s\", \"secret\": \"%s\" }" % (
                self.token, self.secret)
        f.write(d)
        f.close()

        self.write_latest(1)
        self.write_latest(1, 'mentions')

        print 'Clitwi was successfully set up.'

    def setup_api(self):
        self.twitter = OAuthApi(self.consumer_key,
                self.consumer_secret,
                self.token,
                self.secret)

    def list_tweets(self, type='default'):
        os.system('clear')
        if type == 'default':
            user_timeline = self.twitter.GetHomeTimeline(
                {'since_id': self.latest})
        else:
            user_timeline = self.twitter.GetMentions(
                {'since_id': self.mention_latest})
        if user_timeline == []:
            print 'No new tweets.'
            return
        mle = False
        for tweet in user_timeline:
            print '\033[94m' + tweet['user']['screen_name'] + '\033[0m' + ':'
            self.print_text(tweet['text'])
            if not mle:
                if type == 'default':
                    self.write_latest(tweet['id'])
                else:
                    self.write_latest(tweet['id'], 'mention')
                mle = True

    def write_latest(self, id, type='default'):
        if type == 'default':
            f = open('_latest', 'w')
        else:
            f = open('_mention_latest', 'w')
        f.write(str(id))
        f.close()

    def print_text(self, text):
        l = len(text)
        if l > 77:
            print '  ' + text[:77]
            print '  ' + text[77:]
        else:
            print '  ' + text

    def send_tweet(self):
        tweet = sys.argv[1]
        if len(tweet) > 140:
            print 'Too long'
            sys.exit(1)
            return
        else:
            update = self.twitter.UpdateStatus(str(tweet))
            print 'Sent!'

    def show_help(self):
        print 'Cli Twi - version %s' % __version__
        print 'main.py [options]'
        print 'main.py - will print latest tweets'
        print 'main.py "Some message" - will update your status'
        print 'main.py -m - will print latest mentions'
        print 'main.py setup - will run the OAuth process'
        print 'main.py --help - will display this help'

    def run(self):
        # Actions that don't require any config (help, setup)
        if self.action == 'setup':
            self.setup()
        elif self.action == 'help':
            self.show_help()
        # Check if we have correct config settings
        if not self.config_ok:
            return
        self.setup_api()
        if self.action == 'list':
            self.list_tweets()
        elif self.action == 'update':
            self.send_tweet()
        elif self.action == 'mentions':
            self.list_tweets('mentions')

if __name__ == "__main__":
    twitter = CliTwi()
