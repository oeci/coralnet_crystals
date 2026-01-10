## Fiji Crystal Script ##

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#######################

#Requires a very specific directory set up and file naming scheme.
#Uses Area and Shape Parameter data outputted by labeled images from ImageJ.

#Directory set up:

#Working directory (any name will do).
    #NA165-XXX, where X is the sample number and NA165 is the cruise
        #Crystals
            #Pyroxene
            #Olivine
            #Feldspar
#csvs also have naming requirements e.g., Image1_SP_results or Image1_crystallinity_results
#The image names are indexed and determine whether a SP is present. If so, it fits it into a SP data structure.

#The classes for reading csvs and visualizing data are below

#######################

class FileReader:
    
    def __init__(self, path):
        #Define a path to NA165-XXX from the working directory
        self.path = path

    def csv_list(self):
        
        mineral_types = ["Olivine", "Pyroxene", "Feldspar"] #List containing different file names
        tmp_list = [[] for _ in range(len(mineral_types))] #Three empty lists that will be used to store csv names

        #The list mineral types is used and joined to the path ending in NA165-XXX/ to open csvs in the files Olivine, Pyroxene and Feldspar
        self.full_paths = {mineral: os.path.join(self.path, f"Crystals/{mineral}/") for mineral in mineral_types} 

        #Adding csvs name in each of the three directories to tmp_list
        for i, (mineral, full_path) in enumerate(self.full_paths.items()):
            if os.path.exists(full_path):  # Make sure that the path exists
                tmp_list[i] = [f for f in os.listdir(full_path) if f.endswith('.csv')]

        print("Returning csv filename lists in this order: Olivine, Pyroxene, Feldspar")
        return tmp_list

    def read_csvs(self, lists):

        #Beginning to make the data structure

        #Example: mineral_data["Olivine"] would return Olivine's shape parameters and crystallinity values
        mineral_data = {mineral: {"SP": [], "crys": []} for mineral in ["Olivine", "Pyroxene", "Feldspar"]}

        for i, file_list in enumerate(lists):
            mineral = list(self.full_paths.keys())[i]
            for filename in file_list:
                file_path = os.path.join(self.full_paths[mineral], filename)
                
                try:
                    df = pd.read_csv(file_path)

                    if "SP" in filename:
                        mineral_data[mineral]["SP"].append(df)
                    else:
                        mineral_data[mineral]["crys"].append(df)
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")

        return mineral_data
    
    def combine_csvs(self, csv_dict):
        combined_data = {}
        for mineral, data_types in csv_dict.items():
            combined_data[mineral] = {
                key: pd.concat(data_list, ignore_index=True) if data_list else None for key, data_list in data_types.items()
            }

        return combined_data





class CrystalAnalysis:
    def __init__(self, metadata_path, pyroxene_df, olivine_df, feldspar_df):
        self.metadata = pd.read_csv(metadata_path)
        self.pyroxene_df = pyroxene_df
        self.olivine_df = olivine_df
        self.feldspar_df = feldspar_df
        
        self.total_image_size = self.calculate_total_image_size()
        print(self.total_image_size)

    def calculate_total_image_size(self):
        
        image_size = []
        for size, ves in zip(self.metadata["Size"], self.metadata["Vesicularity"]):
            if ves != 0:
                image_size.append(size-(size*ves))
            else:
                image_size.append(size)
        

        return sum(image_size)

    def calculate_crystallinity(self):
        percent_pyroxene = (sum(self.pyroxene_df["Area"]) / self.total_image_size) * 100 if self.pyroxene_df is not None else 0
        percent_olivine = (sum(self.olivine_df["Area"]) / self.total_image_size) * 100 if self.olivine_df is not None else 0
        percent_feldspar = (sum(self.feldspar_df["Area"]) / self.total_image_size) * 100 if self.feldspar_df is not None else 0

        return {
            "Pyroxene": percent_pyroxene,
            "Olivine": percent_olivine,
            "Feldspar": percent_feldspar,
            "Total Crystallinity": percent_pyroxene + percent_olivine + percent_feldspar
        }

    def verbose(self):

        #A debugging method
        
        print(self.pyroxene_df["Area"])
        print(self.feldspar_df["Area"])
        print(self.olivine_df["Area"])

        print(self.total_image_size)

class CrystalVisualization:
    @staticmethod
    def plot_crystallinity(crystallinity_data, title):
        labels = ["Olivine", "Pyroxene", "Feldspar", "Total Crystallinity"]
        values = [crystallinity_data[label] for label in labels]

        plt.bar(labels, values, color=["green", "brown", "black", "gray"], edgecolor="black")
        plt.ylabel("Percentage (%)")
        plt.title(title)
        plt.show()

    @staticmethod
    def plot_SPs(SP_data, sample):

        for key in SP_data.keys():
            if SP_data[key]["SP"] is not None:
                plt.title(f"{sample} {key}")
                plt.scatter(SP_data[key]["SP"]["Major"], SP_data[key]["SP"]["Minor"], label='Data')
                plt.xlabel("Major axis")
                plt.ylabel("Minor axis")
        
                major = SP_data[key]["SP"]["Major"]
                plt.plot(major, 0.2 * major, linestyle='--', color='black', label='AR = 0.2')
                plt.plot(major, 0.5 * major, linestyle='--', color='darkgray', label='AR = 0.5')
                plt.plot(major, 1.0 * major, linestyle='--', color='gray', label='AR = 1')
                plt.plot(major, 1.5 * major, linestyle='--', color='lightgray', label='AR = 1.5')
        
                plt.legend()
                plt.grid(True)
                plt.show()
            else:
                print(f"NoneType detected for {key} in {sample}")

