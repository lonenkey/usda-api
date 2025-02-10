import requests
import json
import credentials

''' We need to refine the search to return more useful information, more refined.
    Also needed, add error handling, return a health score by comparing the protein, carbs, calories
    and other nutrients to rate each food on how good it is for you.
    Also, generate a document with serveral different foods chosen
    Create a database of recently saved foods.'''

def main():
    food = input("What food are you looking for:  ")
    get_food_items(food)

def get_food_items(food):
    url = credentials.url
    headers = requests.structures.CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"
    data = {"query": food, "dataType": ["Branded"], "maxItems": 1, "format": "abridged"}
    # Make the API call here.
    resp = requests.post(url, headers=headers, json=data)
    food_data = json.dumps(resp.json(), indent = 4)

    with open("food_data.txt", "w") as f:
        f.write(food_data)
    food_fields = json.loads(food_data)

    with open("food_fields.txt", "w") as f:
        f.write(str(food_fields))
    
    hits = (food_fields["totalHits"])
    if hits > 50:
        hits = 50

    itemcount=0
    print ("Matching foods:")

    for itemcount in range(0, hits):
        print (str(itemcount) + " " + food_fields["foods"][itemcount]["description"])

    # create a try and except block
    item_choice = int(input ("Which item would you like to see: "))
    print (str(item_choice) + " " + food_fields["foods"][item_choice]["description"])

    # Print food name
    print (f"Nutrients for:", food_fields["foods"][item_choice]["description"])
    
    selected_food = food_fields["foods"][item_choice]  
    
    # Print nutrients
    print(f"Nutrients for: {selected_food['description']}")
    for nutrient in selected_food["foodNutrients"]:
        print(f"{nutrient['nutrientName']}: {nutrient['value']} {nutrient['unitName']}")   
        #test 


def main():
    food = input("What food are you looking for:  ")
    get_food_items(food)


if __name__ == "__main__":
    main()
