import requests
import json
import credentials  # Unused import if 'credentials' is not fully utilized

''' We need to refine the search to return more useful information, more refined.
    Also needed, add error handling, return a health score by comparing the protein, carbs, calories
    and other nutrients to rate each food on how good it is for you.
    Also, generate a document with serveral different foods chosen
    Create a database of recently saved foods.'''
# PEP8: Use triple double quotes for docstrings (""" instead of ''')
# PEP8: Typo in "serveral" -> should be "several"

def main():  # PEP8: Function docstring missing
    food = input("What food are you looking for:  ")  # PEP8: Extra space after colon
    get_food_items(food)

def get_food_items(food):  # PEP8: Function docstring missing
    url = credentials.url  # PEP8: Ensure 'credentials.url' exists or handle missing attribute
    headers = requests.structures.CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"

    data = {"query": food, "dataType": ["Branded"], "maxItems": 1, "format": "abridged"}
    # PEP8: For complex dictionaries, break into multiple lines for readability

    resp = requests.post(url, headers=headers, json=data)
    # PEP8: No error handling for the API request (add try-except block)

    food_data = json.dumps(resp.json(), indent = 4)
    # PEP8: Avoid spaces around the equals sign in keyword arguments (use indent=4)

    with open("food_data.txt", "w") as f:
        f.write(food_data)

    food_fields = json.loads(food_data)

    with open("food_fields.txt", "w") as f:
        f.write(str(food_fields))

    hits = (food_fields["totalHits"])
    # PEP8: Unnecessary parentheses around 'food_fields["totalHits"]'

    if hits > 50:
        hits = 50

    itemcount=0  # PEP8: Missing spaces around assignment operator (itemcount = 0)
    print("Matching foods:")  # PEP8: Space inside parentheses is unnecessary

    for itemcount in range(0, hits):
        print(str(itemcount) + " " + food_fields["foods"][itemcount]["description"])
        # PEP8: Prefer f-strings over concatenation for readability

    item_choice = int(input("Which item would you like to see: "))  
    # PEP8: Consider wrapping input in try-except to handle non-integer input

    print(str(item_choice) + " " + food_fields["foods"][item_choice]["description"])
    # PEP8: Prefer f-strings over concatenation

    print(f"Nutrients for:", food_fields["foods"][item_choice]["description"])
    # PEP8: When using f-strings, avoid mixing with commas, use full f-string

    selected_food = food_fields["foods"][item_choice]

    print(f"Nutrients for: {selected_food['description']}")

    for nutrient in selected_food["foodNutrients"]:
        print(f"{nutrient['nutrientName']}: {nutrient['value']} {nutrient['unitName']}")
        # PEP8: Inline comment (#test) is irrelevant and should be removed

def main():  # PEP8: Duplicate function definition (remove one)
    food = input("What food are you looking for:  ")

if __name__ == "__main__":
    main()