
import requests

url = "http://127.0.0.1:5000/api/menu"

new_item = {
    "category_id": 1,
    "item_name": "BBQ Pizza",
    "description": "Delicious BBQ pizza",
    "price": 15.99
}

response = requests.post(url, json=new_item)

print("Status:", response.status_code)
print("Response:", response.json())
