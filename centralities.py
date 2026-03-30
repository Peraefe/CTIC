import os
import pickle
import igraph as ig
import osmnx as ox
from shapely.geometry import Polygon
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

CACHE_DIR = "dados_cache"
os.makedirs(CACHE_DIR, exist_ok=True)


def save_pickle(obj, filename):
    with open(filename, "wb") as f:
        pickle.dump(obj, f)

def load_pickle(filename):
    with open(filename, "rb") as f:
        return pickle.load(f)
    

# Polígono de Palmas

coords = [
    (-48.36696955241467, -10.16042180576919),
    (-48.37886688384131, -10.336359895479362),
    (-48.35982289686413, -10.35628534841031),
    (-48.342471323758105, -10.357751575597831),
    (-48.33666333289699, -10.370889148819813),
    (-48.30672563561052, -10.378178731196513),
    (-48.25570954866717, -10.34419542890619),
    (-48.249420868902234, -10.321439608338196),
    (-48.29231253625048, -10.28068681395601),
    (-48.30943053325848, -10.24007484517854),
    (-48.30981880008265, -10.229993635704872),
    (-48.303957402338625, -10.220574128399832),
    (-48.29577028867692, -10.159450203497599),
    (-48.317091634855245, -10.132453181528646),
    (-48.36696955241467, -10.16042180576919)
]
poly = Polygon(coords)

custom_filter = (
    '["highway"!~"footway|path|cycleway|pedestrian|steps"]'
    '["area"!~"yes"]["highway"]'
)



# Converter NetworkX p iGraph

def nx_to_igraph(G_nx, directed=True):
    mapping = {node: idx for idx, node in enumerate(G_nx.nodes())}
    G_ig = ig.Graph(directed=directed)
    G_ig.add_vertices(len(mapping))

    for node, idx in mapping.items():
        n = G_nx.nodes[node]
        G_ig.vs[idx]["id"] = node
        G_ig.vs[idx]["x"] = n.get("x", None)
        G_ig.vs[idx]["y"] = n.get("y", None)

    edges = []
    weights = []
    for u, v, data in G_nx.edges(data=True):
        edges.append((mapping[u], mapping[v]))
        weights.append(data.get("length", 1.0))
    G_ig.add_edges(edges)
    G_ig.es["weight"] = weights

    return G_ig, mapping


# Centralidades

def compute_centralities_igraph(G):
    degree = G.degree()
    closeness = G.closeness(mode="ALL",normalized=True)
    betweenness = G.betweenness(normalized=True)
    return {
        "degree": {v.index: degree[v.index] for v in G.vs},
        "closeness": {v.index: closeness[v.index] for v in G.vs},
        "betweenness": {v.index: betweenness[v.index] for v in G.vs},
    }



#Processamento do Grafo

def process_graph(graphml_path):

    if os.path.exists(graphml_path):
        print("Carregando grafo do cache...")
        G_nx = ox.load_graphml(graphml_path)
    else:
        print("Baixando grafo do OSM...")
        G_nx = ox.graph_from_polygon(poly, custom_filter=custom_filter, network_type="drive")
        ox.save_graphml(G_nx, graphml_path)
        print("Grafo salvo no cache.")

    #Checar cache do igraph
    igraph_cache = os.path.join(CACHE_DIR, "grafo_igraph.pkl")
    if os.path.exists(igraph_cache):
        print("Carregando grafo iGraph do cache...")
        G_ig, mapping = load_pickle(igraph_cache)
    else:
        print("Convertendo para iGraph...")
        G_ig, mapping = nx_to_igraph(G_nx)
        save_pickle((G_ig, mapping), igraph_cache)
        print("Grafo iGraph salvo em cache.")

    #Checar cache das centralidades 
    centralities_cache = os.path.join(CACHE_DIR, "centralities.pkl")
    if os.path.exists(centralities_cache):
        print("🔹 Carregando centralidades do cache...")
        centralities = load_pickle(centralities_cache)
    else:
        print("Calculando centralidades...")
        centralities = compute_centralities_igraph(G_ig)
        save_pickle(centralities, centralities_cache)
        print("Centralidades salvas em cache.")

    deg_c = centralities["degree"]
    clo_c = centralities["closeness"]
    bet_c = centralities["betweenness"]

    plot_centrality(bet_c, "Betweenness Centrality")
    plot_centrality(deg_c, "Degree Centrality")
    plot_centrality(clo_c, "Closeness Centrality")

    return 


def plot_centrality(centrality, title):

    values = list(centrality.values())

    plt.figure(figsize=(12,6))
    plt.plot(range(len(values)), values, marker='.', linestyle='None', markersize=4)

    plt.title(title)
    plt.ylim(0, max(values)+0.00001)
    plt.ylabel("Centrality")
    plt.grid(True)
    plt.show()


#Executa

if __name__ == "__main__":
    graph_file = "dados_cache/grafo.graphml"
    process_graph(graph_file)

    






