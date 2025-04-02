import requests

url = "http://127.0.0.1:5000/api/optimize"
data = {"tickers": ["MCFTR", "RGBITR", "MESMTR"]}

response = requests.post(url, json=data)

print("Response:", response.json())
