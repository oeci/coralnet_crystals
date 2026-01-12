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

```
paths = ["/Volumes/T7/SEM_image_analysis/NA165-136/", ..., "/Volumes/T7/SEM_image_analysis/NA165-195/"]
```
Next, iterate over paths list and call the first few methods in class FileReader. Note: see comments in script to understand required directory layout.

```
final_df = {}
ind_df = {}
for path in paths:
    reader = FileReader(path)
    file_lists = reader.csv_list()
    raw_data = reader.read_csvs(file_lists)

    sample_id = path.rstrip("/").split("-")[-1]

    ind_df[sample_id] = raw_data

    final_df[sample_id] = reader.combine_csvs(raw_data)
```
The final dataframe, or final_df, will be used in the class CrystalAnalysis to determine crystallinity

```
analysis_136 = CrystalAnalysis(
    metadata_path="/Volumes/T7/SEM_image_analysis/Crystal_Data/metadata_136.csv",
    pyroxene_df=final_df["136"]["Pyroxene"]["crys"],
    olivine_df=final_df["136"]["Olivine"]["crys"],
    feldspar_df=final_df["136"]["Feldspar"]["crys"]
)
crystallinity_136 = analysis_136.calculate_crystallinity()

```
Notice that the class requires a metadata file that is made by hand and formatted in a very specific way. Please email me if you have questions regarding it (see email above).

The line:
```
crystallinity_136 = analysis_136.calculate_crystallinity()

```

Will calculate crystallinity in percent area (um^2) for feldspar, pyroxene, and olivine with a correction for vesicularity which is included in the metadata file and is unique to each image processed.





