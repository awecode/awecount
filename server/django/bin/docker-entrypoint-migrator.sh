#!/usr/bin/env bash

set -e

uv run manage.py wait_for_db $1

uv run manage.py migrate $1
