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


@dataclass
class HotspotComparatorArguments(object):
    """Container Class for the arguments passed to the hotspot comparator"""
    baseline: str  # path to .discopop folder of the baseline code
    updated: str  # path to .discopop folder of the updated code
    number: int  # execution number to be compared

    def __post_init__(self):
        self.__validate()

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

    # plot(baseline_values, updated_values)

    # Identify slower code sections
    slower_cs: List[int] = []
    for key in baseline_values:
        if updated_values[key] > baseline_values[key]:
            slower_cs.append(key)
    #print("SLOWER CS`s: ")
    #print(slower_cs)

    # translate cs ids to file ids and line numbers
    slower_positions: List[Tuple[int, int]] = []
    cs_id_dict: Dict[int, Tuple[str, int, int, str]] = dict()
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

    for cs_id in slower_cs:
        slower_positions.append((cs_id_dict[cs_id][2], cs_id_dict[cs_id][1]))
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
    with open(os.path.join(arguments.updated, "explorer", "detection_result_dump.json"), "r") as f:
        tmp_str = f.read()
    detection_result: DetectionResult = jsonpickle.decode(tmp_str)  # type: ignore
    
    slower_suggestion_ids: List[int] = []
    for slower_position in slower_positions:
        for suggestion_id in applied_suggestion_ids:
            pattern = detection_result.patterns.get_pattern_from_id(suggestion_id)
            pattern_file_id = int(pattern.start_line.split(":")[0])
            pattern_start_line = int(pattern.start_line.split(":")[1])
            if slower_position[0] == pattern_file_id and slower_position[1] == pattern_start_line:
                slower_suggestion_ids.append(suggestion_id)

    #print("Slower suggestion ids:")
    print(slower_suggestion_ids)

    return slower_suggestion_ids


def plot(baseline_values: Dict[int, float], updated_values: Dict[int, float]):
    print("Plotting...")



    names = [str(key) for key in baseline_values]
    values = [updated_values[key] - baseline_values[key] for key in baseline_values]
    colors = ["red" if value > 0 else "green" for value in values]

    plt.figure(figsize=(9, 4))

    plt.subplot(131)
    plt.bar(names, values, color=colors)

    plt.xlabel("CS_ID")
    plt.ylabel("runtime difference (s)")

    plt.show()