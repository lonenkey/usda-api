# Changes and Enhancements

## 1. Added Health Score Calculation  
- Introduced a new function `calculate_health_score(nutrients)`, which computes a health score based on nutrient values.  
- The score is calculated using a formula that considers:
  - **Protein** and **fiber** (positive contribution to the score).
  - **Fat, sugar, and sodium** (negative contribution to the score).
  - Ensured the score is within the range of **0 to 100**.

## 2. Extracted and Processed Nutrient Data  
- Modified `get_food_items(food)` to extract relevant nutrient values from the API response.  
- Created a dictionary `nutrients` to store extracted nutrient values from `foodNutrients`.  
- Passed this dictionary to `calculate_health_score(nutrients)` to compute the health score.  

## 3. Displaying Health Score  
- After retrieving nutrient data, the calculated health score is displayed to the user.  
- Ensured the score is rounded to **two decimal places** for better readability.

## 4. Code Comments and Documentation  
- Added docstrings to `calculate_health_score()` to explain the purpose of the function.  
- Included inline comments to clarify logic in health score calculation and API response handling.

## Summary  
These enhancements improve the script by adding a **quantitative health evaluation** for food items, making the output more informative and user-friendly.  
