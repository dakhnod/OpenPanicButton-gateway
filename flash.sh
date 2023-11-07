#!/bin/bash

set -e

if ! [ $1 ]; then
    echo "please specify an id"
    exit
fi

AMPY_PORT=/dev/ttyUSB*

if ! [ -c "$AMPY_PORT" ]; then
    AMPY_PORT=/dev/ttyACM*
fi

if ! [ -c "$AMPY_PORT" ]; then
    read -p "Please enter serial port: " port
    AMPY_PORT=$port
fi

echo "Serial port: $AMPY_PORT"

cp config.json /tmp/openpanic_config.json

sed -i "s/\"name\": \"Node X\"/\"name\": \"Node $1\"/" /tmp/openpanic_config.json
sed -i "s/\"id\": X/\"id\": $1/" /tmp/openpanic_config.json

cat /tmp/openpanic_config.json

echo "copying main.py"
ampy -p $AMPY_PORT put main.py

sleep 2

echo "copying config.json"
ampy -p $AMPY_PORT put /tmp/openpanic_config.json config.json

rm /tmp/openpanic_config.json