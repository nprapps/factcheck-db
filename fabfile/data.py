import app_config
import csv
import json
import os
import pytz
import requests
import tweepy

from datetime import datetime
from fabric.api import execute, hide, local, settings, shell_env, task
from fabric.contrib import django
from fabric.state import env

# django setup
django.settings_module('factcheck.settings')
import django
django.setup()
from annotations.models import Author, Claim

def authenticate():
    secrets = app_config.get_secrets()

    auth = tweepy.OAuthHandler(
        secrets['TWITTER_CONSUMER_KEY'], 
        secrets['TWITTER_CONSUMER_SECRET']
    )
    auth.set_access_token(
        secrets['TWITTER_ACCESS_KEY'], 
        secrets['TWITTER_ACCESS_SECRET']
    )

    api = tweepy.API(auth)
    return api


@task
def get_trump_tweets():
    api = authenticate()
    
    utc = pytz.timezone('UTC')
    et = pytz.timezone('US/Eastern')

    if len(Claim.objects.all()) > 0:
        tweet_start_date = Claim.objects.latest('claim_date').claim_date
    else:
        tweet_start_date = datetime(2017, 1, 20, 0, 0, 0, 0, tzinfo=et)

    all_tweets=[]
    handles = ['realDonaldTrump', 'POTUS']

    for handle in handles:
        for status in tweepy.Cursor(
            api.user_timeline, 
            screen_name=handle,
            trim_user=True
        ).items():
            utc_datetime = utc.localize(status.created_at, is_dst=None)
            if tweet_start_date >= utc_datetime:
                break
            claim = Claim(
                claim_text=status.text,
                claim_type='twitter',
                claim_date=utc_datetime,
                claim_source='https://twitter.com/{0}/status/{1}'.format(handle, status.id),
                claim_handle=handle
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

@task
def create_db():
    with settings(warn_only=True), hide('output', 'running'):
        if env.get('settings'):
            execute('servers.stop_service', 'uwsgi')

        with shell_env(**app_config.database):
            local('dropdb --if-exists %s' % app_config.database['PGDATABASE'])

        if not env.get('settings'):
            local('psql -c "DROP USER IF EXISTS %s;"' % app_config.database['PGUSER'])
            local('psql -c "CREATE USER %s WITH SUPERUSER PASSWORD \'%s\';"' % (app_config.database['PGUSER'], app_config.database['PGPASSWORD']))

        with shell_env(**app_config.database):
            local('createdb %s' % app_config.database['PGDATABASE'])

        if env.get('settings'):
            execute('servers.start_service', 'uwsgi')

@task
def reset_db():
    Claim.objects.all().delete()
    Author.objects.all().delete()

    get_trump_tweets()
    create_authors()

@task
def audit_tweets():
    for claim in Claim.objects.all():
        r = requests.head(claim.claim_source)
        if r.status_code == 404:
            print('{0} does not exist, {1}'.format(claim.claim_source, r.status_code))
            claim.exists = False
            claim.save()

@task
def export_tweets():
    tweets = Claim.objects.all()

    with open('tweets.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow([
            'date',
            'handle',
            'text',
            'url',
            'exists'
        ])

        for tweet in tweets:
            writer.writerow([
                tweet.claim_date,
                tweet.claim_handle,
                tweet.claim_text,
                tweet.claim_source,
                tweet.exists
            ])