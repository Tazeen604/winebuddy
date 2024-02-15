
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