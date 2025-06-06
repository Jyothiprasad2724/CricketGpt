import streamlit as st
import faiss
import pickle
import numpy as np
import pandas as pd
import plotly.express as px

# Columns to build vectors
VECTOR_COLUMNS = ['matches', 'inns', 'runs', '100s', 'bat_avg', 'wkts', '4w', 'bowl_avg', 'e/r', 'best']

# Load FAISS index and metadata
def load_faiss_index(index_path, metadata_path):
    index = faiss.read_index(index_path)
    with open(metadata_path, "rb") as f:
        metadata = pickle.load(f)
    return index, metadata

# Convert player's stat dictionary to FAISS-compatible vector
def preprocess_vector(player: dict) -> np.ndarray:
    vector = []
    for col in VECTOR_COLUMNS:
        val = player.get(col, "0")
        if isinstance(val, str):
            val = val.replace("*", "").strip()
            if val in ["-", ""]:
                val = 0
        try:
            vector.append(float(val))
        except ValueError:
            vector.append(0.0)
    return np.array(vector, dtype='float32').reshape(1, -1)

# Search similar players based on a selected player's stat vector
def search_similar_players(player_name, index, metadata, top_k=5):
    player_vector = None
    for player in metadata:
        if player.get("known_as", "").lower() == player_name.lower():
            player_vector = preprocess_vector(player)
            break

    if player_vector is None:
        return f"Player '{player_name}' not found.", []

    if player_vector.shape[1] != index.d:
        return f"Vector dimension mismatch: got {player_vector.shape[1]}, expected {index.d}", []

    faiss.normalize_L2(player_vector)
    D, I = index.search(player_vector, top_k)
    return None, [metadata[i] for i in I[0]]

# Main Streamlit app
def main():
    st.set_page_config(page_title="Cricket Stats Chatbot", page_icon="🏏")
    st.title("🏏 Cricket Similar Player Finder")
    st.write("Type a player's name and get their stats. Optionally compare with top 5 similar players.")

    format_choice = st.selectbox("Select Match Format", ["ODI", "Test", "T20"])

    if format_choice == "ODI":
        index, metadata = load_faiss_index("odi_stats.index", "odi_metadata.pkl")
    elif format_choice == "Test":
        index, metadata = load_faiss_index("test_stats.index", "test_metadata.pkl")
    else:
        index, metadata = load_faiss_index("t20_stats.index", "t20_metadata.pkl")

    player_name = st.text_input("Enter Player Name (e.g., Virat Kohli):")

    if player_name:
        player_data = None
        for player in metadata:
            if player.get("known_as", "").lower() == player_name.strip().lower():
                player_data = player
                break

        if player_data is None:
            st.error(f"Player '{player_name}' not found in {format_choice} data.")
        else:
            st.subheader(f"Stats for '{player_data.get('known_as')}'")
            cols = st.columns(2)
            for i, (key, value) in enumerate(player_data.items()):
                cols[i % 2].markdown(f"**{key.replace('_', ' ').title()}**: {value}")

            # Show bar chart of numeric stats
            df = pd.DataFrame([player_data])
            numeric_cols = [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col])]
            if numeric_cols:
                metric = st.selectbox("Choose Metric to Visualize", numeric_cols)
                fig = px.bar(df, x='known_as', y=metric, title=f"{metric} of {player_data.get('known_as')}")
                st.plotly_chart(fig)

                # Ask if user wants comparison
                compare = st.radio("Do you want to compare with top 5 similar players?", ["No", "Yes"])

                if compare == "Yes":
                    with st.spinner("Finding similar players..."):
                        error_msg, results = search_similar_players(player_name.strip(), index, metadata, top_k=5)

                    if error_msg:
                        st.error(error_msg)
                    elif results:
                        st.subheader("Top 5 Similar Players")
                        for idx, res in enumerate(results, 1):
                            st.markdown(f"### {idx}. {res.get('known_as', 'Unknown')}")
                            cols = st.columns(2)
                            for i, (key, value) in enumerate(res.items()):
                                cols[i % 2].markdown(f"**{key.replace('_', ' ').title()}**: {value}")

                        # Comparison Chart
                        df_compare = pd.DataFrame(results)
                        numeric_cols_compare = [col for col in df_compare.columns if pd.api.types.is_numeric_dtype(df_compare[col])]
                        if 'known_as' in df_compare.columns and numeric_cols_compare:
                            metric = st.selectbox("Choose Metric to Compare", numeric_cols_compare, key="compare_metric")
                            fig = px.bar(df_compare, x='known_as', y=metric, title=f"{metric} Comparison")
                            st.plotly_chart(fig)

    else:
        st.info("Please enter a player name to see stats.")

if __name__ == "__main__":
    main()
