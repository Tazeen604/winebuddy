from flask import Flask, render_template, request,redirect,g,Blueprint,session
from config_db import openai, create_database_connection
import openai
import re
import mysql.connector
import os
customers_bp = Blueprint('customers', __name__)
openai.api_key = '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'
@customers_bp.route('/<page_name>')
def show_image(page_name):
    try:
        # Assume you have a table 'images' with a column 'image_data'
        db_connection = create_database_connection()
        cursor = db_connection.cursor(dictionary=True)
        query = "SELECT AI_CSTMR_KEY,CHTBX_LOGO_IMG, CHTBX_FRST_LINE, CHTBX_SCND_LINE FROM AI_CSTMR WHERE AI_CSTMR_START_TXT LIKE %s"
        cursor.execute(query,('%' + page_name + '%',))
        result = cursor.fetchone()   
        if result is not None:
            image_data = result['CHTBX_LOGO_IMG']
            first_line = result['CHTBX_FRST_LINE']  # Fixed column name to 'CHTBX_FRST_LINE'
            second_line_from_database = result['CHTBX_SCND_LINE']
            ai_cstmr_key = result['AI_CSTMR_KEY']
            session['ai_cstmr_key'] = ai_cstmr_key
            print("session "+str(session['ai_cstmr_key']))
            print(second_line_from_database)
            # Save the image to a specified folder
            static_images_folder = 'static/images'
            temp_image_filename = 'temp_image.png'  # You may want to generate a unique filename
            temp_image_path = os.path.join(static_images_folder, temp_image_filename)
            with open(temp_image_path, 'wb') as temp_image:
                temp_image.write(image_data)

            cursor.close()
            return render_template('aiCustomers.html', image_data=temp_image_filename, first_line=first_line, second_line=second_line_from_database,customer_name=page_name)
        else:
            cursor.close()
            return {'page_name': page_name}
    except Exception as e:
        return f"Error: {str(e)}"

    ##### get chATgpt rESPONSE#################################################################################
def get_chatbot_response(messages):
    response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=messages
    )
    return response.choices[0].message["content"]
### Extract Clickable Headinngs########################################################################

#chatgpt response table###############################################################################################3
@customers_bp.route('/chatGPT_response_table', methods=['POST'])
def chatGPT_response_table():
    try:
       #if request.method == "POST":
        user_input = request.form.get("user_input")
        wine_option = request.form.get('wine_option')  
        customer_name = request.form.get('customer_name')
        db_connection = create_database_connection()
        cursor = db_connection.cursor(dictionary=True)
        print("hellooooo"+customer_name)
        if wine_option == 1:
            query = "SELECT PROMPT_TXT_1 FROM ai_cstmr WHERE AI_CSTMR_START_TXT LIKE %s"
            cursor.execute(query, ('%' + customer_name + '%',))
            cstmr_result = cursor.fetchone()
            prompt_result=cstmr_result["PROMPT_TXT_1"]
            prompt_result=str(prompt_result)
        elif wine_option == 2:
            query = "SELECT PROMPT_TXT_2 FROM ai_cstmr WHERE AI_CSTMR_START_TXT LIKE %s"
            cursor.execute(query, ('%' + customer_name + '%',))
            cstmr_result = cursor.fetchone()
            prompt_result=cstmr_result["PROMPT_TXT_2"]
            prompt_result=str(prompt_result)
        else:
            query = "SELECT PROMPT_TXT_3 FROM ai_cstmr WHERE AI_CSTMR_START_TXT LIKE %s"
            cursor.execute(query, ('%' + customer_name + '%',))
            cstmr_result = cursor.fetchone()
            prompt_result=cstmr_result["PROMPT_TXT_3"]
            prompt_result=str(prompt_result)
        conversation = [
            {"role": "system", "content": "You are WineBuddy, the Virtual Sommelier."},
            {"role": "system", "content": f'{prompt_result}? {user_input}'},        
        ] 
        chatbot_response = get_chatbot_response(conversation)
        response_lines = chatbot_response.strip().split('\n')
# Filter out lines that don't contain the expected separator '|'
        data_lines = [line for line in response_lines if '|' in line]
