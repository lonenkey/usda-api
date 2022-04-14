import requests
import json
from requests.structures import CaseInsensitiveDict

url = "https://api.nal.usda.gov/fdc/v1/foods/search?api_key=ci382bPqyQBylV8bkbeqK7ZQGNeW93lIZFevpXOf"

headers = CaseInsensitiveDict()
headers["Content-Type"] = "application/json"

data = '{"query": "loquat", "dataType": ["Branded"], "sortBy": "fdcId", "sortOrder": "desc"}'

resp = requests.post(url, headers=headers, data=data)
food_data = json.dumps(resp.json(), indent = 4)

#jsonify = json.dumps(food_data, indent = 4)
print(food_data)
#print (jsonify)
