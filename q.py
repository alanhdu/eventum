import requests
import json

url = "http://util.columbiaesc.com/uem?group=Application+Development+Initiative"
r = requests.get(url)
data = json.loads(r.text)["data"]

for event in data:
    print event
    break
