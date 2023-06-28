# Wave Gauge Documentation

## What does it do?
The wave gauge is a sensor made to analyse the pressure under water at a given location. This pressure analysis provides information on the state and evolution of seas/oceans, as it provides information on sea level and wave frequency and power.

## How to initialize your DIY wave gauge?
Once you've assembled the electronics for your DIY sensor, you can choose from a range of injection codes:
•	Hardware Testing folder
o	« Check SD writting.ino »
o	« Check Pressure Sensor.ino »
•	Sensor Data Gathering folder
o	« Wave gauge v2.ino »
### Step 1 :
•	Inject “Check SD writting.ino” into the board and check if the data are written on your SD card
### Step 2 :
•	Inject “Check Pressure Sensor.ino” into the board. Then check if the sensor itself is able to gather data. If it’s not working, check your cables, connections and try with another sensor.
### Step 3:
•	Inject “Wave gauge v2.ino” which is the final code. With that code in the board, your sensor is now working.

## How to retrieve your data?
Once you’ve taken your sensor out of the water, unplug the alimentation cable. Take out your SD card and upload your data to your computer, server, etc…

