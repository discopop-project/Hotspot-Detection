from os import walk
import os.path
import numpy as np
import json
import sys
from typing import Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
import matplotlib.pyplot as plt
import jsonpickle

from discopop_library.result_classes.DetectionResult import DetectionResult

inf = float("inf")
LINENUM = int
FILENUM = int

@dataclass
class HotspotComparatorArguments(object):
    """Container Class for the arguments passed to the hotspot comparator"""
    baseline: str  # path to .discopop folder of the baseline code
    updated: str  # path to .discopop folder of the updated code
    number: int  # execution number to be compared
    plot: bool

    def __post_init__(self):
        self.__determine_number()
        self.__validate()

    def __determine_number(self):
        if self.number != -1:
            return
        
        baseline_numbers = []
        for filename in next(walk(os.path.join(self.baseline, "hotspot_detection", "private")), (None, None, []))[2]:  # [] if no file
            if filename.startswith("hotspot_result_"):
                number = int(filename.replace("hotspot_result_", "").replace(".txt", ""))
                baseline_numbers.append(number)

        updated_numbers = []
        for filename in next(walk(os.path.join(self.updated, "hotspot_detection", "private")), (None, None, []))[2]:  # [] if no file
            if filename.startswith("hotspot_result_"):
                number = int(filename.replace("hotspot_result_", "").replace(".txt", ""))
                updated_numbers.append(number)

        overlap = [n for n in baseline_numbers if n in updated_numbers]
        if len(overlap) == 0:
            raise ValueError("No overlapping measurement numbers!")
        self.number = sorted(overlap)[-1]  # select highest number


    def __validate(self):
        """Validate the arguments passed to the hotspot_comparator, e.g check if given files exist"""
        validation_failure = False
        required = [self.baseline, self.updated, os.path.join(self.baseline, "hotspot_detection", "private", "hotspot_result_" + str(self.number) + ".txt"), os.path.join(self.updated, "hotspot_detection", "private", "hotspot_result_" + str(self.number) + ".txt"), os.path.join(self.updated, "patch_applicator", "applied_suggestions.json" ), os.path.join(self.updated, "explorer", "detection_result_dump.json")]
        for file in required:
            if not os.path.exists(file):
                raise FileNotFoundError(file)

        if validation_failure:
            print("Exiting...")
            sys.exit()



def run(arguments: HotspotComparatorArguments) -> List[int]:    
    # returns the suggestion ids which have gotten slower compared to the baseline version


    #print("Baseline: ", arguments.baseline)
    #print("Updated: ", arguments.updated)
    #print("Number: ", arguments.number)
    
    
    # read baseline values
    baseline_file_path = os.path.join(arguments.baseline, "hotspot_detection", "private", "hotspot_result_" + str(arguments.number) + ".txt")
    baseline_values: Dict[int, float] = dict()
    with open(baseline_file_path, "r") as f:
        for line in f.readlines():
            line = line.replace("\n", "")
            split_line = line.split(" ")
            baseline_values[int(split_line[0])] = float(split_line[1])

    # read updated values
    updated_file_path = os.path.join(arguments.updated, "hotspot_detection", "private", "hotspot_result_" + str(arguments.number) + ".txt")
    updated_values: Dict[int, float] = dict()
    with open(updated_file_path, "r") as f:
        for line in f.readlines():
            line = line.replace("\n", "")
            split_line = line.split(" ")
            updated_values[int(split_line[0])] = float(split_line[1])

    # clean values
    remove: List[int] = []
    for key in baseline_values:
        if key not in updated_values:
            remove.append(key)
    for key in remove:
        del baseline_values[key]

    remove = []
    for key in updated_values:
        if key not in baseline_values:
            remove.append(key)
    for key in remove:
        del updated_values[key]

    # Identify slower code sections
    slower_cs: List[int] = []
    for key in baseline_values:
        if updated_values[key] > baseline_values[key]:
            slower_cs.append(key)
    #print("SLOWER CS`s: ")
    #print(slower_cs)

    # translate cs ids to file ids and line numbers
    slower_positions: List[Tuple[int, int]] = []
    cs_id_dict: Dict[int, Tuple[str, LINENUM, FILENUM, str]] = dict()
    with open(os.path.join(arguments.baseline, "hotspot_detection","private", "cs_id.txt"), "r") as f:
        for line in f.readlines():
            line = line.replace("\n", "")
            split_line = line.split(" ")
            if len(split_line) == 4:
                cs_id_dict[int(split_line[0])] = (split_line[1], int(split_line[2]), int(split_line[3]), "")
            elif len(split_line) == 5:
                cs_id_dict[int(split_line[0])] = (split_line[1], int(split_line[2]), int(split_line[3]), split_line[4])
            else:
                raise ValueError("Unsupported format: " + str(split_line))

    #print("FULL: ")
    #print([cs_id_dict[key] for key in slower_cs])

    if arguments.plot:
        plot(baseline_values, updated_values, cs_id_dict)

