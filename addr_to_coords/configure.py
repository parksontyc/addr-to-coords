import os

from dotenv import load_dotenv
import requests


url = 'https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token'
headers = {'content-type': 'application/x-www-form-urlencoded'}
load_dotenv()

data = {
    'grant_type': 'client_credentials',
    'client_id': f'{os.getenv("client_id")}',
    'client_secret': f'{os.getenv("client_secret")}'
}

response = requests.post(url, headers=headers, data=data)
print(response.json())
token = response.json()['access_token']
