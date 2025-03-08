# Food Nutrition Analyzer

A Python script to retrieve nutritional data for food items from the USDA FoodData Central API and calculate a health score based on key nutrients. The health score helps users evaluate how healthy a food item is on a scale of 0 to 100.


---

## Features

- **Health Score Calculation**:  
  Evaluates food items using a formula that considers:
  - **Positive Nutrients**: Protein and fiber.
  - **Negative Nutrients**: Fat, sugar, and sodium.
  - Scores are clamped between **0 (unhealthy)** and **100 (healthy)**.

- **USDA API Integration**:  
  Fetches real-time nutritional data for branded and common foods.

- **User-Friendly Interface**:  
  Displays a list of matching foods, nutrient details, and a health score for the selected item.

- **Error Handling**:  
  Robust error handling for API timeouts, connection issues, and invalid inputs.

---

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/food-nutrition-analyzer.git
   cd food-nutrition-analyzer
   ```

2. **Install Dependencies**:  
   Ensure you have Python 3.7+ installed. No additional packages are required beyond the Python Standard Library.

3. **API Credentials**:  
   - Sign up for an API key from [USDA FoodData Central](https://fdc.nal.usda.gov/api-key-signup.html).
   - Create a `credentials.py` file in the project directory with your API URL and key:
     ```python
     url = "https://api.nal.usda.gov/fdc/v1/foods/search?api_key=YOUR_API_KEY"
     ```

---

## Usage

1. **Run the Script**:
   ```bash
   python usda1.py
   ```

2. **Search for a Food Item**:  
   Enter the name of the food you want to analyze:
   ```
   What food are you looking for: apple
   ```

3. **Select an Item**:  
   The script will display a list of matching foods. Choose one by entering its index:
   ```
   Matching foods:
   0 Apple (Brand: XYZ)
   1 Apple Juice (Brand: ABC)
   Which item would you like to see: 0
   ```

4. **View Results**:  
   The script will display nutrient details and the health score:
   ```
   Nutrients for: Apple (Brand: XYZ)
   Protein: 0.3 g
   Fat: 0.2 g
   Sugar: 10 g
   Fiber: 2.4 g
   Sodium: 1 mg
   Health Score: 78.5/100
   ```

---

## Health Score Formula

The health score is calculated using the following formula:  
```
Score = (Protein × 2 + Fiber × 1.5) − (Fat + Sugar × 2 + Sodium × 0.5)
```
- **Positive Contributions**: Protein and fiber increase the score.
- **Negative Contributions**: Fat, sugar, and sodium decrease the score.
- The final score is clamped between **0** and **100**.

---

## Example Output

```plaintext
What food are you looking for: oatmeal
Matching foods:
0 Oatmeal (Brand: Quaker)
1 Oatmeal Cookies (Brand: ABC)

Which item would you like to see: 0

Nutrients for: Oatmeal (Brand: Quaker)
Protein: 5.0 g
Fat: 3.0 g
Sugar: 1.2 g
Fiber: 4.0 g
Sodium: 150 mg
Health Score: 82.3/100
```

---

## Testing

- **Unit Tests**:  
  Run tests for the health score calculation:
  ```bash
  python -m unittest test_health_score.py
  ```
  Example test cases include:
  - High-protein, low-fat foods.
  - Edge cases (e.g., zero calories, missing nutrients).

- **Manual Testing**:  
  Tested with common foods (e.g., apples, oatmeal, chicken breast) to validate accuracy.

---
