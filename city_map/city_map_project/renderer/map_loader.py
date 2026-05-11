import os
import pickle
import osmnx as ox

CACHE_DIR = "cache/graph"


def load_graph(place):

    os.makedirs(CACHE_DIR, exist_ok=True)

    cache_path = f"{CACHE_DIR}/{place}.pkl"

    if os.path.exists(cache_path):

        print("Loading graph cache...")
        with open(cache_path, "rb") as f:
            return pickle.load(f)

    print("Downloading graph...")
    G = ox.graph_from_place(place, network_type="drive")

    with open(cache_path, "wb") as f:
        pickle.dump(G, f)

    return G

def load_boundary(place_name):
    return ox.geocode_to_gdf(place_name)