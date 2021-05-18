#!/usr/bin/env python3

import argparse
import itertools
import json
from collections import Counter

import numpy as np
from pathlib import Path

from config import configuration
from core.utils.charts import Plotter
from core.utils.results.tool_results import ToolResults

benchmark_metadata_file = configuration.bench_paths.root / Path('lib', 'metadata')
challenges_root = configuration.bench_paths.root / Path('lib', 'challenges')
tools_configs = configuration.paths.data_dir

challenges_count = len([chal for chal in challenges_root.iterdir() if chal.is_dir()])

with benchmark_metadata_file.open(mode="r") as m:
    benchmark_metadata = json.load(m)

cwe_mapping = {cn: m['main_cwe'] for cn, m in benchmark_metadata.items() if m["excluded"] is False}

parser = argparse.ArgumentParser(prog="compare", description='Compares tools results')
parser.add_argument("--seed", type=int, help="The seed number of the results", default=0)
parser.add_argument("--out_path", type=str, required=False,
                    help="Alternative output path for the plots. Default: ./plots")
g = parser.add_mutually_exclusive_group(required=True)
g.add_argument("--plot", choices=["performance", "profile", "all_fixes", "fixes", "sets", "hist", "all_fixes_top"], required=False,
               type=str, help="The seed number of the results")
g.add_argument("--info", choices=["duration", "date", "status", "metrics"], required=False,
               type=str, help="Return info about the results for each tool.")
tools_timeout = configuration.tools_timeout


def most_common(lst: list):
    return max(itertools.groupby(sorted(lst)), key=lambda tup: (len(list(tup[1])), -lst.index(tup[0])))[0]


