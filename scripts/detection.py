import os.path
import numpy as np
import json
from typing import List
from enum import Enum

inf = float("inf")


class cs:
    def __init__(self, csid):
        self.csid = csid  # note: csid is a unique identifier
        self.typ = False  # function is false, loop is true
        self.fid = 0  # file id
        self.lineNum = 0  # line number
        self.name = ""  # only for functions: name of function
        self.runtimes = []  # runtimes
        self.level = 0
        self.hot = True
        self.hotness = "MAYBE"  # possible: YES, NO, MAYBE
        self.discopop_file_id = -1  # -1 as a marker for "no id"

    delta = -1.0
    avr = 0.0
    sum = -1
    minVal = inf
    maxVal = 0.0
    ratio = 0.0
    topAvr = False
    topRatio = False

    def toJSON(self):
        return json.dumps(self.__dict__, indent=4)

    def addData(self, runtime):
        self.runtimes.append(runtime)

    def addInfo(self, tp, linN, filN, namN):
        self.typ = tp
        self.lineNum = linN
        self.fid = filN
        self.name = namN

    def updateLevel(self, lvl):
        self.level = lvl

    def calMin(self):
        for x in self.runtimes:
            self.minVal = min(x, self.minVal)

    def roundMin(self):
        if self.minVal == 0:
            self.minVal = 0.000001

    def calMax(self):
        for x in self.runtimes:
            self.maxVal = max(x, self.maxVal)

    def calDelta(self):
        self.delta = self.maxVal - self.minVal

    def calRatio(self):
        self.ratio = 1 / ((self.minVal / self.maxVal) + 1)

    def calAvr(self):
        tempSum = 0
        for i in self.runtimes:
            tempSum += i
        self.avr = tempSum / len(self.runtimes)
        self.sum = tempSum

    def isHot(self, bl):
        self.hot = bl

    def isTopAvr(self, bl):
        self.topAvr = bl

    def isTopRatio(self, bl):
        self.topRatio = bl

    def getHotness(self):
        if self.topAvr == True and self.topRatio == True:
            return "YES"
        if self.topAvr != self.topRatio:
            return "MAYBE"
        return "NO"


def __print_cs_list(list: List[cs]):
    for x in list:
        print(
            "##cs lists:",
            str(x.typ).ljust(6),
            str(x.csid).ljust(2),
            str(x.fid).ljust(2),
            "{:10.7f}".format(x.runtimes[0]),
            "avr:" + "{:10.7f}".format(x.avr),
            "sum:" + "{:10.7f}".format(x.sum),
            f"ratio:{x.ratio} min:{x.minVal} max:{x.maxVal} topAvr:{x.topAvr} topRatio:{x.topRatio}",
        )
    print(len(list))


