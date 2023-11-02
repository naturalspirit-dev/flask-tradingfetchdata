# Import Libraries 
import os
import importlib

# Get the current directory's name
current_directory = os.path.basename(os.path.dirname(os.path.abspath(__file__)))

# Get all files.
views = [f for f in os.listdir(os.path.dirname(os.path.abspath(__file__))) if f.endswith(".py") and f != "__init__.py"]

# Import all files from the current directory.
for view in views:
    # Construct the module name
    module_name = f"{current_directory}.{view[:-3]}"
    
    # Dynamically import the module
    importlib.import_module(module_name)
    
    print(f'App imported {view} successfully as {module_name}.')
