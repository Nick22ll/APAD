import os
import pickle as pkl
import sys
from time import perf_counter

import networkx as nx


def main():
    os.chdir(os.path.dirname(sys.argv[0]))
    os.makedirs("results/question_4", exist_ok=True)


    #
    # with open(f"graphs/authors/author_graphV1.pkl", "rb") as graph_file:
    #     G = pkl.load(graph_file)
    #
    # print(G)
    #
    # start = perf_counter()
    # max_pair, max_collaborations = mostCollaborativeAuthorsV1(G)
    # stop = perf_counter()
    #
    # print(f"Collaborative authors V1\nTime: {stop-start}s\nPair: {(max_pair, max_collaborations)}")

    with open(f"graphs/authors/author_graphV2.pkl", "rb") as graph_file:
        G = pkl.load(graph_file)

    print(G)

    start = perf_counter()
    max_pair, max_collaborations = mostCollaborativeAuthorsV2(G)
    stop = perf_counter()

    print(f"Collaborative authors V2\nTime: {stop - start}s\nPair: {(max_pair, max_collaborations)}")
    with open(f"results/question_4/author_graphV2_results.pkl", "wb") as result_file:
        pkl.dump({"max_pair":max_pair, "max_collaborations":max_collaborations, "time":stop - start}, result_file)

    del G

    with open(f"graphs/authors/author_graphV3.pkl", "rb") as graph_file:
        G = pkl.load(graph_file)

    print(G)

    start = perf_counter()
    max_pair, max_collaborations = mostCollaborativeAuthorsV2(G)
    stop = perf_counter()

    print(f"Collaborative authors V2 (GraphV3)\nTime: {stop - start}s\nPair: {(max_pair, max_collaborations)}")
    with open(f"results/question_4/author_graphV3_results.pkl", "wb") as result_file:
        pkl.dump({"max_pair":max_pair, "max_collaborations":max_collaborations, "time":stop - start}, result_file)


def mostCollaborativeAuthorsV1(G):
    edge_counts = {}
    max_pair = None
    max_collaborations = 0

    for u, v in G.edges():

        if u > v:
            pair = (v, u)
        else:
            pair = (u, v)

        edge_counts[pair] = edge_counts.setdefault(pair, 0) + 1
        if edge_counts[pair] > max_collaborations:
            max_collaborations = edge_counts[pair]
            max_pair = pair
    return max_pair, max_collaborations


def mostCollaborativeAuthorsV2(G):
    max_pair = None
    max_collaborations = 0

    for u, v, attrs in G.edges(data=True):
        if attrs.get("collaborations", -1) > max_collaborations:
            max_collaborations = attrs["collaborations"]
            max_pair = (u, v)

    return max_pair, max_collaborations


if __name__ == "__main__":
    main()
