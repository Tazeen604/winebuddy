
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