class CSD:

    def __init__(self, SP_data, sample):
        self.SPs = SP_data
        self.sample = sample

    def number_density(self):
        sizes = {}
        areas = {}
        
        for key in self.SPs[self.sample].keys():
            if self.SPs[self.sample][key]["SP"] is not None:
                sizes[key] = self.SPs[self.sample][key]["SP"]["Major"]
                areas[key] = self.SPs[self.sample][key]["SP"]["Area"]

        self.sizes = sizes
        self.areas = areas
        
    def plot_number_density(self, bins):

        self.linebestfit = {}

        for key, sizes in self.sizes.items():
            if len(sizes) == 0:
                continue  # skip empty datasets

            # Histogram
            bin_edges = np.linspace(0, max(sizes), bins)
            hist, edges = np.histogram(sizes, bins=bin_edges)
            bin_centers = (edges[:-1] + edges[1:]) / 2

            # Log transform, replace -inf/nan with 0
            n_log = np.log(hist)
            
            n_log = np.where(np.isfinite(n_log), n_log, 0)

            # Filter out zero entries
            mask = n_log != 0
            bin_centers_filtered = bin_centers[mask]
            n_log_filtered = n_log[mask]

            print(n_log)
            
            if len(bin_centers_filtered) < 2:
                continue  # not enough points to fit

            # Linear regression (no int() here!)
            m, b = np.polyfit(bin_centers_filtered, n_log_filtered, 1)
            y_fit = m * bin_centers_filtered + b

            # Plot
            plt.figure(figsize=(5,4))
            plt.scatter(bin_centers_filtered, n_log_filtered, s=8, label="Data")
            plt.plot(bin_centers_filtered, y_fit, color="red", label="Fit")
            plt.xlabel("Size (µm)")
            plt.ylabel("Ln(n)")
            plt.title(f"CSD {self.sample} - {key}")
            plt.legend()
            plt.tight_layout()
            plt.savefig(f"/Volumes/NA171-DE/Vailulu'u/Crystals/SEM_Image_analysis/Figures/CSD_{self.sample}_{key}.png", dpi=300)
            plt.close()  # close the figure so it doesn’t overlap on the next loop

            # Save results
            self.linebestfit[key] = (m, b, y_fit)

        # Store in overall dictionary
        return(self.linebestfit)
    


    def total_number_density(self, sample_list):

        self.tmpsizes = {"Olivine": [], "Pyroxene": [], "Feldspar": []}
        self.tmpareas = {"Olivine": [], "Pyroxene": [], "Feldspar": []}

        self.totalsizes = {}
        self.totalareas = {}
        
        for sample in sample_list:
            for key in self.SPs[sample].keys():
                if self.SPs[sample][key]["SP"] is not None:
                    
                    size_val = np.array(self.SPs[sample][key]["SP"]["Major"])
                    area_val = np.array(self.SPs[sample][key]["SP"]["Area"])

                    # initialize list if first time for this key
                    self.tmpsizes[key].append(size_val)
                    self.tmpareas[key].append(area_val)
        for key in self.tmpsizes.keys():
            self.totalsizes[key] = np.concatenate(self.tmpsizes[key])
            self.totalareas[key] = np.concatenate(self.tmpareas[key])
    def plot_total_number_density(self, bins, sample_list, linetotal):
        total = {}
        for key in self.totalsizes.keys():
            bin_edges = np.linspace(0, max(self.totalsizes[key]), bins)
            hist, edges = np.histogram(self.totalsizes[key], bins = bin_edges)
            bin_center = []
            for i in range(len(edges)):
                try:
                    bin_center.append((edges[i] + edges[i+1])/2)
            
                except:
                    pass
            bin_center = np.array(bin_center)
            n_log = np.log(hist, where=(hist > 0))
            n_log = np.where(np.isfinite(n_log), n_log, 0)

            # Filter out zero entries
            mask = n_log != 0
            bin_center_filtered = bin_center[mask]
            n_log_filtered = n_log[mask]

            m, b = np.polyfit(bin_center_filtered, n_log_filtered, 1)
            y_fit = m*bin_center_filtered + b
            
            plt.scatter(bin_center_filtered, n_log_filtered, s = 2)
            plt.plot(bin_center_filtered, y_fit, color = "red")
            plt.xlabel("Size (um)")
            plt.ylabel("Ln(n)")
            plt.title("CSD {}".format(key))
            plt.legend()
            plt.savefig("/Volumes/NA171-DE/Vailulu'u/Crystals/SEM_Image_analysis/Figures/CSD{}".format(key), dpi=300)
            plt.show()

            plt.hist(self.totalareas[key], bins = 40, edgecolor = "black")
            plt.xlabel("Area (um^2)")
            plt.ylabel("Frequency")
            plt.title("Area Histogram - {}".format(key))
            plt.savefig("/Volumes/NA171-DE/Vailulu'u/Crystals/SEM_Image_analysis/Figures/area_histogram{}".format(key), dpi=300)
            plt.show()
            
            total[key] = (m,b,y_fit)
        return(total)
    


