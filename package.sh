#!/usr/bin/bash

set -e

pyinstaller -D calculate.py --collect-all paddleocr --collect-all pyclipper --collect-all imghdr --collect-all skimage --collect-all imgaug --collect-all scipy.io --collect-all lmdb --collect-all Cython --collect-all requests

cp /opt/homebrew/Cellar/openssl@3/3.3.1/lib/libcrypto.3.dylib dist/main/_internal


