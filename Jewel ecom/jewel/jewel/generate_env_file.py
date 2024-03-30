# generate_env_file.py

import os

# Read settings from settings.py
from settings import *

# Write settings to .env file
with open('.env', 'w') as env_file:
    env_file.write(f"SECRET_KEY='{SECRET_KEY}'\n")
    env_file.write(f"DEBUG={DEBUG}\n")
    env_file.write("ALLOWED_HOSTS=\n")  # Add logic to write ALLOWED_HOSTS if needed
    # Write other settings as needed

print(".env file generated successfully!")
