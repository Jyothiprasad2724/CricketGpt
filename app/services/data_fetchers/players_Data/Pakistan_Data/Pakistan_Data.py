import requests
import pandas as pd
from bs4 import BeautifulSoup

def fetch_players(country_code="Pak", comp="T", current="F", sort="Name"):
    url = "https://www.howstat.com/Cricket/Statistics/Players/PlayerCountryList.asp"
    params = {
        "Country": country_code,
        "Comp": comp,
        "Current": current,
        "SortOrder": sort
    }

    response = requests.get(url, params=params)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', class_='TableLined')
    
    if table is None:
        print(f"No table found for {country_code} - {comp}")
        return pd.DataFrame()

    rows = table.find_all('tr')
    data = []
    for row in rows:
        cols = [col.get_text(strip=True) for col in row.find_all(['td', 'th'])]
        if cols:
            data.append(cols)

    df = pd.DataFrame(data[1:], columns=data[0])
    df['Country'] = country_code
    df['Format'] = comp
    return df


def save_country_format_data():
    country_codes = ['Pak']
    comp_format_map = {'T': 'test', 'O': 'odi', 'W': 't20'}

    for country in country_codes:
        for comp_code, format_name in comp_format_map.items():
            print(f"Fetching data for {country} - {format_name.upper()}...")
            df = fetch_players(country_code=country, comp=comp_code)
            if not df.empty:
                filename = f"app\services\data_fetchers\players_Data\Pakistan_Data\{country.lower()}_{format_name}.csv"
                df.to_csv(filename, index=False)
                
            else:
                print(f"No data found for {country} - {format_name.upper()}")


if __name__ == '__main__':
    save_country_format_data()
