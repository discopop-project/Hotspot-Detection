# This file is part of the DiscoPoP software (http://www.discopop.tu-darmstadt.de)
#
# Copyright (c) 2020, Technische Universitaet Darmstadt, Germany
#
# This software may be modified and distributed under the terms of
# the 3-Clause BSD License.  See the LICENSE file in the package base
# directory for details.

from argparse import ArgumentParser
import os

from .hotspot_comparator import HotspotComparatorArguments, run


def parse_args() -> HotspotComparatorArguments:
    """Parse the arguments passed to the hotspot_comparator"""
    parser = ArgumentParser(description="Hotspot Comparator")

    parser.add_argument("-b", "--baseline", type=str, default=os.getcwd(), help="Path to .discopop folder of the baseline implementation. Make sure executions of baseline and update use the same input sizes.")
    parser.add_argument("-u", "--updated", type=str, default=os.getcwd(), help="Path to .discopop folder of the updated implementation. Make sure executions of baseline and update use the same input sizes.")
    parser.add_argument("-p", "--plot", action="store_true", help="Plot the runtime differences of both configurations" )
    parser.add_argument("-n", "--execution_number", type=int, default=-1, help="ID of the compared execution. Default: latest")
    arguments = parser.parse_args()

    return HotspotComparatorArguments(baseline = arguments.baseline, updated = arguments.updated, number = arguments.execution_number, plot = arguments.plot)


def main():
    arguments = parse_args()
    run(arguments)


if __name__ == "__main__":
    main()
