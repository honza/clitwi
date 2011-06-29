#!/usr/bin/env python
# Cli-twi
# Copyright (C) 2011 Honza Pokorny <me@honza.ca>

import os
import sys
import json
from oauthtwitter import OAuthApi
import config

__version__ = '1.3'


class CliTwi(object):

    consumer_key = config.consumer_key
    consumer_secret = config.consumer_secret
    cli_twi_path = os.path.expanduser('~') + '/.clitwi'

    token = None
    secret = None

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
        self.config_ok = True
        if not os.path.isfile('_config'):
            print 'Missing _config'
            self.config_ok = False

    def read_config(self):
        if self.action == 'setup' or self.action == 'help':
            return
        if not self.config_ok:
            return
        # Read the config file
        file = open('_config', 'r')
        v = file.read()
        config = json.loads(v)
        file.close()

        self.latest = config['latest']
        self.mention = config['mention']
        self.token = config['token']
        self.secret = config['secret']

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

        self.latest = 1
        self.mention = 1

        print 'Clitwi was successfully set up.'

    def setup_api(self):
        self.twitter = OAuthApi(self.consumer_key,
                self.consumer_secret,
                self.token,
                self.secret)

    def list_tweets(self, type='default'):
        os.system('clear')
        if type == 'default':
            user_timeline = self.twitter.GetHomeTimeline({
                'since_id': self.latest
            })
        else:
            user_timeline = self.twitter.GetMentions({
                'since_id': self.mention
            })
        if user_timeline == []:
            print 'No new tweets.'
            return
        first = True
        for tweet in user_timeline:
            print tweet['user']['screen_name'] + ':'
            self.print_text(tweet['text'])
            if first:
                if type == 'default':
                    self.latest = tweet['id']
                else:
                    self.mention = tweet['id']
                first = False

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
            self.twitter.UpdateStatus(str(tweet))
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

    def finish(self):
        d = {
            'token': self.token,
            'secret': self.secret,
            'latest': self.latest,
            'mention': self.mention
        }
        f = open(os.getcwd() + '/_config', 'w')
        f.write(json.dumps(d))
        f.close()


if __name__ == "__main__":
    twitter = CliTwi()
    twitter.finish()
