import os
import pandas as pd

#getting all files from all subdirectories and paths to said files
imgs = []
name_as_lst = []
VGnums = set()
VDnums = set()
target_prefix = "NEGFXY"

filenum = 0
filenames = []
for root, dirs, files in os.walk("/home/kyle/ML_NEGF/main_data_dir"):
    for name in files:
      if name.startswith(target_prefix):
        filenames.append(os.path.join(root, name))
        name = str(name).split(".txt")[0] #Removing .txt at end of strings
        name_as_lst = name.split("_")
        XY = name_as_lst.pop(0)[-2:]
        name_as_lst.insert(0,XY)
        imgs.append(name_as_lst + str(root).split("/")[-3:])


df = pd.DataFrame(imgs,columns=['Plane','VG','VD','Location',"Type","Iteration","Magnitude","Shape","Index"])
print(df.query("Shape == '3x3'"))