# Check if there are at least two lines (header and one data row)
        if len(data_lines) >= 2:
    # Extract header and data rows
            header = data_lines[0].split('|')
            data_rows = [row.split('|') for row in data_lines[2:]]
            print(data_rows)
    # Check if there are data rows
            if data_rows:
        # Extract data from rows
                varie = []
                descriptions = []
                popularity_scores = []
                for row in data_rows:
                    if all(cell.strip() == '-' for cell in row):
                        continue
            # Check if the row consists only of dashes
                    varie.append(row[0].strip())
                    descriptions.append(row[1].strip())
                    popularity_scores.append(row[2].strip())
            else:
        # Handle case when there are no data rows
                varie, descriptions, popularity_scores = [], [], []
        else:
    # Handle case when there are not enough lines in the response
            varie, descriptions, popularity_scores = [], [], []
        if chatbot_response is not None:
    #formatted_response, headings = extract_clickable_headings(chatbot_response)
            matched_varietals = []
            query = "SELECT VRTL_NM,VRTL_KEY FROM ai_vrtl"
            cursor.execute(query)
            matched_varietals = cursor.fetchall()
            #print(matched_varietals)
            formatted_response = chatbot_response
            result = [{"VRTL_KEY": item["VRTL_KEY"], "VRTL_NM": item["VRTL_NM"]} for item in matched_varietals if item["VRTL_NM"].strip().lower() in [elem.strip().lower() for elem in varie]]
# Print the result
            print(result)
            #result = [{"VRTL_KEY": item["VRTL_KEY"], "VRTL_NM": item["VRTL_NM"]} for item in matched_varietals if item["VRTL_NM"].lower() in [elem.lower() for elem in varie]]
# Convert each item into a link
            links = [f'<a href="/restaurants?key={item["VRTL_KEY"]}">{item["VRTL_NM"]}</a>' for item in result]
            return render_template("chatGPT_response_table.html", var=links,desc=descriptions,score=popularity_scores)
        else:
            return "No response from chatbot"
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        # Make sure to close the cursor and database connection
        cursor.close()
        db_connection.close()
# restaurants#########################################################################################
@customers_bp.route('/restaurants')
def restaurants():
    ai_vrtl_key = request.args.get("key")
    session['ai_vrtl_key'] = ai_vrtl_key
    cstmr_key=session.get('ai_cstmr_key')
    try:
        selr_key=[]
        db_connection = create_database_connection()
        cursor = db_connection.cursor(dictionary=True)
        query="SELECT WINE_SELR.*,CSTMR_WIN_SELR.* FROM CSTMR_WIN_SELR JOIN AI_CSTMR ON CSTMR_WIN_SELR.AI_CSTMR_KEY = AI_CSTMR.AI_CSTMR_KEY JOIN WINE_SELR ON CSTMR_WIN_SELR.WIN_SELR_KEY = WINE_SELR.WINE_SELR_KEY WHERE CSTMR_WIN_SELR.ChatGPT_ACTV_IND = 'Y'"
        cursor.execute(query)
        restaurants = cursor.fetchall()
        return render_template("restaurants.html", restr=restaurants, vrtl_key=ai_vrtl_key)
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        # Make sure to close the cursor and database connection
        cursor.close()
        db_connection.close()
#external URL########################################################################################################

@customers_bp.route("/external_URL", methods=["GET", "POST"])
def external_URL():
    if request.method == "POST":
        selected_restaurant_key = request.form.get("selected_restaurant")
        keyValue = request.form.get("vrtlkey")
            # Replace your_vrtl_key_here with the appropriate value          
            # Get the target URL using the separate function
        target_url = get_target_url(selected_restaurant_key,keyValue)
        if target_url:
            return redirect(target_url)
        else:
            # Handle the case where target_url is not available
            return """
                <html>
                <head>
                    <script>
                        alert("Target URL not found");
                        window.location.href = "/restaurants";  // Redirect to the restaurants URL
                    </script>
                </head>
                <body>
                    <p>If you are not redirected, <a href="/restaurants">click here</a>.</p>
                </body>
                </html>
            """, 404
    else:
        # Handle GET request or other methods
        return "Invalid request method", 405

def get_target_url(restaurant_key, vrtl_key):
    db_connection = create_database_connection()
    cursor = db_connection.cursor(dictionary=True)
    query = """
        SELECT AFLT_VTRL_URL FROM aflt_vtrl_url 
        WHERE WINE_SELR_KEY = %s AND VRTL_KEY = %s
        """
    cursor.execute(query, (restaurant_key, vrtl_key))
    url_result = cursor.fetchone()
    if url_result:
        return url_result["AFLT_VTRL_URL"]
