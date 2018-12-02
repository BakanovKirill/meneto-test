#!/usr/bin/env bash
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install python3.6
export PIPENV_VENV_IN_PROJECT=1
cat <<EOF > ./.env
APP_NAME="meneto"
APP_SETTINGS="project.server.config.DevelopmentConfig"
FLASK_DEBUG=1
EOF
sudo pip install pipenv
pipenv install --dev
pipenv run ./db-setup.sh
pipenv shell

