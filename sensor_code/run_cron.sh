#! /bin/bash
cd /home/pi/repos/air_quality_sensor/

source venv/bin/activate

python src/run.py > temp.log 2>&1