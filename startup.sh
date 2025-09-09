#!/bin/bash

sleep 10

export DISPLAY=:0
export XDG_RUNTIME_DIR=/run/user/1000

cd /home/anderson/picture-frame/web
nohup python3 app.py > /home/anderson/flask.log 2>&1 &

nohup bash /home/anderson/picture-frame/slideshow.sh > /home/anderson/slideshow.log 2>&1  &
