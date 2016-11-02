# happ-backend application

## create sample data
You can create sample cities, currencies, interests, users and events.
Cities and currencies are created from fixtures. Interests, users and events are created randomly.

``` ./manage.py create_cities ```

``` ./manage.py create_currencies ```

``` ./manage.py create_interests N ```

``` ./manage.py create_users N ```

``` ./manage.py create_events N ```

Create cities and currencies first, then interests and users, and after that - events.

## migrate your mongo schema or data

./manage.py migrate 000X   #  check migration number you need to upgrade to in `happ.migrations` module and then do following migrations

## Deployment strategy

1. Containerize and name services using docker-compose +
2. Deploy app locally using nginx and two docker containers of app
3. Split nginx features to different docker containers: +
	3.1 Serve static +
	3.2 Proxy +
4. Refine docker-compose and deploy 2) and 3) with docker-machine using one docker host +
5. Deploy whole application locally 1)-4) using two docker hosts with docker swarm and docker-machine
	5.1 Determine naming conventions of images
	5.2 Refine docker network topology with scale in mind
6. Deploy 5) on production environment

# Automated deploy

## Application provisioning

1. Build wheel package of app with version-x.y.z
2. App and celery compose files should change just version of app to install on image at pre-launch stage
3. Refine docker-compose.prod.yml to reflect 1) and 2)

# Application launch

## dev version

1. add `127.0.0.1	happ.dev` to `/etc/hosts`
2. copy `conf/nginx/dev/happ.host.conf` to `/etc/nginx/sites-available/` and create symlink
3. restart nginx on host machine
4. run `docker-compose -f docker-compose.dev.yml up`
