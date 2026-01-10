This repository has a collection of scripts meant for processing crystal shape parameter data either from Fiji (ImageJ) or CoralNet-Toolbox.

CoralNet-Toolbox has annotations exported in a json format requiring parsing and data organization in dictionaries/ lists prior to processing and visualization.

To successfully use the suite of CoralNet-Toolbox scripts we have here, we suggest:

1. Having one project per sample.
2. Having the requisite packages installed such as: Pillow (aka PIL), cv2 (opencv-python), & json. The other packages should already be installed.
3. Making sure metadata files are available and have been created by hand.
4. Running one sample at a time. Classes may be implemented in the future to ease iteration over a directory of CoralNet-Toolbox annotations (one per project).

The Fiji (ImageJ) code was used to process and organize data previously collected in Fiji.

This code should only be used on the first set of data collected.

However, Fiji is still used to scale images processed in CoralNet-Toolbox from pixels to micrometers (see step 3).

These scripts are still being streamlined and revised, but if you would like to use them and don't know where to start please reach out to me at: jacob.tomer@uri.edu.

How to use the Fiji script:

First, define a list of paths to directories containing csvs:

''' paths = ["/Volumes/T7/SEM_image_analysis/NA165-136/","/Volumes/T7/SEM_image_analysis/NA165-139/", 
         "/Volumes/T7/SEM_image_analysis/NA165-145/", "/Volumes/T7/SEM_image_analysis/NA165-148/", 
         "/Volumes/T7/SEM_image_analysis/NA165-149/", "/Volumes/T7/SEM_image_analysis/NA165-150/", 
         "/Volumes/T7/SEM_image_analysis/NA165-153/", "/Volumes/T7/SEM_image_analysis/NA165-154/", 
         "/Volumes/T7/SEM_image_analysis/NA165-177/", "/Volumes/T7/SEM_image_analysis/NA165-178/", 
         "/Volumes/T7/SEM_image_analysis/NA165-181/", "/Volumes/T7/SEM_image_analysis/NA165-184/", 
         "/Volumes/T7/SEM_image_analysis/NA165-191/", "/Volumes/T7/SEM_image_analysis/NA165-195/"]
