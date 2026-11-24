
import requests

url = "http://127.0.0.1:5000/api/menu/9"

updated_item = {
    "price": 17.99
}

response = requests.put(url, json=updated_item)

print("Status:", response.status_code)
print("Response:", response.json())
