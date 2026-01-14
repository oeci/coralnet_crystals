***
## Introduction
***

### The code and readme in this repository are a work in progress.

This repository has a collection of scripts meant for processing crystal shape parameter data either from Fiji (ImageJ) or CoralNet-Toolbox.

CoralNet-Toolbox has annotations exported in a json format requiring parsing and data organization in dictionaries/ lists prior to processing and visualization.

To successfully use the suite of CoralNet-Toolbox scripts we have here, we suggest:

1. Having one project per sample.
2. Having the requisite packages installed such as: Pillow (aka PIL), cv2 (opencv-python), & json. The other packages should already be installed.
3. Making sure metadata files are available and have been created by hand.
4. Running one sample at a time. Classes may be implemented in the future to ease iteration over a directory of CoralNet-Toolbox annotations (one per project).

***
## Fiji Image Processing Workflow
***

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

To visualize crystallinity data as a bar chart, call this method and input the crystallinity:

```
CrystalVisualization.plot_crystallinity(crystallinity_136, "Crystallinity NA165-136")
```
This code is challenging to implement and use for Fiji crystal counts due to its detailed workflow, and could break for unexpected reasons. The CoralNet-Toolbox scripts are more generalized and, therefore, easier to use. It is recommended that any future annotations be made in CoralNet-Toolbox.
***
## CoralNet-Toolbox Annotation Processing Workflow
***
To create metadata files containing image size and scale for each image it is recommended that you run the Fiji macro listed below to create the intial spreadsheet. The rest must be done by hand in excel, but since all images for one sample are the same size you will only need to find the scale for one image and apply it to all image sizes in the spreadsheet.

```
// Choose a folder
dir = getDirectory("/Users/jrtomer/Documents/SURFO/Batch4/NA165-191(2)/Crystals/");
list = getFileList(dir);

// Clear Results
run("Clear Results");

for (i = 0; i < list.length; i++) {

    path = dir + list[i];

    // Skip directories
    if (File.isDirectory(path)) {
        continue;
    }

    // Try opening image (some files may not be images)
    open(path);

    // Get width, height, depth
    w = getWidth();
    h = getHeight();
    d = bitDepth();

    // Add to Results table
    setResult("Filename", i, list[i]);
    setResult("Width",    i, w);
    setResult("Height",   i, h);
    setResult("BitDepth", i, d);

    // Close image
    close();
}

// Show results
updateResults();
```

The CoralNet-Toolbox scripts follow a simple order. Crystallinity -> CSDs.

It is recommended that you run crystallinity first then export the organized data using this code block not included in the script here:

```
for area in area_list:
    area_scaled.append(area/(scale**2))

coralnet_export = []
for maj, mino, area, lab, image in zip(lengths, minor, area_scaled, label_list, image_path):
    coralnet_export.append({
        "Sample": image[27:36],
        "Image": image[49:68],
        "Major": maj,
        "Minor": mino,
        "Area": area,
        "Label": lab
        })


tmp_df = pd.DataFrame(coralnet_export)
tmp_df.to_csv("/Volumes/NA171-DE/CoralNet/Processing/191_data.csv", index = False)
```

It is important to note that based off of your directory path that the index for the sample name and image number will change. Adjust these accordingly.

It will export the dataframe to a csv and this should be added to the "master" csv not included in this repository. If you would like it please send me an email at jacob.tomer@uri.edu.





