import requests
import json
from requests.structures import CaseInsensitiveDict
import credentials

def main():
    url = credentials.url

    food = input("What food are you looking for:  ")

    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"

    data = {"query": food, "dataType": ["Branded"], "maxItems": 1, "format": "abridged"}
    resp = requests.post(url, headers=headers, json=data)
    food_data = json.dumps(resp.json(), indent = 4)
    food_fields = json.loads(food_data)
    hits = (food_fields["totalHits"])
    if hits > 50:
        hits = 50
    itemcount=1
    print ("Matching foods:")
    for itemcount in range(1, hits):
        #print (item, itemcount)
        print (food_fields["foods"][itemcount]["description"])
        #itemcount = itemcount+1

if __name__ == "__main__":
    main()
