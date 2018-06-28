#!/bin/bash

source env/bin/activate
pytest -rx --capture=no $@
