import streamlit as st
import  faiss
import pickle
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

VECTOR_COLUMNS = ['matches', 'inns', 'runs', '100s', 'bat_avg', 'wkts', '4w', 'bowl_avg', 'e/r', 'best']

def load_faiss_index(index_path, metadata_path):
    index = faiss.read_index(index_path)
    with open(metadata_path, "rb") as f:
        metadata = pickle.load(f)
    return index, metadata

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

def get_player_data(name, metadata):
    return next((p for p in metadata if p.get("known_as", "").lower() == name.lower()), None)

def display_stats(player_data, header=None):
    if header:
        st.subheader(header)
    cols = st.columns(2)
    for i, (k, v) in enumerate(player_data.items()):
        cols[i % 2].markdown(f"**{k.replace('_', ' ').title()}**: {v}")

def comparison_radar_chart(player1, player2):
    stats = ['matches', 'runs', 'bat_avg', 'wkts', 'bowl_avg']
    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=[float(player1.get(stat, 0)) for stat in stats],
        theta=stats,
        fill='toself',
        name=player1['known_as']
    ))

    fig.add_trace(go.Scatterpolar(
        r=[float(player2.get(stat, 0)) for stat in stats],
        theta=stats,
        fill='toself',
        name=player2['known_as']
    ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True)),
        showlegend=True,
        title="Overall Skill Comparison (Radar Chart)"
    )
    return fig

def side_by_side_table(player1, player2):
    df = pd.DataFrame({
        'Metric': list(player1.keys()),
        player1['known_as']: list(player1.values()),
        player2['known_as']: list(player2.values())
    })
    return df.set_index("Metric")

def main():
    st.set_page_config(page_title="Cricket Player Stats", layout="wide")
    st.title("Cricket Player Stats Comparison")

    format_choice = st.selectbox("Select Match Format", ["ODI", "Test", "T20"])
    if format_choice == "ODI":
        index, metadata = load_faiss_index("odi_stats.index", "odi_metadata.pkl")
    elif format_choice == "Test":
        index, metadata = load_faiss_index("test_stats.index", "test_metadata.pkl")
    else:
        index, metadata = load_faiss_index("t20_stats.index", "t20_metadata.pkl")

    col1, col2 = st.columns(2)
    with col1:
        player1_name = st.text_input("Enter First Player Name")
    with col2:
        player2_name = st.text_input("Enter Second Player Name (Optional)")

    player1 = get_player_data(player1_name, metadata) if player1_name else None
    player2 = get_player_data(player2_name, metadata) if player2_name else None

    if player1:
        st.markdown("---")
        display_stats(player1, f"{player1.get('known_as')} Stats")

        if player2:
            display_stats(player2, f"{player2.get('known_as')} Stats")

            # Comparison Charts
            df_compare = pd.DataFrame([player1, player2])
            numeric_cols = [col for col in df_compare.columns if pd.api.types.is_numeric_dtype(pd.to_numeric(df_compare[col], errors='coerce'))]

            if numeric_cols:
                st.markdown("---")
                metric = st.selectbox("Choose Metric to Compare", numeric_cols)
                fig1 = px.bar(df_compare, x='known_as', y=metric, title=f"{metric} Comparison", color='known_as')
                st.plotly_chart(fig1, use_container_width=True)

                st.plotly_chart(comparison_radar_chart(player1, player2), use_container_width=True)

                st.markdown("#### Side-by-Side Table Comparison")
                st.dataframe(side_by_side_table(player1, player2))

        # Similar player suggestion
        st.markdown("---")
        show_similar = st.checkbox("Show Top 5 Similar Players")
        if show_similar:
            with st.spinner("Finding similar players..."):
                err, similar_players = search_similar_players(player1_name, index, metadata)
            if err:
                st.error(err)
            else:
                st.subheader("Top 5 Similar Players")
                for sim_player in similar_players:
                    st.markdown(f"**{sim_player.get('known_as')}**")
                    cols = st.columns(2)
                    for i, (k, v) in enumerate(sim_player.items()):
                        cols[i % 2].markdown(f"{k.replace('_', ' ').title()}: {v}")

                df_similar = pd.DataFrame(similar_players)
                sim_metric = st.selectbox("Metric for Similar Player Comparison", [col for col in df_similar.columns if pd.api.types.is_numeric_dtype(pd.to_numeric(df_similar[col], errors='coerce'))])
                fig2 = px.bar(df_similar, x='known_as', y=sim_metric, title=f"Top 5 Similar Players - {sim_metric} Comparison")
                st.plotly_chart(fig2, use_container_width=True)

    else:
        st.info("Please enter at least one player name to see stats.")

if __name__ == "__main__":
    main()
