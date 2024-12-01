"""
Este módulo proporciona una interfaz gráfica para calcular rutas óptimas y árboles de expansión mínima 
(MST) en grafos urbanos generados a partir de datos de OpenStreetMap. Incluye funcionalidades para 
mostrar rutas en grafos, comparar tiempos de ejecución de algoritmos (Dijkstra y Prim) y visualizar 
gráficos de desempeño.

Librerías utilizadas:
- `osmnx` para la obtención de datos de mapas y generación de grafos urbanos.
- `networkx` para trabajar con grafos y aplicar algoritmos como Dijkstra y Prim.
- `matplotlib` para la visualización de resultados.
- `tkinter` para la creación de la interfaz gráfica.

Funciones principales:
- Construcción de grafos urbanos.
- Cálculo de rutas óptimas utilizando Dijkstra.
- Generación de árboles de expansión mínima utilizando Prim.
- Visualización de rutas y MST en el grafo.
- Comparación de tiempos de ejecución de los algoritmos en función del tamaño del grafo.
"""

import tkinter as tk
from tkinter import messagebox
import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
import time

def construir_grafo_urbano(ciudad):
    """
    Construye un grafo urbano para una ciudad específica utilizando datos de OpenStreetMap.

    Args:
        ciudad (str): Nombre de la ciudad o región a buscar.

    Returns:
        networkx.DiGraph: Grafo urbano con datos de carreteras y calles.
        None: Si ocurre algún error al construir el grafo.
    """
    try:
        Start = ox.graph_from_place(ciudad, network_type='drive')
        return Start
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo construir el grafo para la ciudad: {e}")
        return None

def ruta_optima_dijkstra(Start, origen, destino):
    """
    Encuentra la ruta más corta entre dos nodos en un grafo utilizando el algoritmo de Dijkstra.

    Args:
        Start (networkx.Graph): Grafo urbano.
        origen (int): Nodo inicial.
        destino (int): Nodo final.

    Returns:
        list: Lista de nodos que forman la ruta más corta.
        None: Si no existe un camino entre los nodos.
    """
    try:
        return nx.shortest_path(Start, origen, destino, weight='length')
    except nx.NetworkXNoPath:
        return None

def arbol_expansion_minima_prim(Start):
    """
    Genera un árbol de expansión mínima (MST) utilizando el algoritmo de Prim.

    Args:
        Start (networkx.Graph): Grafo urbano.

    Returns:
        networkx.Graph: Árbol de expansión mínima.
    """
    if Start.is_directed():
        Start = Start.to_undirected()
    return nx.minimum_spanning_tree(Start, weight='length')

def mostrar_ruta(Start, ruta):
    """
    Muestra una ruta en el grafo utilizando matplotlib.

    Args:
        Start (networkx.Graph): Grafo urbano.
        ruta (list): Lista de nodos que forman la ruta a mostrar.
    """
    if ruta:
        ox.plot_graph_route(Start, ruta, route_linewidth=6, node_size=0, bgcolor='k')

def mostrar_mst(Start, mst):
    """
    Muestra el árbol de expansión mínima (MST) en el grafo utilizando matplotlib.

    Args:
        Start (networkx.Graph): Grafo urbano.
        mst (networkx.Graph): Árbol de expansión mínima.
    """
    plt.close()
    pos = {node: (data['x'], data['y']) for node, data in Start.nodes(data=True)}
    edges = list(mst.edges(data=True))
    plt.figure(figsize=(12, 12))
    nx.draw(Start, pos, node_size=10, node_color='blue', alpha=0.5, with_labels=False)
    nx.draw_networkx_edges(Start, pos, edgelist=edges, edge_color='red', width=2)
    plt.show()

def obtener_nodo_por_coordenadas(Start, lat, lon):
    """
    Encuentra el nodo más cercano a un punto geográfico específico.

    Args:
        Start (networkx.Graph): Grafo urbano.
        lat (float): Latitud del punto.
        lon (float): Longitud del punto.

    Returns:
        int: Nodo más cercano al punto proporcionado.
    """
    return ox.distance.nearest_nodes(Start, X=lon, Y=lat)

def medir_promedio_tiempo(funcion, *args, repeticiones=5):
    """
    Mide el tiempo promedio de ejecución de una función en múltiples repeticiones.

    Args:
        funcion (callable): Función a medir.
        *args: Argumentos para la función.
        repeticiones (int): Número de repeticiones para la medición.

    Returns:
        float: Tiempo promedio de ejecución en segundos.
    """
    tiempos = []
    for _ in range(repeticiones):
        start_time = time.perf_counter()
        funcion(*args)
        tiempos.append(time.perf_counter() - start_time)
    return sum(tiempos) / len(tiempos)

