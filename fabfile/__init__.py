import app_config

from fabric.api import local, settings, task
from fabric.state import env

# Other fabfiles
from . import data
from . import servers

"""
Base configuration
"""
env.user = app_config.SERVER_USER
env.forward_agent = True

env.hosts = []

"""
Environments
Changing environment requires a full-stack test.
An environment points to both a server and an S3
bucket.
"""
@task
def production():
    """
    Run as though on production.
    """
    env.settings = 'production'
    app_config.configure_targets(env.settings)
    env.hosts = app_config.SERVERS

@task
def staging():
    """
    Run as though on staging.
    """
    env.settings = 'staging'
    app_config.configure_targets(env.settings)
    env.hosts = app_config.SERVERS

"""
Branches
Changing branches requires deploying that branch to a host.
"""
@task
def stable():
    """
    Work on stable branch.
    """
    env.branch = 'stable'

@task
def master():
    """
    Work on development branch.
    """
    env.branch = 'master'

@task
def branch(branch_name):
    """
    Work on any specified branch.
    """
    env.branch = branch_name

@task
def collect_static():
    local('python manage.py collectstatic')

@task
def setup_django():
    data.create_db()
    local('python manage.py makemigrations annotations')
    local('python manage.py migrate annotations')
    local('python manage.py migrate')
    local('python manage.py collectstatic')
    local('python manage.py createsuperuser')
    data.reset_db()

@task
def migrate_db():
    local('python manage.py makemigrations')
    local('python manage.py migrate')

@task
def deploy_server():
    servers.checkout_latest()
    servers.restart_service('uwsgi')