import itertools
import os
import pickle as pkl
import sys
import time
from time import perf_counter

import networkx as nx
import pandas
import pandas as pd
from tqdm import tqdm


def main():
    os.chdir(os.path.dirname(sys.argv[0]))


    # generateGraphs()
    # generateIntegerUnionGraph([graph_filename for graph_filename in os.listdir("graphs/bipartite")])

    start = perf_counter()

    # G = generateUnionGraph([graph_filename for graph_filename in os.listdir("graphs/bipartite")])
    #
    # print(nx.is_bipartite(G))
    with open("graphs/bipartite/union_graph.pkl", "rb") as graph_file:
        G = pkl.load(graph_file)
    stop = perf_counter()
    # print(f"Generate union graph V1\nTime: {stop - start}s")

    start = perf_counter()
    author_G = generateAuthorGraphV1(G)
    stop = perf_counter()

    print(f"Generate author graph V1\nTime: {stop - start}s")
    print(author_G)

    with open("graphs/authors/author_graphV1.pkl", "wb") as graph_file:
        pkl.dump(author_G, graph_file)

    del author_G
    #
    # start = perf_counter()
    # author_G = generateAuthorGraphV2(G)
    # stop = perf_counter()
    # print(f"Generate author graph V2\nTime: {stop - start}s")
    # print(author_G)
    # #
    # # with open("graphs/authors/author_graphV2.pkl", "wb") as graph_file:
    # #     pkl.dump(author_G, graph_file)
    # #
    # del author_G
    #
    start = perf_counter()
    author_G = generateAuthorGraphV3(G)
    stop = perf_counter()
    print(f"Generate author graph V3\nTime: {stop - start}s")
    print(author_G)
    #
    # with open("graphs/authors/author_graphV3.pkl", "wb") as graph_file:
    #     pkl.dump(author_G, graph_file)


def generateGraphs():
    for csv in os.listdir("csv"):
        start = perf_counter()
        publications = pd.read_csv(f'csv/{csv}', delimiter=";", on_bad_lines="warn", low_memory=False)[["author", "title", "year"]].dropna()
        print("Load and first process time: ", perf_counter() - start)
        print(len(publications))

        start = perf_counter()
        publications = publications[['title', 'year']].join(publications[["author"]].squeeze().str.split('|', expand=True).stack().droplevel(level=1).rename("author"))
        print("Single author time: ", perf_counter() - start)

        start = perf_counter()
        if publications.year.dtype == object:
            publications = publications[['author', 'title']].join(publications[["year"]].squeeze().str.split('|', expand=True).stack().droplevel(level=1).rename("year"))
            publications.year = pandas.to_numeric(publications.year)
        print("Single year time: ", perf_counter() - start)

        print("Pre-bipartite check length:", len(publications))

        # Drop rows if some title is in author and viceversa
        start = perf_counter()
        publications.drop(publications[publications.author.isin(publications.title)].index, inplace=True)
        publications.reset_index(inplace=True, drop=True)
        print("Making the graph true bipartite:  ", perf_counter() - start)
        print("Post-bipartite check length:", len(publications))

        start = perf_counter()
        # Generando un multigraph si mantengono gli anni di pubblicazione doppi generando un edge per ogni anno, di default si genera un grafo quindi viene mantenuto l'ultimo anno di pubblicazione presente nel database generato precedentemente
        G = nx.from_pandas_edgelist(publications, "author", "title")  # , create_using=nx.MultiGraph

        nx.set_node_attributes(G, {el: True for el in publications.author}, "author")
        nx.set_node_attributes(G, {title: {"author": False, "year": year} for title, year in publications[["title", "year"]].itertuples(index=False)})

        print("Graph generation: ", perf_counter() - start)

        print("Is bipartite: ", nx.is_bipartite(G))

        with open(f"graphs/bipartite/{csv.replace('csv', 'pkl')}", "wb") as graph_file:
            pkl.dump(G, graph_file)

        print("\n\n")


