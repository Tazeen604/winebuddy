# Provided tabular data
import re
from config_db import create_database_connection
tabular_data = """
Here are some beer recommendations that pair well with Roasted Chicken:

Varietal                      | Description                                             | Popularity Score
----------------------------- | ------------------------------------------------------- | ----------------
Amber Ale                     | A malt-forward beer with caramel and toasty flavors.    | 8.5/10
Belgian Saison                | A fruity and spicy Belgian-style ale.                   | 8/10
Pilsner                       | A crisp and refreshing lager with a light hop bitterness. | 7/10
Wheat Beer                    | A light-bodied beer with fruity and yeasty flavors.     | 7.5/10
Pale Ale                      | A hop-forward beer with citrusy and floral notes.       | 8/10

Note: The popularity score is subjective and based on general preferences."""
matched_varietals = []
db_connection = create_database_connection()
cursor = db_connection.cursor(dictionary=True)
query = "SELECT VRTL_NM,VRTL_KEY FROM ai_vrtl"                
cursor.execute(query)
matched_varietals = cursor.fetchall()
tabular_pattern = re.compile(r'\|.*\|')
headers=[]
data_lines=[]

if tabular_pattern.search(tabular_data):
    lines = tabular_data.strip().split('\n')
    start_index = next((index for index, line in enumerate(lines) if '|' in line), None)
    print(start_index)
    if start_index is not None:
        headers = [header.strip() for header in lines[start_index].split('|') if header.strip()]
        data_lines = [line.strip() for line in lines[start_index + 2:-1]]
    else:
        print("Table not found in the response.")
        #print(data_lines)
# Create HTML table
    html_table = "<table>\n<thead>\n"
    html_table += "".join([f"<th>{header}</th>\n" for header in headers])
    html_table += "\n</thead><tbody>\n"
    for line in data_lines:
        if '---' in line:
            continue
        columns = [column.strip() for column in line.split('|') if column.strip()]
        #print("Line:", line)
        print("all Column:", columns)
    # Check if the current column is the first column
        if columns and columns[0]:
        # Check if the first column matches any item in matched_varietals
            matched = next((item for item in matched_varietals if item['VRTL_NM'].strip().lower() == columns[0].strip().lower()), None)
            print(matched)
            if matched:
                link = f'<a href="/restaurants?key={matched["VRTL_KEY"]}">{matched["VRTL_NM"]}</a>'
                columns[0] = link           
            else:
                print("no coloumn zero")
        html_table += "<tr>\n"
        html_table += "".join([f"<td>{column}</td>\n" for column in columns])
        html_table += "</tr>\n"

    html_table += "</tbody>\n</table>"
    print("htmltable" + html_table)
else:
    print("2nd if")

