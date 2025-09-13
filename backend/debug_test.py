import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=== DEBUG TEST ===")
print(f"Current working directory: {os.getcwd()}")
print(f"Python path: {sys.path}")

# Test 1: Check if AIs module can be imported
try:
    from AIs import vegify
    print("✓ Successfully imported vegify from AIs")
except Exception as e:
    print(f"✗ Failed to import AIs: {e}")
    sys.exit(1)

# Test 2: Check if context files exist
context_files = [
    'contexts/prep_ai_context.txt',
    'contexts/brainstorm_ai_context.txt', 
    'contexts/integration_ai_context.txt',
    'contexts/checker_ai_context.txt'
]

for file_path in context_files:
    if os.path.exists(file_path):
        print(f"✓ Found {file_path}")
    else:
        print(f"✗ Missing {file_path}")

# Test 3: Check API key
api_key = os.environ.get("CEREBRAS_API_KEY")
if api_key:
    print(f"✓ API key found: {api_key[:10]}...")
else:
    print("✗ No API key found")

# Test 4: Simple vegify test
try:
    test_recipe = "Recipe for spaghetti bolognese with ground beef"
    print(f"\nTesting with: {test_recipe}")
    result = vegify(test_recipe)
    print(f"✓ vegify result: {result[:100]}...")
except Exception as e:
    print(f"✗ vegify failed: {e}")
    import traceback
    traceback.print_exc()