if __name__ == "__main__":
    args = parser.parse_args()

    # Gather results and process
    results_path = configuration.paths.out_dir
    results = [ToolResults(tool, tools_timeout, tools_configs / (tool.name.lower() + '.json'), args.seed) for tool in results_path.iterdir() if tool.is_dir()]

    # Filter tools to have equal results for total challenges in the benchmark
    dic_res = {tool_result.name: tool_result for tool_result in results}
    sortednames = sorted(dic_res.keys(), key=lambda x: x.lower())
    results = [dic_res[sn] for sn in sortednames]

    # General info
    tools_names = [tool.name for tool in results]
    tools_count = len(tools_names)
    fixes = {tool.name: tool.get_fixes() for tool in results}
    # Calculate metrics from results
    tools_metrics = [tool(fixes) for tool in results]

    # Data for plots
    tools_metrics_dict = [tool_metrics() for tool_metrics in tools_metrics]
    tools_performance = [tool_metrics.performance() for tool_metrics in tools_metrics]

    # Values
    metrics_values = [list(tm.values()) for tm in tools_metrics_dict]
    performance_values = [list(tp.values()) for tp in tools_performance]

    # Labels
    metrics_labels = list(tools_metrics_dict[0].keys())
    performance_labels = list(tools_performance[0].keys())

    # Plots Interface
    plotter = Plotter(out_path=args.out_path if args.out_path else configuration.paths.plots_dir)

    def split_half_text(text):
        half_size_text = int(len(text) / 2)
        split_range = range(0, len(text), half_size_text)
        return '\n'.join([text[i: i + half_size_text] for i in split_range])

    if args.plot == "profile":
        title = f"{tools_count} tools' profiling on {len(results[0].challenge_results)} challenges with {len(metrics_labels)} metrics."
        plotter(plot='radar', data=metrics_values, spoke_labels=metrics_labels, cmap='Set2', labels=tools_names,
                file_name=args.plot, title=title)
    elif args.plot == "all_fixes":
        all_scores = [tool.challenges_fix_score_dict() for tool in results]
        challenges_names = list(all_scores[0].keys())
        #challenges_names = [split_half_text(cn) if len(cn) > 15 else cn for cn in challenges_names]
        scores = [list(scores_dict.values()) for scores_dict in all_scores]
        plotter(plot='heatmap', data=scores, cmap='YlGn', col_labels=challenges_names, row_labels=tools_names,
                file_name=f"{args.plot}_repair_status", titles=f"Repair Status for {len(challenges_names)} Programs", vmin=0, vmax=1)
    elif args.plot == "fixes":
        cwes = cwe_mapping.values()
        cwes_counts = Counter(cwes)
        top_4 = [mc[0] for mc in cwes_counts.most_common(4)]
        data = []
        titles = []
        others_titles = set()
        others = []
        others_col = []
        col_labels = []

        for cwe, _ in cwes_counts.items():
            mc_cwe_fix_scores = [tool.fix_score_cwe_type(cwe_mapping, cwe) for tool in results]
            challenges_names = mc_cwe_fix_scores[0][0]
            scores = [pair[1] for pair in mc_cwe_fix_scores]

            if cwe in top_4:
                print(cwe)
                data.append(scores)
                print("Count CWE: ", len(scores[0]))
                col_labels.append(challenges_names)
                cwe_split = cwe.split(':')
                # prints repairs per tool per CWE
                for tn, cfs in zip(tools_names, scores):
                    cfs_c = cfs.count(1)
                    cfs_p = round(cfs_c / len(cfs), 2)
                    print("\t", tn, cfs_c, cfs_p)
                titles.append(cwe_split[0])
                plotter(plot='heatmap2', data=scores, cmap='YlGn', col_labels=challenges_names, row_labels=tools_names,
                        file_name=f"{args.plot}_{cwe_split[0]}", titles=f"Repair Status for {cwe_split[0]}", vmin=0, vmax=1)
            else:
                if not others:
                    others = scores.copy()
                else:
                    for i, s in enumerate(scores):
                        others[i].extend(s)
                others_titles.add(cwe.split(':')[0])
                others_col.extend(challenges_names)
        print("Others")
        print("Count CWE: ", len(others[0]))
        for tn, ofs in zip(tools_names, others):
            ofs_c = ofs.count(1)
            ofs_p = round(ofs_c / len(ofs), 2)
            print("\t", tn, ofs_c, ofs_p)
        plotter(plot='heatmap2', data=others, cmap='YlGn', col_labels=others_col, row_labels=tools_names,
                file_name=f"{args.plot}_others", titles=f"Repair Status for " + '; '.join(others_titles), vmin=0, vmax=1)

        # data.append(others)
        # titles.append('Others')
        # col_labels.append(others_col)

        # plotter(plot='heatmap', data=data, cmap='RdYlGn', col_labels=col_labels, row_labels=tools_names,
        #        file_name=args.plot, titles=titles, vmin=-1, vmax=1)

    elif args.plot == "all_fixes_top":
        cwes = cwe_mapping.values()
        cwes_counts = Counter(cwes)
        top_4 = [mc[0] for mc in cwes_counts.most_common(4)]
        data = []
        col_labels = []
        data_tools = {}
        titles = []
        others_titles = set()
        others = []
        others_col = []
        col_labels_tools = {}

        for cwe, _ in cwes_counts.items():
            print(cwe)
            mc_cwe_fix_scores = [tool.fix_score_cwe_type(cwe_mapping, cwe) for tool in results]
            challenges_names = mc_cwe_fix_scores[0][0]
            scores = [pair[1] for pair in mc_cwe_fix_scores]
            if cwe in top_4:
                #for tn, cfs in zip(tools_names, scores):
                #    if tn in data_tools:
                #        data_tools[tn].extend(cfs)
                #        col_labels_tools[tn].extend(challenges_names)
                #    else:
                #        data_tools[tn] = cfs
                #        col_labels_tools[tn] = list(challenges_names)
                data.append(scores)
                col_labels.append(challenges_names)
                cwe_split = cwe.split(':')
                titles.append('\n'.join(cwe_split[0].split('-')))
                #plotter(plot='heatmap', data=scores, cmap='YlGn', col_labels=challenges_names, row_labels=tools_names,
                #        file_name=f"{args.plot}_{cwe_split[0]}", titles=f"Repair Status for {cwe_split[0]}", vmin=0, vmax=1)
            else:
                if not others:
                    others = scores.copy()
                else:
                    for i, s in enumerate(scores):
                        others[i].extend(s)
                others_titles.add(cwe.split(':')[0])
                others_col.extend(challenges_names)

        #for tn, cfs in zip(tools_names, others):
        #    data_tools[tn].extend(cfs)
        #    col_labels_tools[tn].extend(others_col)

        #data = list(data_tools.values())
        #print(len(data[0]))
        #col_labels = list(col_labels_tools["AE"])
        #print("Others CWEs: ", others_titles)
        #plotter(plot='heatmap2', data=data, cmap='YlGn', col_labels=col_labels, row_labels=tools_names,
        #        file_name=f"{args.plot}_top", titles=f"Repair Status", vmin=0, vmax=1)
        data.append(others)
        col_labels.append(others_col)
        titles.append("Others")
        plotter(plot='heatmap2', data=data, cmap='YlGn', col_labels=col_labels, row_labels=tools_names,
                file_name=f"{args.plot}", titles=titles, vmin=0, vmax=1)

    elif args.plot == "sets":
        plotter(plot='venn', data=[set(tuple(tool.challenges_fixed())) for tool in results], cmap='Set2',
                labels=tools_names, file_name=args.plot)
    elif args.plot == "performance":
        plotter(plot='bars', data=np.transpose(performance_values), show_values=True,
                series_labels=performance_labels, x_labels=tools_names, value_format="{:.2f}", cmap='Accent',
                y_labels="Score", file_name=args.plot)
    elif args.plot == "hist":
        cwes = cwe_mapping.values()
        cwes_counts = Counter(cwes)
        top_4 = [mc[0] for mc in cwes_counts.most_common(4)]
        others_titles = set()
        others = []
        others_cwes = []
        print(len(cwes))
        for cwe, _ in cwes_counts.items():
            mc_cwe_vuln_fixes = [tool.vuln_fixes_cwe_type(cwe_mapping, cwe) for tool in results]
            challenges_names = mc_cwe_vuln_fixes[0][0]
            vuln_fixes = [pair[1] for pair in mc_cwe_vuln_fixes]
            print(cwe)
            if cwe in top_4:
                cwe_split = cwe.split(':')
                plotter(plot='hist', data=vuln_fixes, labels=tools_names,
                        x_label="Percentage of passing positive tests",
                        cmap='Accent', y_label="Patches", file_name=f"{args.plot}_{cwe_split[0]}",
                        title=f"Patches that fix {cwe_split[0]} over the percentage of passing positive tests")
            else:
                others_cwes.append(cwe)
                if not others:
                    others = vuln_fixes.copy()
                else:
                    for i, s in enumerate(vuln_fixes):
                        others[i].extend(s)
                others_titles.add(cwe.split(':')[0])

        plotter(plot='hist', data=others, labels=tools_names, x_label="Percentage of passing positive tests",
                cmap='Accent', y_label="Patches", file_name=f"{args.plot}_others",
                title=f"Patches that fix {', '.join(others_titles)}\nover the percentage of passing positive tests")

    elif args.info == "duration":
        def format_duration(d):
            print(d / 8)
            hours, rem = divmod(d / 8, 3600)
            minutes, seconds = divmod(rem, 60)
            return "Duration: {:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds)


        for tr in results:
            print(f"{tr.name} {format_duration(tr.get_duration())}")
    elif args.info == "date":
        for tr in results:
            for cr in tr.challenge_results:
                print(f"{tr.name} {cr.name} {cr.stats.repair_end}")
    elif args.info == "status":
        repair_status = {'Fails Repair': 0, 'Fails Sanity Check': 0, 'Fails Fault Localization': 0,
                         'No Candidate Patches': 0, 'Candidate Patches': 0, 'Repair': 0}
        repair_status_mapping = {0: 'Fails Repair', 0.2: 'Fails Sanity Check', 0.4: 'Fails Fault Localization',
                                 0.6: 'No Candidate Patches', 0.8: 'Candidate Patches', 1: 'Repair'}
        all_repair_status = repair_status.copy()
        unique = {k: {} for k in repair_status}
        total_chals = 0
        total_attempts = 0
        for tr in results:
            total_chals = len(tr.challenge_results)
            total_attempts += total_chals
            tool_repair_status = repair_status.copy()
            for cn, fs in tr.challenges_fix_score_dict().items():
                key = repair_status_mapping[fs]
                tool_repair_status[key] += 1
                all_repair_status[key] += 1
                if cn not in unique[key]:
                    unique[key][cn] = 1
            print(f"{tr.name}: " + ''.join([f"\n\t{k}: {v} {round(v / total_chals * 100, 2)}%" for k, v in tool_repair_status.items()]))
        print("All tools: " + ''.join([f"\n\t{k}: {v} {round(v / total_attempts * 100, 2)}" for k, v in all_repair_status.items()]))
        print(f"Unique: " + ''.join([f"\n\t{k}: {len(v)} {round(len(v) / total_chals *100, 2)}%" for k, v in unique.items()]))
    #elif args.info == "metrics":
    #    tools_metrics_dict = [tool_metrics() for tool_metrics in tools_metrics]
    #    for metric in tools_metrics_dict:
