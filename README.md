# Factcheck DB

## What is this?

Factcheck DB is a Django-based application for facilitating annotations on President Donald Trump's tweets. Its output is JSON that is used to create the graphic seen on [npr.org](www.npr.org/2017/01/27/511216062/president-trumps-tweets-annotated)

Factcheck DB does the following things:

1. Downloads tweets from @realDonaldTrump and @POTUS every minute via a cron job, and logs new ones to a database.
2. Sets up a Django admin for creating annotations on the tweets in the database.
3. Publishes JSON to Amazon S3 for use in graphics.
4. Publishes a CSV of [all collected tweets](https://apps.npr.org/factcheck/tweets.csv) to Amazon S3 for static analysis.

## Prerequisites

- Python 3
- Virtualenv and virtualenvwrapper
- PostgreSQL
- AWS EC2s with Python 3, uWSGI, nginx, upstart, and PostgreSQL drivers installed.
- AWS S3 buckets

## Set up Factcheck DB

*If you work at NPR, then the proper environment variables are stored in our shared env file.*

First, ensure you have created a Twitter app so that you can download the tweets. Store your consumer key, consumer secret, access token and access secret as environment variables. You should also store your local PostgreSQL settings.

```
export factcheckdb_POSTGRES_USER="yourusername"
export factcheckdb_POSTGRES_PASSWORD="yourpassword"
export factcheckdb_POSTGRES_HOST="yourpostgreshost"
export factcheckdb_POSTGRES_PORT="yourpostgresport"
export factcheckdb_TWITTER_CONSUMER_KEY="yourtwitterconsumerkey"
export factcheckdb_TWITTER_CONSUMER_SECRET="yourtwitterconsumersecret"
export factcheckdb_TWITTER_ACCESS_KEY="yourtwitteraccesskey"
export factcheckdb_TWITTER_ACCESS_SECRET="yourtwitteraccesssecret"
```

Then, you can setup the repo.

```
git clone https://github.com/nprapps/factcheck-db.git
cd factcheck-db
mkvirtualenv -p `which python3` factcheck-db
pip install -r requirements.txt
fab setup_django
```

This will set up your virtual environment with all the necessary Python software and setup your database and Django admin.

## Models

There are three models:

- Claim: In this use case, a tweet. But it could be modified to handle any kind of claim.
- Annotation: Contains the text of an annotation, joined to any number of Claims and one Author.
- Author: The author of an annotation.

## How it works

A cron job pulls in tweets from @realDonaldTrump and logs them to the database as Claim objects.

In the admin, any user can annotate any number of claims. On save, the signal runs that creates `annotations.json`, a file containing all annotations in the database.

## Deploying Factcheck DB to servers

The Fabric commands provide all the necessary tooling to interact with EC2 servers (or any Ubuntu server). In the examples that follow, I'll be configuring the staging server.

You'll need to ensure that the software listed above is installed on the server. Additionally, you will need to place the following environment variables in `/etc/environment`:

```
export DEPLOYMENT_TARGET="staging"
export AWS_ACCESS_KEY_ID="yourawsaccesskey"
export AWS_SECRET_ACCESS_KEY="yourawssecretaccesskey"
export factcheckdb_POSTGRES_USER="yourusername"
export factcheckdb_POSTGRES_PASSWORD="yourpassword"
export factcheckdb_POSTGRES_HOST="yourpostgreshost"
export factcheckdb_POSTGRES_PORT="yourpostgresport"
export factcheckdb_TWITTER_CONSUMER_KEY="yourtwitterconsumerkey"
export factcheckdb_TWITTER_CONSUMER_SECRET="yourtwitterconsumersecret"
export factcheckdb_TWITTER_ACCESS_KEY="yourtwitteraccesskey"
export factcheckdb_TWITTER_ACCESS_SECRET="yourtwitteraccesssecret"
```

First, run `fab staging master servers.setup`, which will create the necessary directories and install the app on the server.

To setup the Django app, use `servers.fabcast` to run a Fabric process on the server. In this case, you would run `fab staging master servers.fabcast:setup_django`.

Then, deploy the configuration for uWSGI and nginx with `fab staging master servers.deploy_confs`.

You _should_ be able to go to `http://yourserveraddress.com/admin` and get your Django admin.

## Managing Django

As you develop on this further, there are some convenience commands for development. Use `servers.fabcast` to run these on the server.

- `fab migrate_db`: Migrates the database.
- `fab collect_static`: Runs `python manage.py collectstatic`.
- `fab data.reset_db`: Resets the Claim and Author models, redownloads Trump tweets.

