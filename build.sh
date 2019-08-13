#!/bin/bash

rm -rf dist build .eggs ksmi.egg-info

python3 setup.py sdist bdist_wheel
python3 -m twine upload dist/* --verbose

pip3 install --upgrade ksmi 