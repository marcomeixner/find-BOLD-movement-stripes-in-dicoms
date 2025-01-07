This script identifies a movement artefact in BOLD images; a periodic stripe artefact is found on the basis of an FFT and the expected frequency of the stripes, coming from the slice timing 




# install on Windows:

- download python: https://www.python.org/downloads/
- install python (see screenshot install_python_windows.png)
- check Installation via the command line: python --Version
- install necessary libraries via pip: pip install matplotlib pydicom scipy numpy argparse
- download the code to a cerain folder
- go to that Directory in the command line and type: python main_gui_FFT_dcm_image_analysis.py
  -> the GUI starts (see screenshot GUI.png)



# python scripts used:

- FFT_dcm_image_analysis.py
  runs the FFT Analysis of every dicom volume in the Input Folder to identifiy horizontal stripes for a certain 'Sagittal Slices Index' with a certain 'Periodicity';
  (python libraries required: numpy, pydicom, argparse, scipy.fftpack)

- find_and_plot_outlier
  identify outlier volumes with Stripes and Show (and save) a plot
  (python libraries required: os, matplotlib, argparse, numpy)



input: 
 - Input Folder: where the dicom volumes are
 - Output Folder: where the Outputs are saved
 - Sagittal Slice Index: try to Chose an index a Little off the Center
 - Std Factor: the number of std from the mean to identify outlier volumes with stripe pattern; this determines the threshold in the Output plut

output: 
 - match_score.txt: a file with all the scores for the Chosen periodicity in the Chosen Position
 - match_score_plot.png: a plot of the scores for each volume; the outliers are marked and mentioned in the plot Headline