def main():
    ## CS LIST
    # TODO turn this into a Dict
    cslist: List[cs] = []

    def findCs(iid):
        for x in cslist:
            if x.csid == iid:
                return x
        return False

    def getHots(bl):
        Hots = []
        for x in cslist:
            if x.hot == bl:
                Hots.append(x)
        return Hots

    def getSum(lst):
        hotSum = 0
        for i in lst:
            hotSum += i.avr
        return hotSum

    ## READ FILES
    idfile = open("hotspot_result_0.txt", "r")
    for line in idfile:
        c = cs(int(line.split()[0]))
        cslist.append(c)
    idfile.close()

    i = 0
    resultNum = 0
    minData = inf
    maxData = 0
    while True:
        fileName = f"hotspot_result_{i}.txt"
        i += 1
        if os.path.exists(fileName):
            # print("a file")
            pass
        else:
            # print("no file")
            break
        resultNum += 1
        dataFile = open(fileName, "r")
        for line in dataFile:
            temp = []
            for word in line.split():
                temp.append(word)
            tempCs = findCs(int(temp[0]))
            tempCs.addData(float(temp[1]))
        dataFile.close()

    csfile = open("cs_id.txt", "r")
    for line in csfile:
        temp = []
        for word in line.split():
            temp.append(word)

        tempCs = findCs(int(temp[0]))
        if temp[1] == "func":
            tempCs.addInfo(False, int(temp[2]), int(temp[3]), "func")
        if temp[1] == "loop":
            tempCs.addInfo(True, int(temp[2]), int(temp[3]), "loop")
    csfile.close()

    ## CALCULATE
    vMAX = 0
    vMIN = inf
    dMAX = 0
    dMIN = inf
    deltaData = maxData - minData
    ratioData = maxData / minData

    __print_cs_list(cslist)

    NZcslist: List[cs] = []

    for j in cslist:
        j.calAvr()

    for m in cslist:
        if m.sum > 0:
            NZcslist.append(m)

    for j in NZcslist:
        j.calMin()
        j.calMax()
        j.calAvr()

    for j in NZcslist:
        j.roundMin()
        j.calDelta()
        j.calRatio()

    tempmax = 0

    for x in NZcslist:
        if x.maxVal >= tempmax:
            tempmax = x.maxVal
            maxCS = x

    print("max cs: ", maxCS.csid, " ", maxCS.maxVal)

    # sorting cs list based on avr and ratio
    sortedCsAvr = NZcslist.copy()
    sortedCsAvr.sort(key=lambda x: x.avr, reverse=True)

    sortedCsRatio = NZcslist.copy()
    sortedCsRatio.sort(key=lambda x: x.ratio, reverse=True)

    # detecting hotspots of each list by mean or median
    mean = True
    if mean:
        avrMiddle = np.mean([x.avr for x in NZcslist])
        ratioMiddle = np.mean([x.ratio for x in NZcslist])
    else:
        avrMiddle = np.median([x.avr for x in NZcslist])
        ratioMiddle = np.median([x.ratio for x in NZcslist])

    for x in NZcslist:
        if x.avr >= avrMiddle:
            x.isTopAvr(True)

    for x in NZcslist:
        if x.ratio >= ratioMiddle:
            x.isTopRatio(True)

    # print
    __print_cs_list(NZcslist)
    print(ratioMiddle)

    ## WRITE OUT RESULTS

    with open("hotspot_result.txt", "w") as f:
        for x in NZcslist:
            f.write(f"{x.csid} {x.ratio} {x.avr} {x.minVal} {x.maxVal} {x.getHotness()}\n")

    # categorize Hotspots based on my definition
    f = open("Hotspots.txt", "w")
    f.write("Is this code region a hotspot? \n")
    counterY = 0
    counterM = 0
    counterN = 0
    for x in NZcslist:
        if x.topAvr == True and x.topRatio == True:
            counterY += 1
            yesNoMaybe = " is YES"
            x.hotness = "YES"
        if x.topAvr != x.topRatio:
            counterM += 1
            yesNoMaybe = " is MAYBE"
            x.hotness = "MAYBE"
        if x.topAvr == False and x.topRatio == False:
            counterN += 1
            yesNoMaybe = " is NO"
            x.hotness = "NO"
        f.write(str(x.csid) + " " + str(x.name) + " at " + str(x.fid) + ":" + str(x.lineNum) + yesNoMaybe + "\n")
        # f.write(" "+ str(x.topAvr)+" "+ str(x.topRatio)+"\n")
    f.write("Number of YES code regions: " + str(counterY) + " \n")
    f.write("Number of MAYBE code regions: " + str(counterM) + " \n")
    f.write("Number of NO code regions: " + str(counterN) + " \n")
    f.write("Number of Non-zero code regions: " + str(counterN + counterM + counterY) + " \n")
    f.close()
    print("End")

    
    # map hotspot detection file id to discopop file if (TODO: this solution is not nice and should be replaced in the future)
    file_id_mapping = dict()
    # TODO: make this more robust
    if not os.path.exists("FileMapping.txt"):
        raise FileNotFoundError("FileMapping.txt not found in the current working directory!")
    # get discopop filemapping
    discopop_file_mapping = dict()
    with open("FileMapping.txt", "r") as dp_fmap:
        for line in dp_fmap:
            line = line.replace("\n", "")
            split_line = line.split("\t")
            file_id = int(split_line[0])
            file_path = split_line[1]
            discopop_file_mapping[file_id] = file_path
    
    # get hotspot detection file mapping
    if not os.path.exists("file_mapping.txt"):
        raise FileNotFoundError("file_mapping.txt not found in the current working directory!")
    hotspot_file_mapping = dict()
    with open("file_mapping.txt", "r") as hotspot_fmap:
        line_id = 1
        for line in hotspot_fmap:
            line = line.replace("\n", "")
            file_name = line
            hotspot_file_mapping[line_id] = file_name
            line_id += 1

    # match discopop and hotspot detection file mappings
    for file_id in hotspot_file_mapping:
        for dp_file_id in discopop_file_mapping:
            if os.path.join(os.getcwd(), hotspot_file_mapping[file_id]) == discopop_file_mapping[dp_file_id]:
                file_id_mapping[file_id] = dp_file_id

    # add discopop_file_id to cs
    for x in NZcslist:
        if x.fid in file_id_mapping:
            x.discopop_file_id = file_id_mapping[x.fid]

    # export results to Hotspots.json
    with open("Hotspots.json", "w+") as outfile:
        outfile.write("{\"code_regions\": [")
        for id, x in enumerate(NZcslist):
            outfile.write(x.toJSON())
            if id != len(NZcslist) - 1:
                outfile.write(",\n")
            else:
                # last element of the list
                outfile.write("\n")
        outfile.write("]\n")
        outfile.write("}\n")

if __name__ == "__main__":
    main()
