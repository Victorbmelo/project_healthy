#!/bin/bash

export LC_ALL=en_US.UTF-8

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR

echo "Installing virtualenv"

if which python3.10
then
  PYTHON=python3.10
else
  PYTHON=python3
fi

if ! ${PYTHON} -m pip install virtualenv; then
  echo "========================================="
  echo "ERROR: unable to install virtualenv"
  echo "========================================="
  exit 1
fi

${PYTHON} -m virtualenv .venv
source .venv/bin/activate
${PYTHON} -m pip install -r requirements.txt
deactivate

echo "============================================="
echo "SUCCESS: virtualenv installed."
echo "run 'source .venv/bin/activate' to enable it"
echo "============================================="
exit 0
