#CSD

import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import math

data = pd.read_csv("/Volumes/NA171-DE/CoralNet/CSDs/Final_CSD_data.csv")
sample_list = list(np.unique(data["Sample"]))
print(sample_list)

#print(sample_list)
data.set_index('Sample')

dict = [{"Major": []} for _ in range(len(sample_list))]

j = 0
for sample in sample_list:
    for i in range(len(data["Major"])):
        if data["Sample"][i] == sample and data["Label"][i] == "Pyroxene":
            dict[j]["Major"].append(data["Major"][i])
    
    j = j + 1
            
coefficients = {}
x_range = {}
for i in range(len(dict)):
    hist, bin_edges = np.histogram(dict[i]["Major"], 30)

    x = []
    x_outliers = []
    for j in range(len(bin_edges)):
        try:
            if hist[j] > 5:
                x.append((bin_edges[j] + bin_edges[j+1])/2)
            else:
                x_outliers.append((bin_edges[j] + bin_edges[j+1])/2)
        except Exception as err:
            print(err)

    y = []
    y_outliers = []
    for count in hist:
        if count > 5:
            y.append(np.log(count))
        else:
            y_outliers.append(np.log(count))

    if len(x) > 2:
        tmp = np.polyfit(x,y,1)
        coefficients[sample_list[i]] = tmp

    
        x_range[sample_list[i]] = np.linspace(min(x), max(x), 20)
    
    else:
        pass

    plt.scatter(x,y)
    plt.scatter(x_outliers, y_outliers, marker = "^", color = "black")
    plt.title("{}".format(sample_list[i]))
    plt.show()


for sample in sample_list:

    try:
        slope = coefficients[sample][0]
        intercept = coefficients[sample][1]
        x = x_range[sample]

        plt.plot(x, slope*x + intercept, label = sample)
    except Exception as err:
        print(err)

plt.show()

