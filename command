source venv/bin.activate
pipenv shell
pipenv run gunicorn app:app

To install psycopg2
1. Install postress.app
2. Set the PATH (https://stackoverflow.com/questions/20170895/mac-virtualenv-pip-postgresql-error-pg-config-executable-not-found)
export PATH=$PATH:/Applications/Postgres.app/Contents/Versions/latest/bin