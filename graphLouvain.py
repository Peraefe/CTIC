import plotly.graph_objects as go
import os
import pickle
from collections import Counter
import pandas as pd

CACHE_DIR = "dados_cache"
os.makedirs(CACHE_DIR, exist_ok=True)


def save_pickle(obj, filename):
    with open(filename, "wb") as f:
        pickle.dump(obj, f)

def load_pickle(filename):
    with open(filename, "rb") as f:
        return pickle.load(f)


# Louvain
louvain_cache = os.path.join(CACHE_DIR, "louvain_partition.pkl")

if os.path.exists(louvain_cache):
    print("Carregando clusters Louvain do cache...")
    partition = load_pickle(louvain_cache)
else:
    print("Partição não encontrada...")
    


# =========================
# 📊 TABELA DE CLUSTERS
# =========================

cluster_sizes = Counter(partition.values())

df_clusters = pd.DataFrame(
    cluster_sizes.items(),
    columns=["Cluster", "Tamanho"]
)

df_clusters = df_clusters.sort_values(by="Tamanho", ascending=False).reset_index(drop=True)

total_nodes = len(partition)
df_clusters["%"] = (df_clusters["Tamanho"] / total_nodes * 100).round(2)

# =========================
# 📊 GRÁFICO DE BARRAS
# =========================

# Todos os clusters
bar_fig = go.Figure()

bar_fig.add_trace(go.Bar(
    x=df_clusters["Cluster"].astype(str),
    y=df_clusters["Tamanho"],
))

bar_fig.update_layout(
    title="Clusters Distribution (Louvain)",
    xaxis_title="Cluster",
    yaxis_title="Vertex Number",
    plot_bgcolor="white"
)

bar_fig.show()
