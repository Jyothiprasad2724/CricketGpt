import pandas as pd 
import numpy as np
import faiss
import pickle


def load_csv(file_path):
    df = pd.read_csv(file_path)
    return df 


def clean_data(df):
    df.drop_duplicates(inplace=True)
    df.dropna(how='all', inplace=True)

    df.columns = [col.strip().replace(" ", "_").lower() for col in df.columns]
    df['format'] = df['format'].map({'T': 'Test', 'O': 'ODI', 'W': 'T20'})
    numeric_cols = ['matches', 'inns', 'runs', '100s',  
                    'bat_avg', 'wkts', '4w', 'bowl_avg', 'e/r', 'best']
    numeric_cols = [col for col in numeric_cols if col in df.columns]
    for col in numeric_cols:
        df[col] = df[col].astype(str).str.replace(r'[^\d\.]', '', regex=True)  
        df[col] = pd.to_numeric(df[col], errors='coerce')

    df.dropna(subset=numeric_cols, inplace=True)

    vectors = df[numeric_cols].astype("float32").values
    
    return df ,vectors


def main():
    df_test = load_csv(r"C:\Users\jyothi.p.kommuru\Downloads\CricketGpt Project\CricketGpt\app\services\data_fetchers\Test_Data\all_teams_test_data.csv")
    df_odi = load_csv(r"C:\Users\jyothi.p.kommuru\Downloads\CricketGpt Project\CricketGpt\app\services\data_fetchers\ODI_Data\all_teams_ODI_data.csv")
    df_t20 = load_csv(r"C:\Users\jyothi.p.kommuru\Downloads\CricketGpt Project\CricketGpt\app\services\data_fetchers\T20_DATA\all_teams_T20_data.csv")
   
    # Clean and extract vectors
    df_test, test_vector = clean_data(df_test)
    df_odi, odi_vector = clean_data(df_odi)
    df_t20, t20_vector = clean_data(df_t20)
    

    test_vector = np.ascontiguousarray(test_vector, dtype=np.float32)
    odi_vector = np.ascontiguousarray(odi_vector, dtype=np.float32)
    t20_vector = np.ascontiguousarray(t20_vector, dtype=np.float32)

    # Normalize
    faiss.normalize_L2(test_vector)
    faiss.normalize_L2(odi_vector)
    faiss.normalize_L2(t20_vector)

    # FAISS index for Test
    index_test = faiss.IndexFlatL2(test_vector.shape[1])
    index_test.add(test_vector)
    faiss.write_index(index_test, "test_stats.index")
    with open("test_metadata.pkl", "wb") as f:
        pickle.dump(df_test.to_dict(orient="records"), f)

    # FAISS index for ODI
    index_odi = faiss.IndexFlatL2(odi_vector.shape[1])
    index_odi.add(odi_vector)
    faiss.write_index(index_odi, "odi_stats.index")
    with open("odi_metadata.pkl", "wb") as f:
        pickle.dump(df_odi.to_dict(orient="records"), f)

    # FAISS index for T20
    index_t20 = faiss.IndexFlatL2(t20_vector.shape[1])
    index_t20.add(t20_vector)
    faiss.write_index(index_t20, "t20_stats.index")
    with open("t20_metadata.pkl", "wb") as f:
        pickle.dump(df_t20.to_dict(orient="records"), f)

    print("Vector data stored successfully in FAISS.")


if __name__ == "__main__":
    main()




