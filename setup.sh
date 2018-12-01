#!/usr/bin/env bash
sudo pip install pipenv
pipenv install --dev
pipenv run ./db-setup.sh
pipenv shell

