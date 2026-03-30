import os
import igraph as ig
import plotly.graph_objects as go
from shapely.geometry import Polygon
import osmnx as ox
import numpy as np

CACHE_DIR = "dados_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

# -------------------
# Polígono de Palmas
# -------------------

coords = [
(-48.36696955241467,-10.16042180576919),
(-48.37886688384131,-10.336359895479362),
(-48.35982289686413,-10.35628534841031),
(-48.342471323758105,-10.357751575597831),
(-48.33666333289699,-10.370889148819813),
(-48.30672563561052,-10.378178731196513),
(-48.25570954866717,-10.34419542890619),
(-48.249420868902234,-10.321439608338196),
(-48.29231253625048,-10.28068681395601),
(-48.30943053325848,-10.24007484517854),
(-48.30981880008265,-10.229993635704872),
(-48.303957402338625,-10.220574128399832),
(-48.29577028867692,-10.159450203497599),
(-48.317091634855245,-10.132453181528646),
(-48.36696955241467,-10.16042180576919)
]

poly = Polygon(coords)

custom_filter = (
'["highway"!~"footway|path|cycleway|pedestrian|steps"]'
'["area"!~"yes"]["highway"]'
)

# -------------------
# Baixar ou carregar grafo
# -------------------

def iniciarGrafo():

    path = os.path.join(CACHE_DIR,"grafo.graphml")

    if os.path.exists(path):

        print("Carregando grafo do cache...")
        G = ox.load_graphml(path)

    else:

        print("Baixando grafo do OSM...")
        G = ox.graph_from_polygon(poly,custom_filter=custom_filter,network_type="drive")
        ox.save_graphml(G,path)

    return G


G_nx = iniciarGrafo()

# -------------------
# Converter NetworkX -> iGraph
# -------------------

nx_nodes = list(G_nx.nodes())

node_id_map = {node:i for i,node in enumerate(nx_nodes)}

edges_ig = [(node_id_map[u],node_id_map[v]) for u,v in G_nx.edges()]

G = ig.Graph(edges_ig,directed=True)

# pesos
weights = []

for u,v,data in G_nx.edges(data=True):
    weights.append(data.get("length",1))

G.es["weight"] = weights


# -------------------
# Centralidades
# -------------------

print("Calculando centralidades...")

degree = G.degree()

closeness = G.closeness(weights="weight", normalized=True)

betweenness = G.betweenness(weights="weight",normalized=True)

centralities = {
"Degree Centrality":degree,
"Closeness Centrality":closeness,
"Betweenness Centrality":betweenness
}

# -------------------
# Posições dos nós
# -------------------

pos = {node_id_map[n]:(G_nx.nodes[n]["y"],-G_nx.nodes[n]["x"]) for n in G_nx.nodes()}


# -------------------
# Função de plot
# -------------------

def plot_heatmap(values,title,filename):

    print("Gerando:",title)

    v = np.array(values)

    # normalização
    if v.max() == v.min():
        v = np.zeros_like(v)
    else:
        v = (v - v.min())/(v.max() - v.min())

    min_size = 3
    max_size = 15
    sizes = min_size + v * (max_size - min_size)

    fig = go.Figure()

    # -------- ARESTAS --------

    edge_x=[]
    edge_y=[]
    edge_color=[]

    for e in G.es:

        u,v_id = e.tuple

        x0,y0 = pos[u]
        x1,y1 = pos[v_id]

        val = (values[u]+values[v_id])/2

        edge_x += [x0,x1,None]
        edge_y += [y0,y1,None]
        edge_color.append(val)

    fig.add_trace(go.Scatter(
        x=edge_x,
        y=edge_y,
        mode="lines",
        line=dict(width=1,color="gray"),
        hoverinfo="none"
    ))

    # -------- NÓS --------

    node_x=[pos[i][0] for i in range(len(nx_nodes))]
    node_y=[pos[i][1] for i in range(len(nx_nodes))]

    fig.add_trace(go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers",
        marker=dict(
            size=sizes,
            color=values,
            colorscale="Viridis",
            showscale=True,
            colorbar=dict(
                title="Centrality",
                tickformat=".6f"
            )
        ),
        hoverinfo="none"
    ))

    fig.update_layout(
        title=title,
        showlegend=False,
        margin=dict(l=0,r=0,t=40,b=0),
        plot_bgcolor="white",
        xaxis=dict(showline=False,showgrid=False,zeroline=False,showticklabels=False),
        yaxis=dict(showline=False,showgrid=False,zeroline=False,showticklabels=False)
    )

    fig.update_yaxes(scaleanchor="x",scaleratio=1)

    fig.write_image(filename,width=3000,height=1400)

    print("PNG salvo:",filename)


# -------------------
# Gerar mapas
# -------------------

for name,values in centralities.items():

    file = name.lower().replace(" ","_")+".png"

    plot_heatmap(values,name,file)

print("Todos os heatmaps gerados.")