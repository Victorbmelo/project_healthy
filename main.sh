#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR

if ! source .venv/bin/activate; then
  exit 1
fi

if 1; then
  python main.py
else
  exit 1
fi
