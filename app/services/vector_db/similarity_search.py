import faiss
import pickle
import numpy as np

# Load FAISS indices and metadata
indexes = {
    "Test": faiss.read_index("test_stats.index"),
    "ODI": faiss.read_index("odi_stats.index"),
    "T20": faiss.read_index("t20_stats.index")
}

metadatas = {
    "Test": pickle.load(open("test_metadata.pkl", "rb")),
    "ODI": pickle.load(open("odi_metadata.pkl", "rb")),
    "T20": pickle.load(open("t20_metadata.pkl", "rb"))
}

# Columns used for vector embeddings
VECTOR_COLUMNS = ['matches', 'inns', 'runs', '100s', 'bat_avg',
                  'wkts', '4w', 'bowl_avg', 'e/r', 'best']

def preprocess_vector(player: dict) -> np.ndarray:
    """Convert player stats to a float32 numpy array."""
    vector = []
    for col in VECTOR_COLUMNS:
        val = player.get(col, "0")
        if isinstance(val, str):
            val = val.replace('*', '').strip()
            if val in ['-', '']:
                val = 0
        try:
            vector.append(float(val))
        except ValueError:
            vector.append(0.0)
    vector_np = np.array(vector, dtype='float32').reshape(1, -1)
    return vector_np

def search_similar_players(player_name, match_format="ODI", top_k=5):
    if match_format not in indexes:
        return f"Invalid format: {match_format}. Choose from Test, ODI, T20."

    index = indexes[match_format]
    metadata = metadatas[match_format]

    # Find player's vector
    player_vector = None
    for player in metadata:
        if player.get('known_as', '').lower() == player_name.lower():
            player_vector = preprocess_vector(player)
            break

    if player_vector is None:
        return f"Player '{player_name}' not found in {match_format} data."

    

    # Ensure vector dimension matches index
    if player_vector.shape[1] != index.d:
        return f"Dimension mismatch: vector has {player_vector.shape[1]}, index expects {index.d}"

    # Normalize and search
    faiss.normalize_L2(player_vector)
    distances, indices = index.search(player_vector, top_k)

    # Collect top-k results
    results = [metadata[i] for i in indices[0]]
    return results

if __name__ == "__main__":
    players = search_similar_players("Virat Kohli", match_format="T20", top_k=5)

    if isinstance(players, str):
        print(players)  
    else:
        print(f"\nTop similar players to 'Virat Kohli' in ODI format:")
        for i, p in enumerate(players, 1):
            print(f"{i}. {p.get('known_as')} - Runs: {p.get('runs')}, Avg: {p.get('bat_avg')}")
