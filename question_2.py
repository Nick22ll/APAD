import os
import pickle as pkl
import re
import sys
from collections import Counter
from queue import Queue
from time import perf_counter

import networkx as nx


def main():
    os.chdir(os.path.dirname(sys.argv[0]))
    os.makedirs("results/question_2", exist_ok=True)

    for graph_filename in os.listdir("graphs/bipartite"):
        with open(f"graphs/bipartite/{graph_filename}", "rb") as graph_file:
            G = pkl.load(graph_file)

        print(G)

        print("\n#### COUNT CC WORDS ####")
        output = count_CC_words(G)
        for year in output:
            print(year, output[year]["times"])

        with open(f"results/question_2/{graph_filename}_results.pkl", "wb") as result_file:
            pkl.dump(output, result_file)


def count_CC_words(G):
    # titles_nodes = {n: {"color": "white", "distance": 0, "predecessor": None} for n, d in G.nodes(data=True) if not d["author"]}
    year_times = {}

    for year_limit in [1960, 1970, 1980, 1990, 2000, 2010, 2020, 2023]:

        time_sections = {}

        time_sections["title_nodes_calculation"] = perf_counter()

        titles_nodes = {n for n, d in G.nodes(data=True) if not d["author"] and d["year"] <= year_limit}
        author_nodes = {a for t in titles_nodes for a in G[t]}
        sub_graph = G.subgraph(titles_nodes.union(author_nodes))

        time_sections["number_of_titles"] = len(titles_nodes)
        time_sections["number_of_nodes"] = len(sub_graph.nodes())

        time_sections["title_nodes_calculation"] = perf_counter() - time_sections["title_nodes_calculation"]

        time_sections["CCs_calculation"] = perf_counter()

        nx.set_node_attributes(sub_graph, "white", "color")

        ccs = []

        while len(titles_nodes) > 0:
            cc = set()

            titles_queue = Queue()
            titles_queue.put(titles_nodes.pop())
            while not titles_queue.empty():
                current_node = titles_queue.get()
                if not sub_graph.nodes[current_node]["author"]:
                    cc.add(current_node)
                for adjacent_node in sub_graph[current_node]:
                    if sub_graph.nodes[adjacent_node]["color"] == "white":
                        sub_graph.nodes[adjacent_node]["color"] = "grey"
                        titles_queue.put(adjacent_node)
                sub_graph.nodes[current_node]["color"] = "black"

            titles_nodes -= cc

            if len(cc) >= 30:
                ccs.append(cc)

        time_sections["CCs_calculation"] = perf_counter() - time_sections["CCs_calculation"]

        time_sections["words_calculation"] = perf_counter()

        MUW = {}
        total_words = 0
        for i, cc in enumerate(ccs):
            MUW[i] = most_used_words(cc)
            total_words += MUW[i]["total_words"]
        time_sections["words_calculation"] = perf_counter() - time_sections["words_calculation"]
        time_sections["words_number"] = total_words
        time_sections["cc_number"] = len(ccs)

        year_times[year_limit] = {"ccs_MUW": MUW, "times": time_sections}
    return year_times


def most_used_words(titles):
    start = perf_counter()

    # Combine all titles into a single string
    text = ' '.join(titles)
    text = text.lower()

    words = find_non_stopwords(text)

    words_number = len(words)

    # Count the occurrences of each word
    word_counts = Counter(words)

    # Get the 10 most common words and their frequencies
    most_common_words = word_counts.most_common(10)

    total_words = word_counts.total()

    most_common_words = [(word, (quantity / total_words) * 100) for word, quantity in most_common_words]

    return {"common_words": most_common_words, "time": perf_counter() - start, "total_words": words_number}


def find_non_stopwords(text):
    stopwords_pattern = r'\b(?:and|but|or|the|a|an|in|on|at|is|are|was|were|to|for|of|with|from)\b'
    non_stopwords = re.findall(r'\b(?!(?:' + stopwords_pattern + r')\b)\w+\b', text)
    return non_stopwords


if __name__ == "__main__":
    main()
