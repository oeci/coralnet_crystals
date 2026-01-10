## CoralNet Processing - Crystallinity ##

from PIL import Image, ImageDraw
import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import math
import json
import cv2

path = "/Users/jrtomer/Documents/SURFO/Annotations-191.json"
size_data = pd.read_csv("/Users/jrtomer/Documents/SURFO/191_size_results.csv")
image_total = size_data["Width"][0]*size_data["Height"][0]
total = image_total*10 #multiply by the total number of images

with open(path, 'r') as file:
    data = json.load(file)




label_list = []
area_list = []
point_list = []
image_path = []

for key in data.keys():
    for i in range(len(data[key])):
        if data[key][i]['type'] == "PolygonAnnotation":

            area_list.append(data[key][i]['area'])
            point_list.append(data[key][i]['points'])
            label_list.append(data[key][i]['label_short_code'])
            image_path.append(data[key][i]['image_path'])

        else:
            print(data[key][i]['type'])


dict_labels = np.unique(image_path)


dict = {}
for label in dict_labels:
    dict[label + '_area'] = []
    dict[label + '_points'] = []
    dict[label + '_label'] = []
    for i in range(len(image_path)):
        if label == image_path[i]:
            dict[label + '_area'].append(area_list[i]/(size_data['Scale']**2))
            dict[label + '_points'].append(point_list[i])
            dict[label + '_label'].append(label_list[i])


# Calculating total area #

mineral_dict = {"Feldspar": [], "Pyroxene": [], "Olivine": [], "Vesicles": []}
for label in dict_labels:
    for i in range(len(dict[label + '_area'])):
        area = dict[label + '_area'][i]
        mineral = dict[label + '_label'][i]

        mineral_dict[mineral].append(area)

for key in mineral_dict.keys():
    mineral_dict[key] = sum(mineral_dict[key])
    mineral_dict[key] = np.unique(mineral_dict[key])

    vesicles = mineral_dict["Vesicles"][0]
    

    mineral_dict[key] = (mineral_dict[key]/(total-vesicles))*100
    mineral_dict[key] = float(np.unique(mineral_dict[key]))



print(mineral_dict)

plt.bar(mineral_dict.keys(), mineral_dict.values())
plt.show()
