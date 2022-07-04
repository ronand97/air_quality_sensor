# SDS011 Air Quality Sensor Project

## Intro
With airborne transmission facilitating the transmission of covid-19, and with my growing interest in climate change, renewable energy, and climate tech, I found myself more interested in the air quality that we breathe and exist in every day. I decided to buy a raspberry pi and a simple air quality sensor - in this case I'm using an SDS011 sensor which has a lifetime of ~ 1 year if used sparingly for measurements. The sensor can detect PM2.5 and PM10 particles in the air. *PM* stands for Particulate Matter and the number denotes how small the particle being measured is, in [micrometres]. We breathe these particles into our lungs, and depending on lots of factors I'm not smart enough to fully grasp, can have very negative health connotations. Although different countries/organisations have their own definitions, there are "safe" limits set by WHO which you should not breathe in for prolonged periods of time.

https://www.gov.uk/government/statistics/air-quality-statistics/concentrations-of-particulate-matter-pm10-and-pm25

I recently moved to London, known for its poor pollution, and have set the sensor up to take a reading every 10 minutes in my living room. The data is uploaded to a Cassandra DB instance on DataStax (chosen for its generous free tier). 

Since I'm in the same borough as the world's densest air quality sensor network (https://www.airlabs.com/worlds-densest-air-quality-sensor-network-aims-to-revolutionise-understanding-of-air-pollution-in-urban-spaces/) I should be able to match my measurements up with theirs!

## Taking sensor readings
I found this bit very fiddly and there are lots of wild code snippets online to take sensor readings. Most work, but I could not get to work reliably and some are written horrifically. After many weeks of fiddling around I settled on using this repo:
https://github.com/chrisballinger/sds011_particle_sensor

many thanks to this author. If you clone my repo, you will have to init the git submodule which I have used to access this code (I'm aware git submodules are not the best solution).

`$ git submodule init`

`$ git submodule update`

Then, I have automated the running of this script using a shell script and setting a cronjob up on the raspberry pi. Single readings can be taken using something like 

`python src/run.py > temp.log 2>&1 &`

## Dashboard
I used streamlit as it is very simple to get something up and running quickly. It really just connects to Cassandra and pulls data and displays it. I've then wrapped it in Docker and deployed it to an Azure Container Service hooked up to an Azure Web App. This was more painful than it needed to be due to me building an image using an M1 Mac (ARM based CPU) and the image not running on Azure, giving me a generic message of:
> standard_init_linux.go:228: exec user process caused: exec format error

To get around this, make sure to build the Dockerfile with the `--platform` flag, e.g.
`$ docker build --platform linux/amd64 -t <img_name>:<img_tag> .     `


I found these articles to be very useful:
1. https://docs.microsoft.com/en-us/azure/app-service/tutorial-custom-container?pivots=container-linux
2. https://www.section.io/engineering-education/how-to-deploy-streamlit-app-with-docker/


## To Do (When I have some more free time)
* Makefile
* Better soln to git submodule
* Add more functionality to dashboard using existing data (filters, etc)
* Add new data to dashboard (camden clean air data, wind direction)
* Investigate predictive model for air quality for a given day
* Known unknowns I haven't remembered
* Unknown unknowns
