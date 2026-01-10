import os
from PIL import Image, ImageDraw
import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import math
import json
import cv2
import re

class Main:

    def __init__(self, json_path, scales_path):
        #Opens JSON annotation file
        with open(json_path, 'r') as file:
            self.data = json.load(file)
        self.point_dict = {}

        #opens scales JSON file -> in format "Image_Name": number
        with open(scales_path, "r+") as f:
            self.scales_dict = json.load(f)

        self.colors = {
                "Pyroxene" : "cyan",
                "Olivine" : "dodgerblue",
                "Feldspar" : "magenta",
                "Vesicles" : "green"
        }

        #image width and height in nanometers
        self.width, self.height = 1920, 1200 #Not every image will be this size
    
        # 42 nm/px
        self.scale = 0.42969 #Not every image will be this scale

        #populates point_dict
        for key in self.data.keys():
            point_list = []
            for i in range(len(self.data[key])):        
                point_list.append((self.data[key][i]["points"], self.data[key][i]["label_short_code"], self.data[key][i]["perimeter"], self.data[key][i]["area"]))
            
            #37-46 index for sample  --> Probably fix this: not the same for every image?
            #48-54 index for image #
            img_name = os.path.basename(key)
            folder_path = os.path.dirname(key)
            match = re.search(r"NA\d+-\d+", key)
            if not match:
                print("NA is not in name of image")

            na_code = match.group()
            name_no_ext = os.path.splitext(img_name)[0]
            clean_up = re.sub(r"_processing_\d+$", "", name_no_ext)

            self.point_dict[f"{na_code}_{clean_up}"] = point_list   #key[38:47] + "_" + key[48:54]




#Making outlines from JSON
    def make_outlines(self, filesave_path):
        
        label = {'Pyroxene': 100, 'Olivine': 30, 'Feldspar': 150, 'Vesicles': 200}
        for key in self.point_dict.keys(): 
            image = Image.new("L", (self.width, self.height), color=255)  
            draw = ImageDraw.Draw(image)
            for entry in self.point_dict[key]:
                vertices = entry[0]
                polygon = [(int(x), int(y)) for x, y in vertices]
                gray = label[entry[1]]
                draw.polygon(polygon, fill=gray, outline=0)  

            image.save(os.path.join(filesave_path, f"{key}_outline.png"))

# Uses Freedman–Diaconis Rule to generate appropriate bin width
    def generate_bins(self, data):
        n = len(data)
        q75, q25 = np.percentile(data, [75, 25])
        IQR = q75 - q25
        return 2*(IQR/(n**(1/3)))


#Creating Area Histogram - One image with 3 separate histograms for each crystal
    def make_area_hist(self, filesave_path):
        
        for key in self.point_dict.keys():

            areas_by_label = {
                "Pyroxene" : [],
                "Olivine" : [],
                "Feldspar" : [],
                "Vesicles" : []
            }

            #dictionary with each crystal having list of areas from image
            for entry in self.point_dict[key]:
                label = entry[1]
                area_px2 = entry[3]
                area_um2 = area_px2/self.scale**2
                areas_by_label[label].append(area_um2)

            
            fig, axs = plt.subplots (1, 3, figsize = (18, 5), sharey=True)

            for ax, (label, areas) in zip(axs, areas_by_label.items()):
                
                if len(areas) > 5: 
                    binwidth = min(self.generate_bins(areas), (max(areas) - min(areas)) / 10) #self.generate_bins(areas)
                    
                    bins = np.arange(min(areas), max(areas) + binwidth, binwidth) 
                else:
                    bins = 10
                ax.hist(areas, bins = bins, color = self.colors[label])
                ax.set_title(label, fontsize=14)
                ax.set_xlabel("Area (um²)", fontsize=14)
                ax.set_ylabel("Frequency", fontsize=14)
                #ax.grid(True)

            fig.suptitle(f"Area Distribution by Crystal - {key}", fontsize=20)

            plt.savefig(os.path.join(filesave_path, f"{key}_area_graph.png"))



#Creating Perimeter Histogram - One image with 3 separate histograms for each crystal
    def make_perimeter_hist(self, filesave_path):
        for key in self.point_dict.keys():

            perimeters_by_label = {
                "Pyroxene" : [],
                "Olivine" : [],
                "Feldspar" : [],
                "Vesicles" : []
            }

            #dictionary with each crystal having list of perimeters from image
            for entry in self.point_dict[key]:
                label = entry[1]
                perimeter_px = entry[2]
                perimeter_um = perimeter_px/self.scale
                perimeters_by_label[label].append(perimeter_um)
            
            fig, axs = plt.subplots (1, 3, figsize = (18, 5), sharey=True)

            for ax, (label, perimeters) in zip(axs, perimeters_by_label.items()):
                ax.hist(perimeters, bins = 25, color = self.colors[label])
                ax.set_title(label, fontsize=14)
                ax.set_xlabel("Perimeter (um)", fontsize=14)
                
                ax.set_ylabel("Frequency", fontsize=14)
                #ax.grid(True)

            fig.suptitle(f"Perimeter Distribution by Crystal - {key}", fontsize=20)

            plt.savefig(os.path.join(filesave_path, f"{key}_perimeter_graph.png"))


