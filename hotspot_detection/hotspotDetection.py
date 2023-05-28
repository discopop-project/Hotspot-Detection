from functools import singledispatch
from typing import Dict, List

import numpy as np


def hotspot_ratio(values: List[float]) -> float:
    min = values[0]
    max = values[0]
    if(max == 0):
        return 0.5
    for v in values:
        if v < min:
            min = v
        if v > max:
            max = v

    return 1 / ((min/max) + 1)


def hotspot_ratios(values: Dict[int, List[float]]) -> Dict[int, List[float]]:
    return {k:hotspot_ratio(v) for k,v in values}



def __read_results_file(file_name: str) -> Dict[int,float]:
    with open(file_name, "r") as f:
        lines = f.readlines()
        lines = [line.strip() for line in lines]
        lines = {int(line.split()[0]) : float(line.split()[1]) for line in lines}
        return lines
    

def __read_results_files(file_names: str) -> Dict[int, List[float]]:
    result = {}
    for file_name in file_names:
        r = __read_results_file(file_name)
        for k, v in r.items():
            if k not in result:
                result[k] = []
            result[k].append(v)
    return result


def read_and_write_results(file_names: List[str], output_file_name: str):
    results = __read_results_files(file_names)
    with open(output_file_name, "w") as f:
        for k, v in results.items():
            f.write(f"{k} {hotspot_ratio(v)}\n")
                    
