#This file is used to store the configuration values for the project


#Range and number of points for x values needed in plotting/error calculations
min_x = -1.0
max_x = 1.0
num_x_points = 500

#Directories for saving plots and data
plots_directory = "plots"
data_directory = "data"

#Maximum number of terms the series expansion can go up to
max_num_terms = 20

#Normal number of terms to use in default calculations
default_num_terms = 5

#Dictionary to store colours for the different graphs drawn
graph_colours = {
    "actual": "#1f77b4",        #blue
    "maclaurin": "#ff0e0e",    #red
    "taylor": "#2ca02c",       #green
    "grid": "#d3d3d3"          #light grey
}
