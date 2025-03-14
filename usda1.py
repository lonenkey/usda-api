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
def calculate_health_score(nutrients):
    """
    Calculate a health score based on a modified Nutri-Score system and map it to a 1-100 scale.
    """
    # Extract nutrient values with defaults of 0 if not present
    protein = nutrients.get('Protein', 0.0)  # g
    total_fat = nutrients.get('Total lipid (fat)', 0.0)  # g
    carbs = nutrients.get('Carbohydrate, by difference', 0.0)  # g
    calories = nutrients.get('Energy', 0.0)  # kcal
    sugars = nutrients.get('Total Sugars', 0.0)  # g
    fiber = nutrients.get('Fiber, total dietary', 0.0)  # g
    sodium = nutrients.get('Sodium, Na', 0.0)  # mg
    saturated_fat = nutrients.get('Fatty acids, total saturated', 0.0)  # g
    cholesterol = nutrients.get('Cholesterol', 0.0)  # mg
    calcium = nutrients.get('Calcium, Ca', 0.0)  # mg
    iron = nutrients.get('Iron, Fe', 0.0)  # mg
    vitamin_a = nutrients.get('Vitamin A, IU', 0.0)  # IU
    vitamin_c = nutrients.get('Vitamin C, total ascorbic acid', 0.0)  # mg

    if calories == 0:
        return 1  # Prevent division errors

    # Positive components (up to 40 points)
    protein_score = min((protein / calories) * 100 * 2, 15)  # More reward for protein
    fiber_score = min((fiber / calories) * 100 * 7, 15)  # More reward for fiber
    vitamin_score = min((vitamin_a / 5000) + (vitamin_c / 30), 10)  # Reward for vitamins
    mineral_score = min((calcium / 500) + (iron / 5), 10)  # Reward for minerals

    positive_score = protein_score + fiber_score + vitamin_score + mineral_score

    # Negative components (up to 50 points)
    fat_penalty = min((total_fat / calories) * 100 * 1.2, 10)  # Less penalty for total fat
    sat_fat_penalty = min((saturated_fat / calories) * 100 * 2, 10)  # Same for sat fat
    sugar_penalty = min((sugars / calories) * 100 * 2.5, 15)  # Higher penalty for sugar
    sodium_penalty = min((sodium / 1500) * 15, 15)  # More penalty for sodium

    negative_score = fat_penalty + sat_fat_penalty + sugar_penalty + sodium_penalty

    # Calculate Nutri-Score (-20 to 40 scale)
    nutri_score = negative_score - positive_score

    # Convert to 1-100 scale
    health_score = 100 - ((nutri_score + 20) / 60 * 100)

    return round(max(1, min(100, health_score)))  # Ensure within 1-100 range


# Example usage with your sample data
nutrients = {
    'Protein': 15.0,  # g
    'Total lipid (fat)': 26.6,  # g
    'Carbohydrate, by difference': 6.19,  # g
    'Energy': 319,  # kcal
    'Total Sugars': 1.77,  # g
    'Fiber, total dietary': 0.0,  # g
    'Calcium, Ca': 18.0,  # mg
    'Iron, Fe': 0.64,  # mg
    'Sodium, Na': 319,  # mg
    'Vitamin A, IU': 0.0,  # IU
    'Vitamin C, total ascorbic acid': 1.1,  # mg
    'Cholesterol': 62.0,  # mg
    'Fatty acids, total saturated': 3.98  # g
}

#health_score = calculate_health_score(nutrients)
#print(f"Health Score: {health_score}")

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

    if hits > 5:
        hits = 5

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

    nutrients = {}
    for nutrient in selected_food["foodNutrients"]:
        nutrients[nutrient["nutrientName"]] = nutrient["value"]
        print(f"{nutrient['nutrientName']}: {nutrient['value']} {nutrient['unitName']}")
    
    health_score = calculate_health_score(nutrients)
    print(f"Health Score: {health_score}/100")

    return health_score

def main():
    """
    Main function will call the rest of the application.
    """
    while (1):
        food = input("\nWhat food are you looking for:  ")
 
        get_food_items(food)

        choice  = input("\nWant to check another food? (Y/N): ")

        if choice.lower() == 'n':
            break

if __name__ == "__main__":
    main()
    
