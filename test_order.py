
import requests

url = "http://127.0.0.1:5000/api/orders"

order = {
    "customer_id": 1,
    "items": [
        {"item_id": 1, "quantity": 1},
        {"item_id": 3, "quantity": 1}
    ]
}

response = requests.post(url, json=order)

print("Status:", response.status_code)
print("Response:", response.json())
