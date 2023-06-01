import os
import pickle as pkl
import sys
from time import perf_counter

import numpy as np


def main():
    os.chdir(os.path.dirname(sys.argv[0]))
    os.makedirs("results/question_1", exist_ok=True)

    for graph_filename in os.listdir("graphs/bipartite"):
        with open(f"graphs/bipartite/{graph_filename}", "rb") as graph_file:
            G = pkl.load(graph_file)

        print(G)

        print("#### AVERAGE PUBLICATION ####")
        years_avg, times = averagePublications(G)
        print(years_avg)
        print(times)

        with open(f"results/question_1/{graph_filename}_results.pkl", "wb") as result_file:
            pkl.dump((years_avg, times), result_file)


def averagePublications(G):
    time_sections = {}

    time_sections["pub_calculation"] = perf_counter()

    years, num_titles = np.unique([d["year"] for _, d in G.nodes(data=True) if not d["author"]], return_counts=True)

    time_sections["pub_calculation"] = perf_counter() - time_sections["pub_calculation"]

    time_sections["years_calculation"] = perf_counter()

    last_year_idx = 0
    year_limits = [1960, 1970, 1980, 1990, 2000, 2010, 2020, 2023]

    average_publications = {}

    for i, year_limit in enumerate(year_limits):
        for j, year in enumerate(years[last_year_idx:], start=last_year_idx):
            if year <= year_limit:
                average_publications[year_limit] = average_publications.get(year_limit, default=0) + num_titles[j]
            else:
                last_year_idx = j
                break
        if year_limit != year_limits[-1]:
            average_publications[year_limits[i + 1]] = average_publications[year_limit]
        average_publications[year_limit] /= year_limit - years[0]

    time_sections["years_calculation"] = perf_counter() - time_sections["years_calculation"]

    return average_publications, time_sections


if __name__ == "__main__":
    main()
