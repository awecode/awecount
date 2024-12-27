#! /usr/bin/env bash

git checkout 8e66922
python manage.py migrate
git checkout bb1ecf8
python manage.py migrate
git checkout f083e04
python manage.py migrate
git switch main
