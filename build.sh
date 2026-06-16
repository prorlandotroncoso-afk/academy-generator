#!/usr/bin/env bash

apt-get update || true
apt-get install -y tesseract-ocr poppler-utils || true

pip install -r requirements.txt