from fabric.api import task
from fabric.contrib import django

import json
import os
import tweepy

# django setup
django.settings_module('factcheck.settings')
import django
django.setup()
from annotations.models import Claim, Author

def authenticate():
    auth = tweepy.OAuthHandler(
        os.environ['FACTCHECKDB_TWITTER_CONSUMER_KEY'], 
        os.environ['FACTCHECKDB_TWITTER_CONSUMER_SECRET']
    )
    auth.set_access_token(
        os.environ['FACTCHECKDB_TWITTER_ACCESS_KEY'], 
        os.environ['FACTCHECKDB_TWITTER_ACCESS_SECRET']
    )

    api = tweepy.API(auth)
    return api


@task
def get_trump_tweets():
    api = authenticate()

    for status in tweepy.Cursor(
        api.user_timeline, 
        screen_name='realDonaldTrump',
        trim_user=True
    ).items():
        claim = Claim(
            claim_text=status.text,
            claim_type='twitter',
            claim_date=status.created_at,
            claim_source='http://twitter.com/realDonaldTrump/{0}'.format(status.id)
        )
        claim.save()

@task
def create_authors():
    with open('authors.json') as f:
        authors = json.load(f)

        for author in authors:
            author_object = Author(
                initials=author['initials'],
                first_name=author['name'].split(' ')[0],
                last_name=' '.join(author['name'].split(' ')[1:]),
                author_title=author['role'],
                author_image=author['img'],
                author_page=author['page']
            )
            author_object.save()
