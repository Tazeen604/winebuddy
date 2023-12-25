varie = ["element1", "element2", "element3", "element4"]
matched_varietal = [{"VRTL_KEY": 1, "VRTL_NM": "element1"}, {"VRTL_KEY": 2, "VRTL_NM": "Element2"}, {"VRTL_KEY": 3, "VRTL_NM": "element3"}, {"VRTL_KEY": 4, "VRTL_NM": "element4"}, {"VRTL_KEY": 5, "VRTL_NM": "Element5"}, {"VRTL_KEY": 6, "VRTL_NM": "element6"}, {"VRTL_KEY": 7, "VRTL_NM": "element7"}]

# Extract elements from arr2 with their keys where the value (case-insensitive) is in arr
result = [{"VRTL_KEY": item["VRTL_KEY"], "VRTL_NM": item["VRTL_NM"]} for item in matched_varietal if item["VRTL_NM"].lower() in [elem.lower() for elem in varie]]

# Print the result
print(result)

result = [{"VRTL_KEY": item["VRTL_KEY"], "VRTL_NM": item["VRTL_NM"]} for item in matched_varietal if item["VRTL_NM"].lower() in [elem.lower() for elem in varie]]

# Convert each item into a link
links = [f'<a href="/restaurants?key={item["VRTL_KEY"]}">{item["VRTL_NM"]}</a>' for item in result]

# Print the links
for link in links:
    print(link)