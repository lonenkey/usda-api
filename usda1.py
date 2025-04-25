import requests
import json
import sys
import logging
import sqlite3
from requests.structures import CaseInsensitiveDict
from pathlib import Path
from typing import Dict, Any
from exceptions import CredentialsError, InputError, USDAAPIError
import credentials as creds  # Use alias for clarity

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='food_app.log',
    filemode='a'
)
logger = logging.getLogger(__name__)

def db_insert(food_info, health_score):
    conn = sqlite3.connect('foods.db')
    cursor = conn.cursor()

    #create a table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Food (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    description TEXT,
    brandOwner TEXT,
    ingredients TEXT,
    nutrientId INTEGER,
    nutrientName TEXT,
    value REAL
    health_score INTEGER
    );
    """)
    
    cursor.executemany(
        "Insert INTO Food (id, description, brandOwner, ingredients, nutrientId, nutrientName, value, health_score)"
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?);", 
        food_info)
    
    conn.commit()
    conn.close()

def calculate_health_score(nutrients: Dict[str, float]) -> int:
    """
    Calculate a health score based on a modified Nutri-Score system.
    
    Args:
        nutrients: Dictionary of nutrients and their values
    
    Returns:
        Integer health score from 1-100
    
    Raises:
        ValueError: If nutrients dictionary is empty or invalid
    """
    try:
        if not nutrients:
            raise ValueError("Empty nutrients dictionary provided")

        # Extract nutrient values with defaults of 0 if not present
        protein = nutrients.get('Protein', 0.0)
        total_fat = nutrients.get('Total lipid (fat)', 0.0)
        carbs = nutrients.get('Carbohydrate, by difference', 0.0)
        calories = nutrients.get('Energy', 0.0)
        sugars = nutrients.get('Total Sugars', 0.0)
        fiber = nutrients.get('Fiber, total dietary', 0.0)
        sodium = nutrients.get('Sodium, Na', 0.0)
        saturated_fat = nutrients.get('Fatty acids, total saturated', 0.0)
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

    except Exception as e:
        logger.error(f"Error calculating health score: {str(e)}")
        return 1

def get_food_items(food: str) -> int:
    """
    Search for food items in the USDA database and calculate health score.
    
    Args:
        food: Food item to search for
    
    Returns:
        Health score of selected food
    
    Raises:
        CredentialsError: If API credentials are not found
        USDAAPIError: If API request fails
        InputError: If user input is invalid
    """
    try:
        # Validate input
        if not food or not food.strip():
            raise InputError("Food search term cannot be empty")

        # Check for credentials
        credentials_file = Path("credentials.py")
        if not credentials_file.exists() or not credentials_file.is_file():
            raise CredentialsError("Credentials file not found")

        url = creds.url
        headers = CaseInsensitiveDict()
        headers["Content-Type"] = "application/json"

        data = {
            "query": food,
            "dataType": ["Branded"],
            "pageSize": 5,
            "pageNumber": 1,
            "sortBy": "score",
            "sortOrder": "desc"
        }

        # Make API request with timeout
        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)

            if response.status_code in (401, 403):
                print("Error:  Invalid or unauthorized API key.  Please check your credentials file.")
                try:
                    error_details = response.json()
                    print(f"API response details: {error_details}")
                except ValueError:
                    print(f"API response: {response.text}")
                return None
            
            response.raise_for_status()
            food_data = response.json()
        except requests.exceptions.Timeout:
            raise USDAAPIError("Request timed out")
        except requests.exceptions.ConnectionError:
            raise USDAAPIError("Unable to connect to API")
        except requests.exceptions.HTTPError as err:
            raise USDAAPIError(f"HTTP error occurred: {err}")
        except requests.exceptions.RequestException as err:
            raise USDAAPIError(f"API request failed: {err}")

        # Validate response
        if not food_data.get("foods"):
            logger.warning(f"No foods found for search term: {food}")
            print("\nNo foods found matching your search.")
            return 0

        hits = min(len(food_data["foods"]), 5)
        print("\nMatching foods:")
        for i in range(hits):
            food_item = food_data["foods"][i]
            print(f"{i}. {food_item['description']} - {food_item.get('brandName', 'Unknown Brand')}")

        # Get user selection
        while True:
            try:
                item_choice = int(input(f"\nWhich item would you like to see (0-{hits-1}): "))
                if not 0 <= item_choice < hits:
                    raise ValueError
                break
            except ValueError:
                print(f"Please enter a valid number between 0 and {hits-1}")

        selected_food = food_data["foods"][item_choice]
        print(f"\nNutrients for: {selected_food['description']}")
        print(f"Brand: {selected_food.get('brandName', 'Unknown Brand')}")
        print(f"Ingredients: {selected_food.get('ingredients', 'Not available')}\n")

        nutrients = {}
        for nutrient in selected_food.get("foodNutrients", []):
            if "nutrientName" in nutrient and "value" in nutrient:
                nutrients[nutrient["nutrientName"]] = nutrient["value"]
                print(f"{nutrient['nutrientName']}: {nutrient['value']} {nutrient.get('unitName', '')}")

        health_score = calculate_health_score(nutrients)
        print(f"\nHealth Score: {health_score}/100")

        return health_score

    except CredentialsError as e:
        logger.error(f"Credentials error: {str(e)}")
        sys.exit(1)
    except USDAAPIError as e:
        logger.error(f"API error: {str(e)}")
        return 0
    except InputError as e:
        logger.error(f"Input error: {str(e)}")
        return 0
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return 0

def main() -> None:
    """
    Main application loop with error handling.
    """
    print("Welcome to the USDA Food Database Search")
    print("=======================================")

    while True:
        try:
            food = input("\nWhat food are you looking for (or 'quit' to exit): ").strip()
            
            if food.lower() == 'quit':
                print("\nThank you for using the application!")
                break

            if not food:
                print("Please enter a food name")
                continue

            health_score = get_food_items(food)
            
            if health_score > 0:
                print("\nWant to save this food or check another (1=save, 2=check another, n=quit)?")
                choice = input("Enter your choice: ").strip()
                if choice == 'n':
                    print("\nThank you for using the application!")
                    break
                elif choice != '1':
                    db_insert([food, health_score]) # Save food info to database)

            
        except KeyboardInterrupt:
            print("\nApplication terminated by user")
            break
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {str(e)}")
            print("An unexpected error occurred. Please try again.")

if __name__ == "__main__":
    main()

