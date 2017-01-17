import json
import os
import pytz
import tweepy

from datetime import datetime
from django.core import serializers
from fabric.api import task
from fabric.contrib import django

# django setup
django.settings_module('factcheck.settings')
import django
django.setup()
from annotations.models import Author, Claim

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
    
    utc = pytz.timezone('UTC')

    if len(Claim.objects.all()) > 0:
        tweet_start_date = Claim.objects.latest('claim_date').claim_date
    else:
        tweet_start_date = datetime(2017, 1, 17, 0, 0, 0, 0, tzinfo=utc)


    for status in tweepy.Cursor(
        api.user_timeline, 
        screen_name='realDonaldTrump',
        trim_user=True
    ).items():
        utc_datetime = utc.localize(status.created_at, is_dst=None)

        if tweet_start_date >= utc_datetime:
            return

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