def medir_tiempos_de_ejecucion(ciudad):
    """
    Mide los tiempos de ejecución de los algoritmos Dijkstra y Prim para grafos de tamaño creciente.

    Args:
        ciudad (str): Nombre de la ciudad o región a analizar.

    Returns:
        tuple: Tres listas (tamaños de subgrafos, tiempos de Dijkstra, tiempos de Prim).
    """
    Start = construir_grafo_urbano(ciudad)
    if Start is None:
        return [], [], []

    nodos = list(Start.nodes)
    tamanos = []
    tiempos_dijkstra = []
    tiempos_prim = []

    for i in range(10, min(100, len(nodos)), 10):  # Subgrafos de tamaño creciente
        subgrafo = Start.subgraph(nodos[:i])
        if len(subgrafo.nodes) < 2:
            continue
        origen = list(subgrafo.nodes())[0]
        destino = list(subgrafo.nodes())[-1]

        # Medir tiempo para Dijkstra
        tiempo_dijkstra = medir_promedio_tiempo(ruta_optima_dijkstra, subgrafo, origen, destino)
        tiempos_dijkstra.append(tiempo_dijkstra)

        # Medir tiempo para Prim
        tiempo_prim = medir_promedio_tiempo(arbol_expansion_minima_prim, subgrafo)
        tiempos_prim.append(tiempo_prim)

        tamanos.append(len(subgrafo.nodes))

    return tamanos, tiempos_dijkstra, tiempos_prim

def graficar_resultados():
    """
    Genera una gráfica comparativa de los tiempos de ejecución de Dijkstra y Prim.

    Muestra la gráfica con matplotlib.
    """
    ciudad = ciudad_entry.get()
    if ciudad:
        tamanos, tiempos_dijkstra, tiempos_prim = medir_tiempos_de_ejecucion(ciudad)
        if tamanos:
            plt.figure(figsize=(10, 6))
            plt.plot(tamanos, tiempos_dijkstra, label='Dijkstra', color='blue')
            plt.plot(tamanos, tiempos_prim, label='Prim', color='green')
            plt.xlabel('Número de nodos del grafo')
            plt.ylabel('Tiempo de ejecución (segundos)')
            plt.title('Comparación de tiempos de ejecución: Dijkstra vs Prim')
            plt.legend()
            plt.grid(True)
            plt.show()
        else:
            messagebox.showinfo("Información", "No se encontraron datos suficientes para graficar.")
    else:
        messagebox.showerror("Error", "Debe ingresar una ciudad.")

def calcular_ruta():
    """
    Calcula y muestra la ruta más corta y el árbol de expansión mínima (MST) 
    para los nodos seleccionados en un grafo urbano.
    """
    ciudad = ciudad_entry.get()
    if not ciudad:
        messagebox.showerror("Error", "Debe ingresar una ciudad.")
        return

    Start = construir_grafo_urbano(ciudad)
    if Start is None:
        return

    try:
        lat_origen = float(lat_origen_entry.get())
        lon_origen = float(lon_origen_entry.get())
        origen = obtener_nodo_por_coordenadas(Start, lat_origen, lon_origen)
    except ValueError:
        messagebox.showerror("Error", "Las coordenadas del origen no son válidas.")
        return

    try:
        lat_destino = float(lat_destino_entry.get())
        lon_destino = float(lon_destino_entry.get())
        destino = obtener_nodo_por_coordenadas(Start, lat_destino, lon_destino)
    except ValueError:
        messagebox.showerror("Error", "Las coordenadas del destino no son válidas.")
        return

    ruta = ruta_optima_dijkstra(Start, origen, destino)
    if ruta:
        mostrar_ruta(Start, ruta)

    mst = arbol_expansion_minima_prim(Start)
    if mst:
        mostrar_mst(Start, mst)

# Interfaz gráfica
root = tk.Tk()
root.title("Rutas y MST")
root.geometry("500x400")

tk.Label(root, text="Ciudad:").pack(pady=5)
ciudad_entry = tk.Entry(root)
ciudad_entry.pack(pady=5)

tk.Label(root, text="Latitud Origen:").pack(pady=5)
lat_origen_entry = tk.Entry(root)
lat_origen_entry.pack(pady=5)

tk.Label(root, text="Longitud Origen:").pack(pady=5)
lon_origen_entry = tk.Entry(root)
lon_origen_entry.pack(pady=5)

tk.Label(root, text="Latitud Destino:").pack(pady=5)
lat_destino_entry = tk.Entry(root)
lat_destino_entry.pack(pady=5)

tk.Label(root, text="Longitud Destino:").pack(pady=5)
lon_destino_entry = tk.Entry(root)
lon_destino_entry.pack(pady=5)

tk.Button(root, text="Calcular Ruta y MST", command=calcular_ruta).pack(pady=10)
tk.Button(root, text="Graficar Resultados", command=graficar_resultados).pack(pady=10)

root.mainloop()
