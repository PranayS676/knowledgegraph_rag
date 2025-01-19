from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# aVQh-99TuvHMl0tGcW9gKYQaoDGJq2TG4PQoIuaR9Zg    neo4j insatance password