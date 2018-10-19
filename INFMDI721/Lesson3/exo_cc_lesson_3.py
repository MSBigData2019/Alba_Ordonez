import requests
import json
import pandas as pd

dfs = pd.read_html("http://www.linternaute.com/ville/classement/villes/population")
villes = dfs[0]['Ville'].str.split(' ').str[0].values
villes = villes[0:3]
KEY = open("key_api_google.txt",'r')
KEY = KEY.read().split('\n')[0]

villes_concat = "|".join(villes)
api_prefix = "https://maps.googleapis.com/maps/api/distancematrix/json?units=metrics"
api_address = f"{api_prefix}&origins={villes_concat}&destinations={villes_concat}&key={KEY}"
response = requests.get(api_address)
json_tab = json.loads(response.content)

distance = list(map(lambda x: list(map(lambda y: y['distance']['text'], x['elements'])), json_tab['rows']))
df = pd.DataFrame(distance, index=villes, columns=villes)
