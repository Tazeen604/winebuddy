
import mysql.connector
import openai

# Set OpenAI API key
openai.api_key = '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'

# Create a function to establish a database connection
def create_database_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="qrvino_db"
    )