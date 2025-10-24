import matplotlib.pyplot as plt #for plotting
import numpy    
import os       #for directory management like making the plots folder
import settings #for the colours of each graph 

def plot_series_graphs(x, y_true, y_maclaurin, y_taylor, meta, out_filename=None):
    """
    Plots the actual function and 2 approximation graphs on a single plot
    - x is the numpy array of x values
    - y_true, y_maclaurin, y_taylor are the corresponding y values for each function
    - meta is a dictionary with keys needed for titles and labels
    - out_filename is the path to save the plot, if None the plot is not saved
    """
    #makes sure the plots directory exists
    os.makedirs(settings.plots_directory, exist_ok=True)

    #create a default filename if none is provided
    if out_filename is None:
        safe_function_str = meta.get("function_string", "function").replace('/', '_').replace('(', '_').replace(')', '')
        out_filename = os.path.join(settings.plots_directory, f"{safe_function_str}_plot.png")

    #create a matplotlib figure
    plt.figure(figsize=(7, 3))

    #plot each of the functions
    plt.plot(x, y_true, label="True", color=settings.graph_colours["actual"], linewidth=1.7)
    plt.plot(x, y_maclaurin, label="Maclaurin", color=settings.graph_colours["maclaurin"], linestyle='--')
    plt.plot(x, y_taylor, label="Taylor", color=settings.graph_colours["taylor"], linestyle='--')

    #add the grid, labels and titles
    plt.grid(color=settings.graph_colours["grid"], linestyle=':', linewidth=0.7)
    plt.xlabel(meta.get("x_label", "x"))
    plt.ylabel(meta.get("y_label", "y"))
    plt.title(meta.get("title", "Function Plot"))

    #tidy the layout so labels don't overlap
    plt.tight_layout()

    #save the plot to file
    plt.savefig(out_filename, dpi=150)

    #close the plot to free memory
    plt.close()

    #return the saved filename
    return out_filename