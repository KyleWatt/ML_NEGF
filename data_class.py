import numpy as np
from os.path import join
import os
import argparse
import pandas as pd
import matplotlib as plt

parser = argparse.ArgumentParser()
parser.add_argument("--root", type=str, nargs="?", help="root")
parser.add_argument("--target", type=str, nargs="?", help="target")
args = parser.parse_args()


def find_max_tier(df, row):
    result = df.query(
        "Plane == '{}' and VG == '{}' and VD == '{}' and Location == '{}' and Type == '{}' and Criteria == '{}' and Height == '{}' and Width == '{}'".format(
            row["Plane"],
            row["VG"],
            row["VD"],
            row["Location"],
            row["Type"],
            row["Criteria"],
            row["Height"],
            row["Width"],
        )
    )

    return result.max()["Iteration"]

def rreplace(s, old, new, occurrence):
    li = s.rsplit(old, occurrence)
    return new.join(li)


class Aggregator:
    def __init__(self, args):
        self.root = args.root
        self.target = args.target

        self.df = (
            pd.DataFrame()
        )  # [plane, vg, vd, location, type, iter, crit, width, height, path]
        self.df_cond = (
            pd.DataFrame()
        )  # [plane, vg, vd, location, type, iter, crit, width, height, path, mean, std, cmpPath, tarPath]

    def save(self, filename, condFlag=0):
        try:
            os.mkdir(join(self.target))
        except Exception as e:
            print("Found target dir")

        if condFlag == 0:
            self.df.to_csv(join(self.target, filename))
            print("Saved Dataframe to .csv!")
        else:
            self.df_cond.to_csv(join(self.target, filename))

    def read(self):
        # getting all files from all subdirectories and paths to said files
        print("Reading Files...")
        imgs = []
        name_as_lst = []
        VGnums = set()
        VDnums = set()
        target_prefix = "NEGF"

        filenum = 0
        filenames = []
        for root, dirs, files in os.walk(self.root):
            for name in files:
                if name.startswith(target_prefix):
                    path = os.path.join(root, name)
                    name = str(name).split(".txt")[0]  # Removing .txt at end of strings
                    name_as_lst = name.split("_")  # Spliting to
                    XY = name_as_lst.pop(0)[-2:]
                    name_as_lst.insert(0, XY)
                    Criteria = str(root).split("/")[-3]
                    Shape = str(root).split("/")[-2].split("x")
                    Height = Shape[0]
                    Width = Shape[1]
                    imgs.append(name_as_lst + [Criteria, Height, Width] + [path])

        df = pd.DataFrame(
            imgs,
            columns=[
                "Plane",
                "VG",
                "VD",
                "Location",
                "Type",
                "Iteration",
                "Criteria",
                "Height",
                "Width",
                "Path",
            ],
        )
        self.df = df
        print(self.df)

    def condition(self):
        # Condition should go through the entire self.array and condition based on the iteration number and data type
        # Get all entries with iterator == 1, each entire to find max and mid values of same result
        dataList = []
        unique_devices = self.df.query("Iteration == '1' and Type == 'pot'")
        # [plane, vg, vd, location, type, iter, crit, width, height, path]

        try:
            os.mkdir(join(self.target))
        except Exception as e:
            print("Found target dir")

        for index, row in unique_devices.iterrows():

            tmpList = row.to_list()
            tmpList.pop(5)
            tmpList.pop(4)
            tmpList.pop(-1)

            inpPotPath = row["Path"]
            inpChargePath = rreplace(inpPotPath, "pot", "charge", 1)

            tar = find_max_tier(self.df, row)
            cmp = str(int(tar) // 2)

            tarPotPath = self.df.query(
                "Plane == '{}' and VG == '{}' and VD == '{}' and Location == '{}' and Type == '{}' and Iteration == '{}' and Criteria == '{}' and Height == '{}' and Width == '{}'".format(
                row["Plane"],
                row["VG"],
                row["VD"],
                row["Location"],
                row["Type"],
                tar,
                row["Criteria"],
                row["Height"],
                row["Width"],
                )
            ).iloc[0]["Path"]

            tarChargePath = rreplace(tarPotPath, "pot", "charge", 1)

            cmpPotPath = self.df.query(
                "Plane == '{}' and VG == '{}' and VD == '{}' and Location == '{}' and Type == '{}' and Iteration == '{}' and Criteria == '{}' and Height == '{}' and Width == '{}'".format(
                row["Plane"],
                row["VG"],
                row["VD"],
                row["Location"],
                row["Type"],
                cmp,
                row["Criteria"],
                row["Height"],
                row["Width"],
                )
            ).iloc[0]["Path"]

            cmpChargePath = rreplace(cmpPotPath, "pot", "charge", 1)

            norms = [[0,0],[0,0]]

            norms[0][0] = (np.loadtxt(inpPotPath)).mean()
            norms[0][1] = (np.loadtxt(inpPotPath)).std()

            norms[1][0] = (np.log10(np.loadtxt(inpChargePath))).mean()
            norms[1][1] = (np.log10(np.loadtxt(inpChargePath))).std()

            tmpPath = inpPotPath.split('/')[-4:]
            deviceDir = join(self.target, tmpPath[0], tmpPath[1], tmpPath[2])
            os.mkdirs(deviceDir)

            np.savetxt(join(self.target, deviceDir, inpPotPath.split('/')[-1]), (np.loadtxt(inpPotPath) - norms[0][0]) / (norms[0][1]))
            tmpList.append(join(self.target, tmpPath[0], tmpPath[1], tmpPath[2], tmpPath[3]))

            tmpPath = inpChargePath.split('/')[-4:]
            np.savetxt(join(self.target, deviceDir, inpChargePath.split('/')[-1]), (np.log10(np.loadtxt(inpChargePath)) - norms[0][0]) / (norms[0][1]))
            tmpList.append(join(self.target, tmpPath[0], tmpPath[1], tmpPath[2], tmpPath[3]))

            tmpPath = cmpPotPath.split('/')[-4:]
            np.savetxt(join(self.target, tmpPath[0], tmpPath[1], tmpPath[2], tmpPath[3]), (np.loadtxt(cmpPotPath) - norms[0][0]) / (norms[0][1]))
            tmpList.append(join(self.target, tmpPath[0], tmpPath[1], tmpPath[2], tmpPath[3]))

            tmpPath = cmpChargePath.split('/')[-4:]
            np.savetxt(join(self.target, tmpPath[0], tmpPath[1], tmpPath[2], tmpPath[3]), (np.log10(np.loadtxt(cmpChargePath)) - norms[0][0]) / (norms[0][1]))
            tmpList.append(join(self.target, tmpPath[0], tmpPath[1], tmpPath[2], tmpPath[3]))

            tmpPath = tarPotPath.split('/')[-4:]
            np.savetxt(join(self.target, tmpPath[0], tmpPath[1], tmpPath[2], tmpPath[3]), (np.loadtxt(tarPotPath) - norms[0][0]) / (norms[0][1]))
            tmpList.append(join(self.target, tmpPath[0], tmpPath[1], tmpPath[2], tmpPath[3]))

            tmpPath = tarChargePath.split('/')[-4:]
            np.savetxt(join(self.target, tmpPath[0], tmpPath[1], tmpPath[2], tmpPath[3]), (np.log10(np.loadtxt(tarChargePath)) - norms[0][0]) / (norms[0][1]))
            tmpList.append(join(self.target, tmpPath[0], tmpPath[1], tmpPath[2], tmpPath[3]))
            
            tmpList.append(norms[0][0])
            tmpList.append(norms[0][1])
            tmpList.append(norms[1][0])
            tmpList.append(norms[1][1])

            dataList.append(tmpList)

        self.df_cond = pd.DataFrame(dataList, columns=[
        "Plane",
        "VG",
        "VD",
        "Location",
        "Criteria",
        "Height",
        "Width",
        "inpPotPath",
        "inpChargePath",
        "cmpPotPath",
        "cmpChargePath",
        "tarPotPath",
        "tarChargePath",
        "Pot Mean",
        "Pot STD",
        "Charge Mean",
        "Charge STD",
    ],)


a1 = Aggregator(args)
a1.read()
a1.save("dataframe.csv")
a1.condition()
a1.save("dataframe_conditioned.csv", 1)