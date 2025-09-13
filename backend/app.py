from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Verde API",
    description="Vegetarian recipe generation API for HackMIT 2025",
    version="1.0.0"
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class RecipeRequest(BaseModel):
    dish: str

class RecipeResponse(BaseModel):
    name: str
    ingredients: list[str]
    instructions: list[str]
    cook_time: str
    servings: int
    note: str = None

# Sample vegetarian recipe database
VEGETARIAN_RECIPES = {
    "pasta": {
        "name": "Creamy Mushroom Pasta",
        "ingredients": [
            "8 oz pasta",
            "2 cups mixed mushrooms",
            "3 cloves garlic",
            "1 cup heavy cream",
            "1/2 cup parmesan cheese",
            "2 tbsp olive oil",
            "Salt and pepper to taste"
        ],
        "instructions": [
            "Cook pasta according to package directions",
            "Heat olive oil in a large pan",
            "Add mushrooms and garlic, cook until tender",
            "Add cream and simmer until thickened",
            "Toss with pasta and parmesan",
            "Season with salt and pepper"
        ],
        "cook_time": "20 minutes",
        "servings": 4
    },
    "burger": {
        "name": "Black Bean Veggie Burger",
        "ingredients": [
            "1 can black beans",
            "1/2 cup breadcrumbs",
            "1/4 cup diced onion",
            "2 cloves garlic",
            "1 egg (or flax egg for vegan)",
            "1 tsp cumin",
            "Salt and pepper to taste"
        ],
        "instructions": [
            "Mash black beans in a bowl",
            "Add breadcrumbs, onion, garlic, and spices",
            "Form into patties",
            "Cook in a pan for 4-5 minutes per side",
            "Serve on buns with your favorite toppings"
        ],
        "cook_time": "15 minutes",
        "servings": 4
    }
}

def generate_vegetarian_recipe(dish_name):
    """Generate a vegetarian version of the requested dish"""
    dish_lower = dish_name.lower()
    
    # Check if we have a direct match
    if dish_lower in VEGETARIAN_RECIPES:
        return VEGETARIAN_RECIPES[dish_lower]
    
    # Generate a custom recipe based on the dish
    return {
        "name": f"Vegetarian {dish_name.title()}",
        "ingredients": [
            "2 cups vegetables of choice",
            "1 cup plant-based protein (tofu, tempeh, or beans)",
            "2 tbsp olive oil",
            "3 cloves garlic",
            "1 tsp herbs and spices",
            "Salt and pepper to taste"
        ],
        "instructions": [
            "Prepare your vegetables by washing and chopping",
            "Heat olive oil in a pan over medium heat",
            "Add garlic and cook until fragrant",
            "Add vegetables and cook until tender",
            "Add plant-based protein and seasonings",
            "Cook until heated through",
            "Serve hot and enjoy!"
        ],
        "cook_time": "25 minutes",
        "servings": 2,
        "note": f"This is a vegetarian adaptation of {dish_name}. Feel free to customize with your favorite vegetables and seasonings!"
    }

@app.post("/api/recipe", response_model=RecipeResponse)
async def get_recipe(request: RecipeRequest):
    """API endpoint to generate vegetarian recipes"""
    try:
        dish = request.dish.strip()
        
        if not dish:
            raise HTTPException(status_code=400, detail="Please provide a dish name")
        
        recipe = generate_vegetarian_recipe(dish)
        return RecipeResponse(**recipe)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Verde API is running!"}

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to Verde API!",
        "docs": "/docs",
        "health": "/api/health"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run(app, host="0.0.0.0", port=port, reload=True)
