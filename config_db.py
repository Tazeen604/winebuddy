
import mysql.connector
import openai
# Set OpenAI API key
openai.api_key =''

# Create a function to establish a database connection
def create_database_connection():
    return mysql.connector.connect(
        host="localhost",
        user="admin",
        password="",
        database="qrvino_db"
    )