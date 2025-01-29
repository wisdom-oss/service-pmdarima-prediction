from calculations import predictions as pred

df = pred.request_forecast("urn:ngsi-ld:Device:family-household","one week", "hourly")
