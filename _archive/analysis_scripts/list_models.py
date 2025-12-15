import google.generativeai as genai
import os

# You need an API key. I'll check if one is set in env, otherwise I'll just list models without auth if possible, 
# but usually auth is needed.
# For now, I'll try to list models. If it fails due to missing API key, I'll ask the user.
try:
    for m in genai.list_models():
        print(f"name: {m.name}")
        print(f"description: {m.description}")
        print(f"supported_generation_methods: {m.supported_generation_methods}")
        print("-" * 20)
except Exception as e:
    print(f"Error: {e}")
