#!/bin/bash

cd "$(readlink -f $(dirname "${BASH_SOURCE[0]}"))"

python test.py "$@" && python archive.py
