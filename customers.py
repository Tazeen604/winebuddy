from flask import Flask, render_template, request,redirect,g,Blueprint
from config_db import openai, create_database_connection
import openai
import re
import mysql.connector
import os
customers_bp = Blueprint('customers', __name__)
#pp = Flask(__name__)
#oenai.api_key = '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'
#db_connection = mysql.connector.connect(
   # host="167.172.29.26",
    #user="root",
   # password="Kdem*g6ka8%",
   # database="qrvino_db"
#)

@customers_bp.route('/<page_name>')
def show_image(page_name):
    try:
        # Assume you have a table 'images' with a column 'image_data'
        db_connection = create_database_connection()
        cursor = db_connection.cursor(dictionary=True)
        query = "SELECT CHTBX_LOGO_IMG, CHTBX_FRST_LINE, CHTBX_SCND_LINE FROM AI_CSTMR WHERE AI_CSTMR_START_TXT LIKE %s"
        cursor.execute(query,('%' + page_name + '%',))
        result = cursor.fetchone()   
        if result is not None:
            image_data = result['CHTBX_LOGO_IMG']
            first_line = result['CHTBX_FRST_LINE']  # Fixed column name to 'CHTBX_FRST_LINE'
            second_line_from_database = result['CHTBX_SCND_LINE']
            print(second_line_from_database)
            # Save the image to a specified folder
            static_images_folder = 'static/images'
            temp_image_filename = 'temp_image.png'  # You may want to generate a unique filename
            temp_image_path = os.path.join(static_images_folder, temp_image_filename)

            with open(temp_image_path, 'wb') as temp_image:
                temp_image.write(image_data)

            cursor.close()
            return render_template('aiCustomers.html', image_data=temp_image_filename, first_line=first_line, second_line=second_line_from_database)
        else:
            cursor.close()
            #return "Page not found"
            #print("Error:", str(e))
            #return {'error': str(e)}
            return {'page_name': page_name}
    except Exception as e:
        return f"Error: {str(e)}"
