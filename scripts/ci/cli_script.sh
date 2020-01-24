#!/usr/bin/env bash
set -e

echo "install model for cli"
pip3 install ./model

echo "install kaos cli"
cd cli
pip3 install -e .
kaos
