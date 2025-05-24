import os
import json
from Country_flag import CountryFlag
from Series_list import Series_list
from allmatches_list import allmatches_list
from series_info import series_info
from match_info import Match_info
from player_info import Player_info


DATA_DIR = "app\services\data_fetchers\data"
os.makedirs(DATA_DIR, exist_ok=True)

def save_json(data, filename):
    if data:
        with open(os.path.join(DATA_DIR, filename), "w") as f:
            json.dump(data, f, indent=4)
        print(f"Saved {filename}")
    else:
        print(f"No data to save for {filename}")

def run_all_fetchers():
    print("Starting API fetch...")

    save_json(CountryFlag(), "flags.json")
    save_json(Series_list(), "series.json")
    save_json(allmatches_list(), "matches.json")
    save_json(series_info(), "series.json")
    save_json(Player_info(), "player_stats.json")
    save_json(Match_info(), "match_results.json")

    print("✅ All API data fetched and saved.")

if __name__ == "__main__":
    run_all_fetchers()