#fitting ellipses around annotations
#Open cv limitation >5 points to make an ellipse. section in graph that say able to ellipse XX/XX total annotations
    def make_ellipse_scatter(self, filesave_path):
        for key in self.point_dict.keys():

            ellipses_by_label = {
                "Olivine" : {
                    "major_axis_list": [],
                    "minor_axis_list": []
                }, 
                "Feldspar": {
                    "major_axis_list": [],
                    "minor_axis_list": []
                },
                "Pyroxene": {
                    "major_axis_list": [],
                    "minor_axis_list": []
                }, 
                "Vesicles": {
                    "major_axis_list": [],
                    "minor_axis_list": []
                },
            }
            

            for entry in self.point_dict[key]:
                pts = np.array (entry[0], dtype = np.float32)

                if len(pts) >= 5:
                    ellipse = cv2.fitEllipse(pts)

                    axes= ellipse[1]
                    ellipses_by_label[entry[1]]["major_axis_list"].append(max(axes)/self.scale)
                    ellipses_by_label[entry[1]]["minor_axis_list"].append(min(axes)/self.scale)

            
            fig, axs = plt.subplots (1, 3, figsize = (18, 5), sharey=True)

            for ax, (label, axes) in zip(axs, ellipses_by_label.items()):
                ax.scatter(axes["major_axis_list"], axes["minor_axis_list"], color = self.colors[label])
                ax.set_title(label, fontsize=14)
                ax.set_xlabel("Major Axis (um)", fontsize=14)
                ax.set_ylabel("Minor Axis (um)", fontsize=14)
                #ax.grid(True)

                slopes = [0.2, 0.4, 0.8, 1.0, 1.5, 2]
                x_min, x_max = ax.get_xlim()
                x_vals = np.linspace(x_min, x_max, 100)

                for slope in slopes:
                    y_vals = slope * x_vals
                    ax.plot(x_vals, y_vals, linestyle='--', linewidth=1, label=f"AR = {slope}")
                ax.legend()
                


            fig.suptitle(f"AR - {key}", fontsize=20)

            plt.savefig(os.path.join(filesave_path, f"{key}_axes_graph.png"))


    #calculates the crystal area fraction
    def get_crystal_area_percent(self):
        image_area = self.width * self.height
        
        crystal_areas_dict = {}

        for key in self.point_dict.keys():
            crystal_areas = {
                "Pyroxene" : 0,
                "Olivine" : 0,
                "Feldspar" : 0,
                "Vesicles" : 0,
                "Total Crystal Area": 0
            }
            for entry in self.point_dict[key]:
                crystal_areas[entry[1]] += (entry[3]/image_area)*100

            crystal_areas["Total Crystal Area"] += crystal_areas["Pyroxene"] + crystal_areas["Olivine"] + crystal_areas["Feldspar"] #+ crystal_areas["Vesicles"], we don't want vesicles in this instance

            crystal_areas_dict[key] = crystal_areas



        return crystal_areas_dict

        

    #returns a dictionary with image name as key and corresponding dictionary of crystal:counts as value
    def get_crystal_counts(self):
        crystal_count_dict = {}

        for key in self.point_dict.keys():
            crystal_counts = {
                "Pyroxene" : 0,
                "Olivine" : 0,
                "Feldspar" : 0,
                "Vesicles" : 0
            }
            for entry in self.point_dict[key]:
                crystal_counts[entry[1]] += 1
            
            crystal_count_dict[key] = crystal_counts

        return crystal_count_dict
    

            

test = Main("C:/Users/madis/CoralNet_Project/Ahyi_1/NA171-049_Stitched_Image_Annotations.json", "C:/Users/madis/crystal_processing/scales.json")
#print(test.get_crystal_area_percent())
#test.make_area_hist("C:/Users/madis/image_outlines")
#test.make_perimeter_hist("C:/Users/madis/image_outlines")
#test.make_ellipse_scatter("C:/Users/madis/image_outlines")
# test.make_outlines("C:/Users/madis/image_outlines")


#FIX Histogram bins!!!!!