import requests
import json
import sys
from requests.structures import CaseInsensitiveDict
from pathlib import Path

def calculate_health_score(food_nutrients):
    """
    Calculates a health score based on the ratio of calories to protein,
    with bonuses for fiber and penalties for high sugar, saturated fat, and sodium.
    """
    calories = protein = fiber = sugar = sat_fat = sodium = 0
    
    for nutrient in food_nutrients:
        if nutrient["nutrientName"].lower() == "energy":
            calories = nutrient["value"]
        elif "protein" in nutrient["nutrientName"].lower():
            protein = nutrient["value"]
        elif "fiber" in nutrient["nutrientName"].lower():
            fiber = nutrient["value"]
        elif "sugar" in nutrient["nutrientName"].lower():
            sugar = nutrient["value"]
        elif "saturated fat" in nutrient["nutrientName"].lower():
            sat_fat = nutrient["value"]
        elif "sodium" in nutrient["nutrientName"].lower():
            sodium = nutrient["value"]
    
    if calories == 0:
        return 0  # Avoid division by zero
    
    # Base score from protein-to-calorie ratio
    health_score = (protein / calories) * 100
    
    # Adjust score for other nutrients
    health_score += fiber * 2  # Fiber is good, adds points
    health_score -= sugar * 1.5  # High sugar is bad, reduces points
    health_score -= sat_fat * 2  # Saturated fat reduces points
    health_score -= sodium / 100  # High sodium reduces points
    
    return max(0, round(health_score, 2))  # Ensure score isn't negative

def get_food_items(food):
    credentials_file = Path("credentials.py")
    if not credentials_file.exists():
        print("Error: Credentials not found")
        sys.exit(1)
    
    import credentials
    url = credentials.url
    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"
    
    data = {"query": food, "dataType": ["Branded"], "maxItems": 1, "format": "abridged"}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        food_data = response.json()
    except requests.exceptions.RequestException as err:
        print(f"Error: {err}")
        return
    
    if "foods" not in food_data or not food_data["foods"]:
        print("No food items found.")
        return
    
    selected_food = food_data["foods"][0]
    print(f"Nutrients for: {selected_food['description']}")
    
    for nutrient in selected_food["foodNutrients"]:
        print(f"{nutrient['nutrientName']}: {nutrient['value']} {nutrient['unitName']}")
    
    health_score = calculate_health_score(selected_food["foodNutrients"])
    print(f"Health Score: {health_score}/100")

def main():
    food = input("What food are you looking for: ")
    get_food_items(food)

if __name__ == "__main__":
    main()