def generateUnionGraph(graph_paths):
    graph_list = []
    for i, graph_filename in enumerate(graph_paths):
        if "union" in graph_filename:
            continue

        print(graph_filename, "loaded")
        with open(f"graphs/bipartite/{graph_filename}", "rb") as graph_file:
            graph_list.append(pkl.load(graph_file))
    #         G = pkl.load(graph_file)
    #
    #     if i == 0:
    #         union_graph = G.copy()
    #     else:
    #         union_graph.add_nodes_from(G.nodes(data=True))
    #         union_graph.add_edges_from(G.edges())
    #
    union_graph = nx.compose_all(graph_list)
    for u, v in union_graph.edges():
        if union_graph.nodes(data=True)[u]["author"] == union_graph.nodes(data=True)[v]["author"]:
            union_graph.remove_edge(u, v)

    with open(f"graphs/bipartite/union_graph.pkl", "wb") as graph_file:
        pkl.dump(union_graph, graph_file)
    return union_graph


def generateIntegerUnionGraph(graph_paths):
    author_to_nodes = {}
    union_graph = nx.Graph()
    for i, graph_filename in enumerate(graph_paths):
        if "union" in graph_filename:
            continue

        with open(f"graphs/bipartite/{graph_filename}", "rb") as graph_file:
            # graph_list.append(pkl.load(graph_file))
            G = pkl.load(graph_file)
            print(graph_filename, "loaded")
        tmp = []

        for n, d in G.nodes(data=True):
            author_to_nodes.setdefault(n, len(author_to_nodes))
            d["name"] = n
            tmp.append((author_to_nodes[n], d))
        union_graph.add_nodes_from(tmp)

        tmp = []
        for u, v in G.edges():
            tmp.append((author_to_nodes[u], author_to_nodes[v]))
        union_graph.add_edges_from(tmp)
    for u, v in union_graph.edges():
        if union_graph.nodes(data=True)[u]["author"] == union_graph.nodes(data=True)[v]["author"]:
            union_graph.remove_edge(u, v)

    with open(f"graphs/bipartite/integer_union_graph.pkl", "wb") as graph_file:
        pkl.dump(union_graph, graph_file)
    return union_graph


def generateAuthorGraphV1(G):
    author_graph = nx.MultiGraph()
    title_nodes = {n for n, d in G.nodes(data=True) if not d["author"]}
    my_set = []
    for publication in tqdm(title_nodes):
        author_pairs = list(itertools.combinations(G[publication], 2))
        my_set.extend(author_pairs)
        if len(author_pairs) == 0:
            author_graph.add_node(list(G[publication])[0])
        for author1, author2 in author_pairs:
            author_graph.add_edge(author1, author2, year=G.nodes[publication]["year"], title=publication)
    return author_graph


def generateAuthorGraphV2(G):
    author_graph = nx.Graph()
    title_nodes = {n for n, d in G.nodes(data=True) if not d["author"]}
    for publication in tqdm(title_nodes):
        author_pairs = list(itertools.combinations(G[publication], 2))
        if len(author_pairs) == 0:
            author_graph.add_node(list(G[publication])[0])
        for author1, author2 in author_pairs:
            if author_graph.has_edge(author1, author2):
                author_graph.add_edge(author1, author2, collaborations=author_graph[author1][author2]["collaborations"] + 1)
            else:
                author_graph.add_edge(author1, author2, collaborations=1)
    return author_graph


def generateAuthorGraphV3(G):
    title_nodes = {n for n, d in G.nodes(data=True) if not d["author"]}
    for title_node in tqdm(title_nodes):
        author_pairs = list(itertools.combinations(G[title_node], 2))
        for author1, author2 in author_pairs:
            if G.has_edge(author1, author2):
                G.add_edge(author1, author2, collaborations=G[author1][author2]["collaborations"] + 1)
            else:
                G.add_edge(author1, author2, collaborations=1)
        G.remove_node(title_node)
    return G




if __name__ == "__main__":
    main()
