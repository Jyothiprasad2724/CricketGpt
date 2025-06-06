import sqlite3
import pandas as pd 

def load_csv(file_path):
    df = pd.read_csv(file_path)
    return df


def clean_data(df):
    df.drop_duplicates(inplace=True)
    df.dropna(how='all', inplace=True)

    df.columns = [col.strip().replace(" ", "_").lower() for col in df.columns]
    df['format'] = df['format'].map({'T': 'Test', 'O': 'ODI', 'W': 'T20'})
    return df 

def store_in_db(db_path, df, table_name):
    conn = sqlite3.connect(db_path)
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    print(f"Stored DataFrame to {table_name} table in {db_path}")
    conn.close()



def main():
    df_test = load_csv(r"C:\Users\jyothi.p.kommuru\Downloads\CricketGpt Project\CricketGpt\app\services\data_fetchers\Test_Data\all_teams_test_data.csv")
    df_odi = load_csv(r"C:\Users\jyothi.p.kommuru\Downloads\CricketGpt Project\CricketGpt\app\services\data_fetchers\ODI_Data\all_teams_ODI_data.csv")
    df_t20 = load_csv(r"C:\Users\jyothi.p.kommuru\Downloads\CricketGpt Project\CricketGpt\app\services\data_fetchers\T20_DATA\all_teams_T20_data.csv")
    
    df_test = clean_data(df_test)
    df_odi = clean_data(df_odi)
    df_t20 = clean_data(df_t20)

    db_path = r'C:\Users\jyothi.p.kommuru\Downloads\CricketGpt Project\CricketGpt\app\Database\cricket_stats.db'
    store_in_db(db_path, df_test, 'test_stats')
    store_in_db(db_path, df_odi, 'odi_stats')
    store_in_db(db_path, df_t20, 't20_stats')

    return df_test,df_odi,df_t20

if __name__ == "__main__":
    main()