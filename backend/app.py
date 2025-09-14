from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import traceback
import json
from datetime import datetime
from typing import List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Verde API",
    description="Vegetarian recipe generation API for HackMIT 2025",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
app.mount("/static", StaticFiles(directory="../frontend"), name="static")

# Pydantic models for request/response
class RecipeRequest(BaseModel):
    dish_name: str
    original_recipe: str = ""
    filters: list[str] = []

class RecipeResponse(BaseModel):
    original_recipe: str
    vegetarian_recipe: str
    success: bool
    error_message: str = None

class RatingRequest(BaseModel):
    recipe_name: str
    rating: int  # 1-5 stars
    user_name: Optional[str] = "Anonymous"
    comment: Optional[str] = ""

class RatingResponse(BaseModel):
    success: bool
    message: str
    average_rating: Optional[float] = None
    total_ratings: Optional[int] = None

class RecipeRating(BaseModel):
    recipe_name: str
    rating: int
    user_name: str
    comment: str
    timestamp: str

# Rating storage functions
RATINGS_FILE = "ratings.json"

def load_ratings():
    """Load ratings from JSON file"""
    try:
        if os.path.exists(RATINGS_FILE):
            with open(RATINGS_FILE, 'r') as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"Error loading ratings: {e}")
        return []

def save_ratings(ratings):
    """Save ratings to JSON file"""
    try:
        with open(RATINGS_FILE, 'w') as f:
            json.dump(ratings, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving ratings: {e}")
        return False

def get_recipe_stats(recipe_name):
    """Get rating statistics for a recipe"""
    ratings = load_ratings()
    recipe_ratings = [r for r in ratings if r['recipe_name'] == recipe_name]
    
    if not recipe_ratings:
        return 0.0, 0
    
    total_rating = sum(r['rating'] for r in recipe_ratings)
    average_rating = total_rating / len(recipe_ratings)
    return round(average_rating, 1), len(recipe_ratings)

@app.get("/")
async def serve_frontend():
    """Serve the main frontend page"""
    return FileResponse("../frontend/index.html")

@app.get("/recipes")
async def serve_recipes():
    """Serve the recipes page"""
    return FileResponse("../frontend/recipes.html")

@app.get("/index.css")
async def serve_css():
    """Serve the CSS file"""
    return FileResponse("../frontend/index.css")

@app.post("/generate-recipe", response_model=RecipeResponse)
async def generate_recipe(request: RecipeRequest):
    """API endpoint to generate vegetarian recipes using AI pipeline"""
    try:
        print(f"Received request: dish_name='{request.dish_name}', original_recipe='{request.original_recipe[:50]}...', filters={request.filters}")
        
        dish_name = request.dish_name.strip()
        original_recipe = request.original_recipe.strip()
        restrictions = request.filters  # This is the list of checked dietary restrictions
        
        if not dish_name:
            raise HTTPException(status_code=400, detail="Please provide a dish name")
        
        # If no original recipe provided, create a basic one
        if not original_recipe:
            original_recipe = f"Recipe for {dish_name}"
        
        # Ensure we have at least vegetarian as a restriction
        if not restrictions:
            restrictions = ["vegetarian"]
        
        print(f"Processing recipe: {original_recipe[:100]}...")
        print(f"Dietary restrictions: {restrictions}")
        
        # Import here to catch import errors
        try:
            from AIs import vegify
        except Exception as import_error:
            print(f"Import error: {import_error}")
            raise Exception(f"Failed to import AI module: {import_error}")
        
        # Use the AI pipeline to convert the recipe with restrictions
        print("Calling vegify with restrictions...")
        vegetarian_recipe = vegify(original_recipe, restrictions)
        print(f"Got result: {vegetarian_recipe[:100]}...")
        
        return RecipeResponse(
            original_recipe=original_recipe,
            vegetarian_recipe=vegetarian_recipe,
            success=True
        )
    
    except Exception as e:
        error_msg = str(e)
        print(f"Error in generate_recipe: {error_msg}")
        print(f"Traceback: {traceback.format_exc()}")
        
        return RecipeResponse(
            original_recipe=request.original_recipe if request.original_recipe else "",
            vegetarian_recipe="",
            success=False,
            error_message=error_msg
        )

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Verde API is running!"}

@app.get("/api/debug")
async def debug_info():
    """Debug endpoint to check system status"""
    debug_info = {
        "working_directory": os.getcwd(),
        "api_key_set": bool(os.environ.get("CEREBRAS_API_KEY")),
        "context_files": {}
    }
    
    context_files = [
        'contexts/prep_ai_context.txt',
        'contexts/brainstorm_ai_context.txt', 
        'contexts/integration_ai_context.txt',
        'contexts/checker_ai_context.txt'
    ]
    
    for file_path in context_files:
        debug_info["context_files"][file_path] = os.path.exists(file_path)
    
    try:
        from AIs import vegify
        debug_info["ai_import"] = "success"
    except Exception as e:
        debug_info["ai_import"] = str(e)
    
    return debug_info

@app.post("/api/rate-recipe", response_model=RatingResponse)
async def rate_recipe(request: RatingRequest):
    """API endpoint to rate a recipe"""
    try:
        # Validate rating
        if request.rating < 1 or request.rating > 5:
            raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
        
        # Load existing ratings
        ratings = load_ratings()
        
        # Create new rating
        new_rating = {
            "recipe_name": request.recipe_name,
            "rating": request.rating,
            "user_name": request.user_name or "Anonymous",
            "comment": request.comment or "",
            "timestamp": datetime.now().isoformat()
        }
        
        # Add to ratings list
        ratings.append(new_rating)
        
        # Save ratings
        if save_ratings(ratings):
            # Get updated stats
            avg_rating, total_ratings = get_recipe_stats(request.recipe_name)
            
            return RatingResponse(
                success=True,
                message="Rating submitted successfully!",
                average_rating=avg_rating,
                total_ratings=total_ratings
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to save rating")
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in rate_recipe: {e}")
        return RatingResponse(
            success=False,
            message=f"Error submitting rating: {str(e)}"
        )

@app.get("/api/recipe-ratings/{recipe_name}")
async def get_recipe_ratings(recipe_name: str):
    """Get all ratings for a specific recipe"""
    try:
        ratings = load_ratings()
        recipe_ratings = [r for r in ratings if r['recipe_name'] == recipe_name]
        
        avg_rating, total_ratings = get_recipe_stats(recipe_name)
        
        return {
            "recipe_name": recipe_name,
            "ratings": recipe_ratings,
            "average_rating": avg_rating,
            "total_ratings": total_ratings
        }
    
    except Exception as e:
        print(f"Error getting recipe ratings: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving ratings: {str(e)}")

@app.get("/api/all-ratings")
async def get_all_ratings():
    """Get all ratings grouped by recipe"""
    try:
        ratings = load_ratings()
        
        # Group by recipe
        recipe_stats = {}
        for rating in ratings:
            recipe_name = rating['recipe_name']
            if recipe_name not in recipe_stats:
                recipe_stats[recipe_name] = {
                    "recipe_name": recipe_name,
                    "ratings": [],
                    "average_rating": 0.0,
                    "total_ratings": 0
                }
            recipe_stats[recipe_name]["ratings"].append(rating)
        
        # Calculate stats for each recipe
        for recipe_name, stats in recipe_stats.items():
            avg_rating, total_ratings = get_recipe_stats(recipe_name)
            stats["average_rating"] = avg_rating
            stats["total_ratings"] = total_ratings
        
        return {"recipes": list(recipe_stats.values())}
    
    except Exception as e:
        print(f"Error getting all ratings: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving ratings: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
