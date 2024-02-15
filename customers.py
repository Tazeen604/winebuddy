from flask import Flask, render_template, request,redirect,g,Blueprint,session
from config_db import openai, create_database_connection
import openai
import re
import mysql.connector
from bs4 import BeautifulSoup
import os
customers_bp = Blueprint('customers', __name__)
openai.api_key = "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"
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
        if wine_option == "1":
            query = "SELECT PROMPT_TXT_1 FROM ai_cstmr WHERE AI_CSTMR_START_TXT LIKE %s"
            cursor.execute(query, ('%' + customer_name + '%',))
            cstmr_result = cursor.fetchone()
            prompt_result=cstmr_result["PROMPT_TXT_1"]
            prompt_result=str(prompt_result)
        elif wine_option == "2":
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
            {"role": "system", "content": "You are WineBuddy,and BeerBudy the Virtual Sommelier for wine and beer.You can recommend wine or beer as asked"},
            {"role": "system", "content": f'{prompt_result}? {user_input} also Please return response in tabular format'},        
        ] 
        chatbot_response = get_chatbot_response(conversation)
        print("response"+chatbot_response)
        matched_varietals = []
        query = "SELECT VRTL_NM,VRTL_KEY FROM ai_vrtl"                
        cursor.execute(query)
        matched_varietals = cursor.fetchall()
        if chatbot_response is not None:
            tabular_pattern = re.compile(r'\|')
            if tabular_pattern.search(chatbot_response):
        # Split the data into lines
                lines = chatbot_response.strip().split('\n')
                start_index = next((index for index, line in enumerate(lines) if '|' in line), None)
                if start_index is not None:
                    headers = [header.strip() for header in lines[start_index].split('|') if header.strip()]
                    data_lines = [line.strip() for line in lines[start_index + 2:-1]]
                else:
                    print("Table not found in the response.")
# Create HTML table
                html_table = "<table>\n<thead>\n"
                html_table += "".join([f"<th>{header}</th>\n" for header in headers])
                html_table += "\n</thead><tbody>\n"
                for line in data_lines:
                    if '---' in line:
                        continue
                    columns = [column.strip() for column in line.split('|') if column.strip()]
    # Check if the current column is the first column
                    if columns and columns[0]:
        # Check if the first column matches any item in matched_varietals
                        print("first coloumn"+columns[0])
                        matched = next((item for item in matched_varietals if item['VRTL_NM'].strip().lower() == columns[0].strip().lower()), None)
                        if matched:
                            link = f'<a href="/restaurants?key={matched["VRTL_KEY"]}">{matched["VRTL_NM"]}</a>'
                            columns[0] = link            
                    html_table += "<tr>\n"
                    html_table += "".join([f"<td>{column}</td>\n" for column in columns])
                    html_table += "</tr>\n"
                html_table += "</tbody>\n</table>"
                print("html table" + html_table)
                print("first if")
                return render_template("chatGPT_response_table.html", token=1,var=html_table)
            else:
                print("2nd if")
        #for heading in headings:
                formatted_response = chatbot_response
                for varietal, varietal_key in matched_varietals:
                    varietal_link = f'<a href="/restaurants?key={varietal_key}">{varietal}</a>'
                    formatted_response = formatted_response.replace(varietal, varietal_link, 1)
                paragraphs_with_links = formatted_response.split('\n\n')
                #print(paragraphs_with_links)
                return render_template("chatGPT_response_table.html",paragraphs_with_links=paragraphs_with_links)                
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
    print(cstmr_key)
    try:
        selr_key=[]
        db_connection = create_database_connection()
        cursor = db_connection.cursor(dictionary=True)
        query="""SELECT distinct WINE_SELR.* FROM CSTMR_WIN_SELR JOIN AI_CSTMR ON CSTMR_WIN_SELR.AI_CSTMR_KEY = AI_CSTMR.AI_CSTMR_KEY JOIN WINE_SELR ON CSTMR_WIN_SELR.WIN_SELR_KEY = WINE_SELR.WINE_SELR_KEY WHERE AI_CSTMR.AI_CSTMR_KEY = %s AND CSTMR_WIN_SELR.ChatGPT_ACTV_IND = 'Y'"""
        print(query)
        cursor.execute(query, (cstmr_key,))
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
