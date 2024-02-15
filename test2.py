from config_db import create_database_connection
import re
response="""eWhen it comes to pairing wine with grilled chicken, Sommeliers often suggest the following options:

1. Chardonnay: A medium-bodied, oaked Chardonnay with flavors of butter and vanilla can complement the smoky and charred flavors of grilled chicken.

2. Sauvignon Blanc: This crisp and refreshing white wine with its citrus and herbaceous notes can provide a contrast to the richness of grilled chicken.

3. Pinot Noir: A light to medium-bodied red wine, such as Pinot Noir, can pair well with grilled chicken as the wine's fruity flavors can complement the flavors of the meat without overpowering it.

4. Rosé: A dry and refreshing rosé with notes of red berries can match the flavors of grilled chicken while still providing a vibrant and fresh taste.

Remember, personal preferences can vary, so it's always a good idea to experiment and find the wine that suits your own taste."""
db_connection = create_database_connection()
cursor = db_connection.cursor(dictionary=True)
query = "SELECT VRTL_NM,VRTL_KEY FROM ai_vrtl"                
cursor.execute(query)
matched_varietals = cursor.fetchall()
formatted_response = response
for i, response_string in enumerate(formatted_response):
    for varietal_dict in matched_varietals:
        varietal_link = f'<a href="/restaurants?key={varietal_dict["VRTL_KEY"]}">{varietal_dict["VRTL_NM"]}</a>'
        formatted_response = formatted_response.replace(varietal_dict["VRTL_NM"], varietal_link, 1)
paragraphs_with_links = formatted_response.split('\n\n')
print(paragraphs_with_links)