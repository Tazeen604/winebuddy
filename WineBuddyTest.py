from flask import Flask, render_template, request,redirect,g
import openai
import re
import mysql.connector
app = Flask(__name__)
openai.api_key = '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'
db_connection = mysql.connector.connect(
    host="localhost",
    user="qrvino",
    password="Jorsha777$",
    database="qrvino"
)

def get_chatbot_response(messages):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    return response.choices[0].message["content"]


def extract_clickable_headings(response):
    headings = re.findall(r'(\w+(?:\/\w+)?)\: (?:.|\n)+?(?=\n\n|$)', response)
    formatted_response = re.sub(r'(\w+(?:\/\w+)?)\: ((?:.|\n)+?)(?=\n\n|$)', '- <a href="#\\1">\\1</a>: \\2<br>', response)
    return formatted_response, headings

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user_input = request.form.get("user_input")
        wine_option = request.form.get('wine_option')
       
        return redirect("/chatGPT_response?chatbot_input=" + user_input + "&chatbot_radio=" + wine_option)
    return render_template("index.html")
@app.route("/chatGPT_response")
def chatGPT_response():
    user_input = request.args.get("chatbot_input", "")
    wine_option = request.args.get("chatbot_radio", "")
    conversation = [
            {"role": "system", "content": "You are WineBuddy, the Virtual Sommelier."},
            {"role": "system", "content": f'According to famous sommeliers, what wine pairs with {user_input}?\n- {wine_option}'},
            
        ]
    chatbot_response = get_chatbot_response(conversation)
    #formatted_response, headings = extract_clickable_headings(chatbot_response)
    
    matched_varietals = []
        
        # Query the database to get varietals that match the headings
    if db_connection.is_connected():
        cursor = db_connection.cursor()
        #for heading in headings:
        query = "SELECT VRTL_NM,VRTL_KEY FROM vrtl"
        cursor.execute(query)
        matched_varietals = cursor.fetchall()
    formatted_response = chatbot_response
    for varietal, varietal_key in matched_varietals:
        varietal_link = f'<a href="/restaurants?key={varietal_key}">{varietal}</a>'
        formatted_response = formatted_response.replace(varietal, varietal_link, 1)

    # Split response into paragraphs while preserving links
    paragraphs_with_links = formatted_response.split('\n\n')

    return render_template("chatGPT_response.html", paragraphs_with_links=paragraphs_with_links)

@app.route("/restaurants")
def restaurants():
    key = request.args.get("key")
    
    if db_connection.is_connected():
        cursor = db_connection.cursor(dictionary=True)
        query = "SELECT RSTRNT_NM,RSTRNT_KEY FROM RSTRNT WHERE ChatGPT_IND = 'Y'"
        cursor.execute(query)
        restaurants = cursor.fetchall()
        return render_template("restaurants.html", restr=restaurants, key_value=key)


@app.route("/external_URL", methods=["GET", "POST"])
def external_URL():
    if request.method == "POST":
        selected_restaurant_key = request.form.get("selected_restaurant")
        keyValue = request.form.get("keyvalue")
        print(keyValue)
            # Replace your_vrtl_key_here with the appropriate value          
            # Get the target URL using the separate function
        target_url = get_target_url(selected_restaurant_key,keyValue)
        print(target_url)
        if target_url:
            return redirect(target_url)


def get_target_url(restaurant_key, vrtl_key):
    if db_connection.is_connected():
        cursor = db_connection.cursor(dictionary=True)
        query = """
            SELECT AFLT_VTRL_URL FROM aflt_vtrl_url 
            WHERE RSTRNT_KEY = %s AND VRTL_KEY = %s
        """
        cursor.execute(query, (restaurant_key, vrtl_key))
        url_result = cursor.fetchone()
        
        if url_result:
            return url_result["AFLT_VTRL_URL"]
    
    return None

if __name__ == "__main__":
    app.run(debug=True)