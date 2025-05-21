import requests 
import json 

API_KEY = "9139fc75-b90b-40ab-9d67-05f8caedb5b2"

def CountryFlag():
    url = f"https://api.cricapi.com/v1/countries?apikey={API_KEY}"
    res = requests.get(url)
    if res.status_code == 200:
        response = res.json()
        return response
    else:
        print(f"Error with statuscode:{res.status_code}")


if __name__ == '__main__':
    result = CountryFlag()
    if result:
        with open('data\CountryFlag_Data\countries.json', 'w') as f:
            json.dump(result, f, indent=4)

    

