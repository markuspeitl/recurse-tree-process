#!/usr/bin/env sh

bash build.sh
twine check dist/*
#twine upload -r testpypi dist/*
twine upload dist/*