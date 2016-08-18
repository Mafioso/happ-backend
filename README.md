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
