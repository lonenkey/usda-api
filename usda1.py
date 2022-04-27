import requests
import json
from requests.structures import CaseInsensitiveDict

url = "https://api.nal.usda.gov/fdc/v1/foods/search?api_key=ci382bPqyQBylV8bkbeqK7ZQGNeW93lIZFevpXOf"

food = input("What food are you looking for:  ")

headers = CaseInsensitiveDict()
headers["Content-Type"] = "application/json"

data = {"query": "goji" , "dataType": ["Branded"], "maxItems": 1, "format": "abridged"}
print (data)
#json.dumps(data)
print (data)
resp = requests.post(url, headers=headers, json=data)
food_data = json.dumps(resp.json(), indent = 4)
food_fields = json.loads(food_data)
#jsonify = json.dumps(food_data, indent = 4)
#print(food_data)
#print (jsonify)
print (food_fields["foods"]["description"])
