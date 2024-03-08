# Provided tabular data
import re
from config_db import create_database_connection
chatbot_response = """
Here's an example of a table format based on your request:

| Varietal     | Description                                                | Best Countries/Regions                         | Wine and Beer Pairing                           |
|--------------|------------------------------------------------------------|------------------------------------------------|-------------------------------------------------|
| Chardonnay   | Full-bodied white wine with notes of citrus and oak       | Balaton-felvidék, USA (California)           | Grilled chicken, seafood, light cheeses         |
| Pinot Noir   | Light to medium-bodied red wine with red fruit flavors    | France (Burgundy), USA (Oregon)               | Salmon, duck, lamb, mushrooms                  |
| Cabernet Sauvignon | Full-bodied red wine with black fruit and oak flavors | USA (California), Australia, Chile           | Steak, lamb, aged cheeses                      |
| Sauvignon Blanc | Crisp white wine with herbal and citrus notes         | New Zealand (Marlborough), France (Loire Valley) | Goat cheese, seafood, salads, sushi            |
| IPA (India Pale Ale) | Hoppy beer with citrus and floral notes               | USA (West Coast), England (Traditional)        | Spicy foods, burgers, strong cheeses           |
| Stout        | Dark beer with roasted malt and chocolate flavors         | Aegean, USA (Imperial Stouts)               | Beef stew, oysters, chocolate desserts         |
| Pilsner      | Crisp and refreshing beer with a slight hoppy bitterness  | Germany (Pilsen), Czech Republic             | Grilled fish, salads, light appetizers         |

Please note that wine and beer pairings can vary greatly based on personal taste preferences and specific dishes. These recommendations are general guidelines and may not suit every individual's palate.
Note: The popularity score is subjective and based on general preferences."""
matched_varietals = []
cl=0
db_connection = create_database_connection()
cursor = db_connection.cursor(dictionary=True)
query = "SELECT VRTL_NM,VRTL_KEY FROM ai_vrtl"                
cursor.execute(query)
matched_varietals = cursor.fetchall()
query = "SELECT CNTRGN_KEY,CNTRGN_NM FROM cntrgn"                
cursor.execute(query)
matched_regions = cursor.fetchall()
headers=[]
data_lines=[]
if chatbot_response is not None:
    matched_column_no = None
    tabular_pattern = re.compile(r'\|')
    if tabular_pattern.search(chatbot_response):
        # Split the data into lines
        lines = chatbot_response.strip().split('\n')
        start_index = next((index for index, line in enumerate(lines) if '|' in line), None)
       # if start_index is not None:
        headers = [header.strip() for header in lines[start_index].split('|') if header.strip()]
        data_lines = [line.strip() for line in lines[start_index + 2:-1]]
        target_words = ["regions", "countries", "regions/countries","countries/regions"]    
        # Find the first matched column
            
        for i, header in enumerate(headers, 1):
            for word in target_words:
                if word in header.lower():
                    matched_column_no = i
                    break  # Once a match is found, stop searching 
        # Print the matched column if found
            if matched_column_no is not None:
                print(f"Matched column: Column {matched_column_no}: {headers[matched_column_no-1]}")
                cl=matched_column_no-1
                break
            else:
                print("No column matched with the specified words.")
       # else:
           # print("Table not found in the response.")
# Create HTML table
        html_table = "<table>\n<thead>\n"
        html_table += "".join([f"<th>{header}</th>\n" for header in headers])
        html_table += "\n</thead><tbody>\n"

        for line in data_lines:
            if '---' in line:
                continue
            columns = [column.strip() for column in line.split('|') if column.strip()]
            print(len(columns))
            if len(columns)<=0:
                break
            print(cl)
    # Check if the current column is the first column
            if columns and columns[0]:
        # Check if the first column matches any item in matched_varietals
                print("first coloumn"+columns[0])
                matched = next((item for item in matched_varietals if item['VRTL_NM'].strip().lower() == columns[0].strip().lower()), None)
                if matched:
                    link = f'<a href="/restaurants?key={matched["VRTL_KEY"]}">{matched["VRTL_NM"]}</a>'
                    columns[0] = link
            if cl is not None :
                print("3rd"+columns[matched_column_no-1])
                # Preprocess column_words
                column_words_processed = [word.replace(" ", "").lower().strip() for word in columns[matched_column_no-1].split(',')]

# Check if any word in column_words_processed matches any item in matched_regions after preprocessing itemreg['CNTRGN_NM']
                matched_reg = next((itemreg for itemreg in matched_regions if any(word in itemreg['CNTRGN_NM'].replace(" ", "").lower().strip() for word in column_words_processed)), None)

                if matched_reg: 
                    link_reg = f'<a href="/restaurants?key={matched_reg["CNTRGN_KEY"]}">{matched_reg["CNTRGN_NM"]}</a>'
                    columns[matched_column_no-1] = link_reg   
                    print("3rd coloumn link"+link_reg)
            else:
                print("No 3rd coloumn exist")      
            html_table += "<tr>\n"
            html_table += "".join([f"<td>{column}</td>\n" for column in columns])
            html_table += "</tr>\n"
        html_table += "</tbody>\n</table>"
        print("html table" + html_table)
        print("first if")