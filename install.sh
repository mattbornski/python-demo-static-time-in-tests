#!/bin/bash

virtualenv --no-site-packages --python=python3.6 env/
source env/bin/activate
pip install -r requirements.txt