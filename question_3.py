import itertools
import os
import pickle as pkl
import sys
from time import perf_counter

import networkx as nx
from tqdm import tqdm


def main():
    os.chdir(os.path.dirname(sys.argv[0]))
    os.makedirs("results/question_3", exist_ok=True)

    for graph_filename in os.listdir("graphs/bipartite")[8:]:
        with open(f"graphs/bipartite/{graph_filename}", "rb") as graph_file:
            G = pkl.load(graph_file)

        print(G)

        # print("\n#### MOST AUTHORS PAIR ####")
        # output = most_authors_pair(G)
        # for year in output:
        #     print(year, output[year])

        # with open(f"results/question_3/{graph_filename}_results.pkl", "wb") as result_file:
        #     pkl.dump(output, result_file)

        print("\n#### MOST AUTHORS PAIR ####")
        output = most_authors_pairV2(G)
        for year in output:
            print(year, output[year])

        with open(f"results/question_3/{graph_filename}_resultsV2.pkl", "wb") as result_file:
            pkl.dump(output, result_file)


def most_authors_pair(G):
    year_times = {}

    for year_limit in [1960, 1970, 1980, 1990, 2000, 2010, 2020, 2023]:
        time_sections = {}

        time_sections["author_nodes_calculation"] = perf_counter()

        author_nodes = {n for n, d in G.nodes(data=True) if d["author"]}

        time_sections["author_nodes_calculation"] = perf_counter() - time_sections["author_nodes_calculation"]

        time_sections["pair_calculation"] = perf_counter()

        pairs_count = {}
        best_pair = None
        max_authors = 0
        for author in author_nodes:  # i nodi autore sono unici nel grafo, non ci sono doppioni
            publications = [p for p in G[author] if G.nodes[p]["year"] <= year_limit]  # # un autore può avere solo pubblicazioni come vicini (Grafo bipartito)
            for pair in itertools.combinations(publications, 2):
                if pair[0] > pair[1]:
                    pair = (pair[1], pair[0])
                pairs_count[pair] = pairs_count.setdefault(pair, 0) + 1
                if pairs_count[pair] > max_authors:
                    max_authors = pairs_count[pair]
                    best_pair = pair

        time_sections["pair_calculation"] = perf_counter() - time_sections["pair_calculation"]
        time_sections["pair_number"] = len(pairs_count)
        year_times[year_limit] = {"times": time_sections, "best_pair": best_pair, "common_authors": max_authors}

    return year_times


def most_authors_pairV2(G):
    year_times = {}

    for year_limit in [1960, 1970, 1980, 1990, 2000, 2010, 2020, 2023]:
        time_sections = {}

        time_sections["author_nodes_calculation"] = perf_counter()

        title_nodes = {n for n, d in G.nodes(data=True) if not d["author"] and d["year"] <= year_limit}

        time_sections["author_nodes_calculation"] = perf_counter() - time_sections["author_nodes_calculation"]

        time_sections["pair_calculation"] = perf_counter()
        already_done=set()
        best_pair = None
        max_authors = 0
        for publication in title_nodes:
            already_done.add(publication)
            pairs_count = {}
            connected_publications = []
            for author in G[publication]:
                connected_publications.extend([p for p in G[author] if p not in already_done and G.nodes[p]["year"] <= year_limit and p != publication])
            for connected_pub in connected_publications:
                pair = (publication, connected_pub)
                pairs_count[pair] = pairs_count.setdefault(pair, 0) + 1
                if pairs_count[pair] > max_authors:
                    max_authors = pairs_count[pair]
                    best_pair = pair

        time_sections["pair_calculation"] = perf_counter() - time_sections["pair_calculation"]

        year_times[year_limit] = {"num_nodes":len(title_nodes), "times": time_sections, "best_pair": best_pair, "common_authors": max_authors}

        print(year_times[year_limit])

    return year_times




if __name__ == "__main__":
    main()
