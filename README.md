# CoBRA_segmentor
The CoBRA_segmentor software was developed during the CoBRA project (Cow Behaviour Recording and Analysis) in order to have a desktop application for image segmentation which works completely offline and thus does not require an internet connection.

CoBRA_segmentor generates for each image a .json file containing 1) the coordinates, name and class of annotated segment vertices and 2) the coordinates of annotated mask vertices. 

CoBRA_segmentor can be run from the CoBRA_segmentor.py file, but can also be compiled to an executable file using pyinstaller in combination with the compilation parameters specified in  CoBRA_segmentor.spec


