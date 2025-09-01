from supabase import create_client
import os
from dotenv import load_dotenv

# Load .env file from project root
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
APP_ORIGIN = os.getenv("APP_ORIGIN")


url = "https://fvikvdzkdhxyoljfyoam.supabase.co"
api = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZ2aWt2ZHprZGh4eW9samZ5b2FtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTU1MTM0NzgsImV4cCI6MjA3MTA4OTQ3OH0.t5t4i3_3DtvILbEoTQxyJ5uZdQbl2D02657HvFONQAw"

db = create_client(url, api)