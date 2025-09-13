from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import traceback
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

@app.get("/")
async def serve_frontend():
    """Serve the main frontend page"""
    return FileResponse("../frontend/index.html")

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

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
