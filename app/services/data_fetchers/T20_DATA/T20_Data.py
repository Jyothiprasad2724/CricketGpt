import requests
import pandas as pd
from bs4 import BeautifulSoup
import os

def fetch_players(country_code="AFG", comp="T", current="F", sort="Name"):
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


def save_combined_test_data():
    country_codes = ['AFG','ENG','AUS','IND','PAK','SAF','WIN']
    comp_code = 'W'  # Test format
    combined_df = []

    for country in country_codes:
        print(f"Fetching data for {country} - T20...")
        df = fetch_players(country_code=country, comp=comp_code)
        if not df.empty:
            combined_df.append(df)
        else:
            print(f"No data found for {country} - T20")

    if combined_df:
        final_df = pd.concat(combined_df, ignore_index=True)
        output_path = r"C:\Users\jyothi.p.kommuru\Downloads\CricketGpt Project\CricketGpt\app\services\data_fetchers\T20_DATA\all_teams_T20_data.csv"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        final_df.to_csv(output_path, index=False)
        print(f"\nCombined data saved to: {output_path}")
    else:
        print("No data to save.")
    


if __name__ == '__main__':
    save_combined_test_data()