#    for cs_id in slower_cs:
#        slower_positions.append((cs_id_dict[cs_id][2], cs_id_dict[cs_id][1]))
    #print("SLOWER POSITIONS:")
    #print(slower_positions)

    # translate slower positions to suggestion ids if applied
    applied_suggestion_ids: List[int] = []
    with open(os.path.join(arguments.updated, "patch_applicator", "applied_suggestions.json" ), "r") as f:
        d = json.load(f)
        if "applied" in d:
            applied_suggestion_ids = [int(id) for id in d["applied"]]
    #print("applied suggestion ids: ", applied_suggestion_ids)

    # load suggestions
    with open(os.path.join(arguments.updated, "explorer", "patterns.json"), "r") as f:
        detected_patterns = json.load(f)
    
#    print("ALL SLOWER: ", slower_positions)

    slower_suggestion_ids: List[int] = []
    
    for suggestion_id in applied_suggestion_ids:
        # find pattern information
        found_pattern = False
        pattern = dict()
        for pattern_type in detected_patterns["patterns"]:
            for pattern_entry in detected_patterns["patterns"][pattern_type]:
                if pattern_entry["pattern_id"] == suggestion_id:
                    pattern = pattern_entry
                    found_pattern = True
                    break
            if found_pattern:
                break
        if not found_pattern:
            continue

    
        if "affected_functions" not in pattern:
            continue
        cleaned_affected_functions = [(int(f.split(":")[0]), f.split(":")[2]) for f in pattern["affected_functions"]]
        for slow_cs_id in slower_cs:
            # check if the pattern is potentially detremental to function execution times
            if cs_id_dict[slow_cs_id][0] != "func":
                continue

            cleaned_slow_function = (cs_id_dict[slow_cs_id][2], cs_id_dict[slow_cs_id][3])

            if cleaned_slow_function in cleaned_affected_functions:
                slower_suggestion_ids.append(suggestion_id)
                break


            # check if the pattern is potentially detremental
#            slower_position_line_id = str(slower_position[0]) + ":" + str(slower_position[1])
#            is_potentially_slower = False
#            print("SLOWER: ", slower_position_line_id)
#            print("AFFECTED FUNCTIONS:", pattern["affected_functions"])
#            if slower_position_line_id in pattern["affected_line_ids"]:
#                if suggestion_id not in slower_suggestion_ids:
#                    is_potentially_slower = True        
#            if not is_potentially_slower:
#                continue
#
#            # if the pattern is potentially detremental to the programs performance, check its effects in detail by summing up total differences.        
#            runtime_difference = 0.0
#            for cs_id in cs_id_dict:
#                line_id = str(cs_id_dict[cs_id][2]) + ":" + str(cs_id_dict[cs_id][1])
#                if line_id in pattern["affected_line_ids"]:
#                    runtime_difference += updated_values[cs_id] - baseline_values[cs_id]
#            print("PATTERN: ", suggestion_id, " -> DIFF: ", runtime_difference)
#
#            if runtime_difference > 0:
#                slower_suggestion_ids.append(suggestion_id)

    #print("Slower suggestion ids:")
    print(slower_suggestion_ids)

    return slower_suggestion_ids

def __get_lineid_string(cs_id: int, cs_id_dict: Dict[int, Tuple[str, LINENUM, FILENUM, str]]) -> str:
    return "" + str(cs_id_dict[cs_id][2]) + ":" + str(cs_id_dict[cs_id][1])

def plot(baseline_values: Dict[int, float], updated_values: Dict[int, float], cs_id_dict: Dict[int, Tuple[str, LINENUM, FILENUM, str]]):
    # sort keys descending by runtime contribution
    tuples = [(baseline_values[key], key) for key in baseline_values]
    sorted_tuples = sorted(tuples, key=lambda x: x[0], reverse=True)
    sorted_keys = [tpl[1] for tpl in sorted_tuples]

    #names = [__get_lineid_string(key, cs_id_dict) for key in sorted_keys]
    names = [str(key) for key in sorted_keys]

    # determine values for plotting
    contribution_values = [baseline_values[key] for key in sorted_keys]
    updated_contribution_values = [updated_values[key] for key in sorted_keys]
    diff_values = [updated_values[key] - baseline_values[key] for key in sorted_keys]
    abs_diff_values = [abs(val) for val in diff_values]

    # determine axis scale
    y_value_range = [0, max(contribution_values + updated_contribution_values + abs_diff_values)]

    # plot runtime contribution
    contribution_colors = ["grey" for value in contribution_values]
    ax1 = plt.subplot(3,1,1)
    ax1.bar(names, contribution_values, color=contribution_colors)
    ax1.set_xlabel("CS_ID")
    ax1.set_ylabel("baseline runtime (s)")
    ax1.set_ylim(y_value_range)

    # plot updated runtime
    updated_contribution_colors = ["grey" for value in updated_contribution_values]
    ax2 = plt.subplot(3,1,2, sharex=ax1, sharey=ax1)
    ax2.bar(names, updated_contribution_values, color=updated_contribution_colors)
    ax2.set_xlabel("CS_ID")
    ax2.set_ylabel("updated runtime (s)")
    ax2.set_ylim(y_value_range)

    # plot differences
    diff_colors = ["red" if value > 0 else "green" for value in diff_values]
    ax3 = plt.subplot(3,1,3, sharex=ax1, sharey=ax1)
    ax3.bar(names, abs_diff_values, color=diff_colors)
    ax3.set_xlabel("CS_ID")
    ax3.set_ylabel("runtime difference (s)")
    ax3.set_ylim(y_value_range)

    plt.show()