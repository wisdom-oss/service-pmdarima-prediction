## Python Version
Use Python Interpreter 3.12.9 at most in order to use pmdarima


## Connection to Database
1. Credentials are secure, you can hook up your own database if wanted
2. when using ours, vpn connection to UOL must be established

## Inserting Data

1. Uncomment Instructions in data_inserter.py
2. Fill files/smartmeterdata with json files
3. start data_inserter.py to create (hyper)tables and insert data

## Flask Service
1. Start app.py
2. Use defined endpoints
3. Make sure .env is defined

## Environment Variables
Add these variables to your .env (located in root) in order to start the service.
You need to connect your own postgresql database.

ALLOW_DUPLICATE_MODELS=False

DEVICE_PREFIX=urn:ngsi-ld:Device:

FILE_PATH_TRAINED_MODELS=files/trained_models

FILE_PATH_EXAMPLE_DATA=files/smartmeterdata/

FILE_PATH_RESULTS=files/results/

EXAMPLE_META_DATA=example_pm_meta.json

EXAMPLE_DATA=example_pm_measurements.json

DATETIME_STANDARD_FORMAT="%d.%m.%y %H:%M"

DB= name-of-your-db

USER= name-of-your-user

PW= your-pw

HOST= your-host

PORT= your-port

DWD_API_V1=https://wisdom-demo.uol.de/api/dwd/v1

WEATHER_STATION=/00691

