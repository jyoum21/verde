import os
from cerebras.cloud.sdk import Cerebras

os.environ["CEREBRAS_API_KEY"] = "csk-4xnhky9yjn4nwnktjw3hpjwf592mkeywfcm3e3w96e5enw3h"

client = Cerebras(
    # This is the default and can be omitted
    api_key=os.environ.get("CEREBRAS_API_KEY"),
)

def vegify(input_recipe, restrictions):
  '''
  Vegify is a function that will take in a recipe and a list of restrictions (represented as strings), and return a recipe that follows the restrictions.
  '''
  
  formatted_recipe = preparation_ai(input_recipe)
  if formatted_recipe == "Not a recipe":
    return "Sorry, something went wrong here."
  suggestions = brainstorm_ai(formatted_recipe, restrictions)
  new_recipe = integration_ai(formatted_recipe, suggestions, restrictions)
  
  if checker_ai(new_recipe, restrictions):
    return new_recipe
  else:
    return "Sorry, something went wrong."

def preparation_ai(input_recipe):  
  # Load the system prompt from the text file
  with open('contexts/prep_ai_context.txt', 'r') as file:
    system_content = file.read()
  
  chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": system_content,
        },
        {
            "role": "user", 
            "content": input_recipe
        }
  ],
      model="llama-4-scout-17b-16e-instruct",
  )

  return chat_completion.choices[0].message.content

def brainstorm_ai(input_recipe, restrictions):
  with open('contexts/brainstorm_ai_context.txt', 'r') as file:
    system_content = file.read()
  
  chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": "You are the second of a series of LLMs that will taken in a recipe, and adapt it to follow different dietary restrictions. The restrictions you want to follow are " + ", ".join(restrictions) + ". " + system_content,
        },
        {
            "role": "user", 
            "content": input_recipe
        }
  ],
      model="llama-4-scout-17b-16e-instruct",
  )

  return chat_completion.choices[0].message.content

def integration_ai(input_recipe, suggestions, restrictions):
  with open('contexts/integration_ai_context.txt', 'r') as file:
    system_content = file.read()
  
  chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": "You are the second of a series of LLMs that will taken in a recipe, and adapt it to follow different dietary restrictions. The restrictions you want to follow are " + ", ".join(restrictions) + ". " + system_content,
        },
        {
            "role": "user", 
            "content": "Original recipe:\n" + input_recipe + "Suggestions for making vegetarian:\n" + suggestions
        }
  ],
      model="llama-4-scout-17b-16e-instruct",
  )

  return chat_completion.choices[0].message.content

def checker_ai(input_recipe, restrictions):
  with open('contexts/checker_ai_context.txt', 'r') as file:
    system_content = file.read()
  
  chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": "You are the fourth of a series of LLMs that will taken in a recipe, and adapt it to follow different dietary restrictions. The restrictions you want to follow are " + ", ".join(restrictions) + ". " + system_content,
        },
        {
            "role": "user", 
            "content": input_recipe
        }
  ],
      model="llama-4-scout-17b-16e-instruct",
  )

  return chat_completion.choices[0].message.content == "yes"

# Test code - commented out to avoid import errors
# with open('test.txt', 'r') as file:
#   system_content = file.read()
# print(vegify(system_content, ["vegetarian"]))
