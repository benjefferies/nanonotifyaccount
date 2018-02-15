#!/usr/bin/env bash

export $(cat .env | xargs)
python run.py