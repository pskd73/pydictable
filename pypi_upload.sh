#!/usr/bin/env bash
pip install twine
python setup.py sdist
pip install wheel
python setup.py bdist_wheel --universal
twine check dist/*
twine upload dist/* --verbose
