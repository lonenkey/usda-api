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
    Calculate a health score based on nutrient values.
    """
    
    # Extract nutrient values with defaults of 0 if not present
    protein = nutrients.get('Protein', 0.0)  # g
    total_fat = nutrients.get('Total lipid (fat)', 0.0)  # g
    carbs = nutrients.get('Carbohydrate, by difference', 0.0)  # g
    calories = nutrients.get('Energy', 0.0)  # kcal
    sugars = nutrients.get('Total Sugars', 0.0)  # g
    fiber = nutrients.get('Fiber, total dietary', 0.0)  # g
    calcium = nutrients.get('Calcium, Ca', 0.0)  # mg
    iron = nutrients.get('Iron, Fe', 0.0)  # mg
    sodium = nutrients.get('Sodium, Na', 0.0)  # mg
    vitamin_a = nutrients.get('Vitamin A, IU', 0.0)  # IU
    vitamin_c = nutrients.get('Vitamin C, total ascorbic acid', 0.0)  # mg
    cholesterol = nutrients.get('Cholesterol', 0.0)  # mg
    saturated_fat = nutrients.get('Fatty acids, total saturated', 0.0)  # g

    # Avoid division by zero
    if calories == 0:
        return 0

    # Calculate nutrient densities (per 100 kcal)
    protein_density = (protein / calories) * 100
    fiber_density = (fiber / calories) * 100
    total_fat_density = (total_fat / calories) * 100
    saturated_fat_density = (saturated_fat / calories) * 100
    sugar_density = (sugars / calories) * 100
    cholesterol_density = (cholesterol / calories) * 100  # mg per 100 kcal
    calcium_density = (calcium / calories) * 100  # mg per 100 kcal
    iron_density = (iron / calories) * 100  # mg per 100 kcal
    sodium_density = (sodium / calories) * 100  # mg per 100 kcal
    vitamin_a_density = (vitamin_a / calories) * 100  # IU per 100 kcal
    vitamin_c_density = (vitamin_c / calories) * 100  # mg per 100 kcal

    # Positive components (max contribution of 70 points)
    protein_score = min(protein_density * 2, 25)  # Max 25 points for 12.5g/100kcal
    fiber_score = min(fiber_density * 5, 15)  # Max 15 points for 3g/100kcal
    vitamin_score = min((vitamin_a_density / 500 + vitamin_c_density / 10), 15)  # Max 15 points
    mineral_score = min((calcium_density / 50 + iron_density / 2), 15)  # Max 15 points
    
    positive_total = protein_score + fiber_score + vitamin_score + mineral_score

    # Negative components (can subtract up to 50 points)
    fat_penalty = min(total_fat_density * 1.5, 20)  # Max 20 penalty for 13.3g/100kcal
    sat_fat_penalty = min(saturated_fat_density * 3, 10)  # Max 10 penalty for 3.33g/100kcal
    sugar_penalty = min(sugar_density * 2, 10)  # Max 10 penalty for 5g/100kcal
    cholesterol_penalty = min(cholesterol_density / 20, 10)  # Max 10 penalty for 200mg/100kcal
    
    negative_total = fat_penalty + sat_fat_penalty + sugar_penalty + cholesterol_penalty

    # Calculate final score (base of 80, max positive 70, max negative -50)
    raw_score = 80 + positive_total - negative_total
    
    # Normalize to 0-100 scale
    final_score = max(0, min(100, raw_score))
    
    return round(final_score)

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

def main():
    """
    Main function will call the rest of the application.
    """
    food = input("What food are you looking for:  ")
    get_food_items(food)

if __name__ == "__main__":
    main()
