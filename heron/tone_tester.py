import json

import requests

data = "He Donnie, put that Big Mac down, here are more beautiful women out marching today! #WomensMarch2018pic.twitter.com/uelqNnVNVY"

username = 'b7712a18-059e-4569-bee3-0d28f10e1d54'
password = 'p64ahPWTv4Pr'
watsonUrl = 'https://gateway.watsonplatform.net/tone-analyzer/api/v3/tone?version=2017-09-21&text='

headers = {"content-type": "text/plain"}

r = requests.post(watsonUrl, auth=(username, password), headers=headers,
                  data=data)
tone_dict = json.loads(r.text)['document_tone']['tones']
readable_dict = {x['tone_name']: x['score'] for x in tone_dict}
print readable_dict
