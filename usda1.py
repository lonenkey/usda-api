import requests
import json
import sys
from requests.structures import CaseInsensitiveDict
from pathlib import Path

""" 
We need to refine the search to return more useful information, more refined.
Also needed, add error handling, return a health score by comparing the protein, carbs, calories
and other nutrients to rate each food on how good it is for you.
Also, generate a document with several different foods chosen
Create a database of recently saved foods.
"""

def get_food_items(food):
    """
    Credentials.url file is required with API url and key
    This module will take the food item and search for it in the USDA database
    """

    credentials_file = Path("credentials.py")

    if credentials_file.exists() and credentials_file.is_file():
        import credentials
        print ("Credentials found.")
    else:
        print ("Error:  Credentials not found")
        sys.exit(1)
    # Set up the API call
    url = credentials.url
    headers = requests.structures.CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"

    data = {"query": food,
            "dataType": ["Branded"],
            "maxItems": 1,
            "format": "abridged"}

    # Make the API call
    try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            food_data = json.dumps(response.json(), indent=4)

    except requests.exceptions.Timeout:
        print("Request timed out.")
    except requests.exceptions.ConnectionError:
        print("Unable to connect.")
    except requests.exceptions.HTTPError as err:
        print(f"Http error: {err}")
    except requests.exceptions.RequestException as err:
        print(f"An error occurred: {err}")

    # Below files are for troubleshooting for now.
    with open("food_data.txt", "w") as f:
        f.write(food_data)

    food_fields = json.loads(food_data)

    with open("food_fields.txt", "w") as f:
        f.write(str(food_fields))

    hits = food_fields["totalHits"]

    if hits > 50:
        hits = 50

    print("Matching foods:")

    for item_count in range(0, hits):
        print(f"{item_count} {food_fields['foods'][item_count]['description']}")

    item_choice = None
    try:
        item_choice = int(input("Which item would you like to see: "))
    except ValueError:
        print ("Please enter an integer for your choice.")

    selected_food = food_fields["foods"][item_choice]
    print(f"Nutrients for: {selected_food['description']}")

    for nutrient in selected_food["foodNutrients"]:
        print(f"{nutrient['nutrientName']}: {nutrient['value']} {nutrient['unitName']}")

def main():
    """
    Main function will call the rest of the application.
    """
    food = input("What food are you looking for:  ")
    get_food_items(food)

if __name__ == "__main__":
    main()