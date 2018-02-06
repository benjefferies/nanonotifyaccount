# NanoNotify WebApp

Web application for https://nanonotify.co

## Installing
Install pyenv and pipenv. Ensure pyenv installs 3.6.1
```bash
curl -L https://raw.githubusercontent.com/pyenv/pyenv-installer/master/bin/pyenv-installer | bash
pip install pipenv
pipenv install --dev
```

## Run with pipenv 
Running for local development
```bash
pipenv run python run.py
```
Running multi threaded
```bash
pipenv run gunicorn -w 4 -b 0.0.0.0:5000 run:app
```
