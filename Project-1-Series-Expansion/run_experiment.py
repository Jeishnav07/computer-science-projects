import matplotlib.pyplot as plt #for plotting
import numpy
import math
import os       #for directory management like making the data folder
import csv      #for saving data to csv files
from series import evaluate_series_function     #returns x_grid, y_actual, y_maclaurin, y_taylor, meta
from plot_helper import plot_series_graphs      #for plotting the 3 graphs
import settings

#make sure the data and plots directories exist
os.makedirs(settings.data_directory, exist_ok=True)
os.makedirs(settings.plots_directory, exist_ok=True)

def safe_filename(function_string, centre=None, num_terms=None, prefix="series"):
    """
    Creates a safe filename for saving plots and data files
    """
    safe_func = function_string.replace('/', '_div_')
    safe_func = safe_func.replace('(', '_').replace(')', '')
    safe_func = ''.join(c if c.isalnum() or c in '._-' else '_' for c in safe_func)

    parts = [prefix, safe_func]
    if centre is not None:
        parts.append(f"centre{str(centre).replace('-', 'm').replace('.', 'p')}")
    if num_terms is not None:
        parts.append(f"terms{str(num_terms)}")

    # return base filename WITHOUT path and WITHOUT extension
    filename = "_".join(parts)
    return filename


def max_absolute_error(y_true, y_approx):
    """
    Finds the maximum absolute error between the true y values and approximate y values
    """
    difference = numpy.abs(y_true - y_approx)
    if difference.size == 0:
        return float('nan')     #to indicate if undefined
    return float(numpy.nanmax(difference))  #return the max absolute error as a float value

def mean_squared_error(y_true, y_approx):
    """
    Finds the mean squared error between the true y values and approximate y values
    """
    difference = y_true - y_approx
    mse = numpy.nanmean(difference**2)  #mean of squared differences
    if difference.size == 0:
        return float('nan')     #to indicate if undefined
    return float(mse)

def write_data_to_csv(rows, csv_path):
    """
    Writes the x values and corresponding y values to a CSV file
    along with meta information as header comments
    """
    header_lines = ["function", "approximation", "centre", "num_terms", "max_absolute_error", "mean_squared_error"]
    with open(csv_path, "w", newline='') as csvfile:            #open the file for writing
        writer = csv.DictWriter(csvfile, fieldnames=header_lines) #create the csv writer with header
        writer.writeheader()        #write the header row
        for row in rows:    
            writer.writerow(row)    #write each dictionary as a csv row

def generate_plot_for_function(function_string, rows, num_terms, centres):
    """
    Generate 2 summary plots for the given function string using 2 rows:
    - how error varies with num_terms in the polynomial approximation
    - how error varies with the expansion centre with a fixed num_terms
    """
    safe_function = safe_filename(function_string)
    function_rows = [row for row in rows if row["function"] == function_string] #filter the rows for this specific function

    #-----Plot 1: Error varying with num_terms-----#
    plt.figure(figsize=(8, 4))
    for centre in centres:
        #select the rows for each approximation with this centre and sort by num_terms
        maclaurin = sorted([row for row in function_rows if row["approximation"] == "maclaurin" and row["centre"] == centre], key=lambda x: x["num_terms"])
        taylor = sorted([row for row in function_rows if row["approximation"] == "taylor" and row["centre"] == centre], key=lambda x: x["num_terms"])

        #if list is not empty then plot a graph of num_terms vs error for MACLAURIN SERIES
        if maclaurin:   
            num_terms_maclaurin = [int(row["num_terms"]) for row in maclaurin]
            num_errors_maclaurin = [float(row["max_absolute_error"]) for row in maclaurin]
            plt.plot(num_terms_maclaurin, num_errors_maclaurin, marker='o', linestyle='--', label=f"Maclaurin (centre={centre})")
        #if list is not empty then plot a graph of num_terms vs error for TAYLOR SERIES
        if taylor:  
            num_terms_taylor = [int(row["num_terms"]) for row in taylor]
            num_errors_taylor = [float(row["max_absolute_error"]) for row in taylor]
            plt.plot(num_terms_taylor, num_errors_taylor, marker='x', linestyle='-.', label=f"Taylor (centre={centre})")

    plt.yscale('log')   #log scale for y-axis to better see error trends
    plt.xlabel("Number of Terms in Polynomial Approximation")
    plt.ylabel("Maximum Absolute Error (log scale)")
    plt.title(f"Error vs Number of Terms for {function_string}")
    plt.grid(True, linestyle=':', linewidth=0.7)
    plt.legend(loc='upper right', fontsize='small')
    plt.tight_layout()
    out1 = os.path.join(settings.plots_directory, f"{safe_function}_error_vs_num_terms.png") #output filename
    plt.savefig(out1, dpi=150)
    plt.close()


    #-----Plot 2: Error varying with different expansion centres-----#
    #pick the maximum num_terms tested as reference
    chosen_num_terms = max(num_terms)
    plt.figure(figsize=(8, 4))  #create a new figure
    sorted_centres = sorted(centres)
    maclaurin_errors = []
    taylor_errors = []
    for centre in sorted_centres:
        #find the rows for this centre and chosen num_terms for each series approximation
        maclaurin_row = next((row for row in function_rows if row["approximation"] == "maclaurin" and row["centre"] == centre and row["num_terms"] == chosen_num_terms), None)
        taylor_row = next((row for row in function_rows if row["approximation"] == "taylor" and row["centre"] == centre and row["num_terms"] == chosen_num_terms), None)
        #append the errors if the rows exist
        maclaurin_errors.append(float(maclaurin_row["max_absolute_error"]) if maclaurin_row else float('nan'))
        taylor_errors.append(float(taylor_row["max_absolute_error"]) if taylor_row else float('nan'))

    #plot the error vs centres for the 2 series
    plt.plot(sorted_centres, maclaurin_errors, marker='o', linestyle='--', label=f"Maclaurin (terms={chosen_num_terms})")
    plt.plot(sorted_centres, taylor_errors, marker='x', linestyle='-.', label=f"Taylor (terms={chosen_num_terms})")

    plt.yscale('log')   #log scale for y-axis to better see error trends
    plt.xlabel("Expansion Centre")
    plt.ylabel("Maximum Absolute Error (log scale)")
    plt.title(f"Error vs Expansion Centre for {function_string} (Terms={chosen_num_terms})")
    plt.grid(True, linestyle=':', linewidth=0.7)
    plt.legend(loc='upper right', fontsize='small')
    plt.tight_layout()
    out2 = os.path.join(settings.plots_directory, f"{safe_function}_error_vs_centre.png") #output filename
    plt.savefig(out2, dpi=150)
    plt.close()

def run_experiment(functions, centres, num_terms_list, x_min=None, x_max=None, num_x_points=None):
    """
    Runs the series expansion experiment for the given functions, centres and number of terms.
    """
    if x_min is None: x_min = settings.min_x
    if x_max is None: x_max = settings.max_x
    if num_x_points is None: num_x_points = settings.num_x_points

    data_rows = []   #to store all the data rows for CSV output

    for function_string in functions:
        print(f"Running experiment for function: {function_string}")
        for centre in centres:
            for num_terms in num_terms_list:
                #evaluate the actual function and series approximations using series module function
                x_grid, y_true, y_maclaurin, y_taylor, meta = evaluate_series_function(
                    function_string,
                    centre=centre,
                    maclaurin_num_terms=num_terms,
                    taylor_num_terms=num_terms,
                    x_min=x_min,
                    x_max=x_max,
                    num_x_points=num_x_points
                )
                #compute the errors for maclaurin and taylor series
                maclaurin_max_error = max_absolute_error(y_true, y_maclaurin)
                maclaurin_mse = mean_squared_error(y_true, y_maclaurin)
                taylor_max_error = max_absolute_error(y_true, y_taylor)
                taylor_mse = mean_squared_error(y_true, y_taylor)

                #store the data rows for maclaurin series
                data_rows.append({
                    "function": function_string,
                    "approximation": "maclaurin",
                    "centre": centre,
                    "num_terms": num_terms,
                    "max_absolute_error": maclaurin_max_error,
                    "mean_squared_error": maclaurin_mse
                })

                #store the data rows for taylor series
                data_rows.append({
                    "function": function_string,
                    "approximation": "taylor",
                    "centre": centre,
                    "num_terms": num_terms,
                    "max_absolute_error": taylor_max_error,
                    "mean_squared_error": taylor_mse
                })

                print(f"  Centre: {centre}, Terms: {num_terms} -> Maclaurin Max Error: {maclaurin_max_error:.3e}, Taylor Max Error: {taylor_max_error:.3e}")

        #generate summary plots for this function
        generate_plot_for_function(function_string, [row for row in data_rows if row["function"] == function_string], num_terms_list, centres)

    #write the csv results file after every function has been processed
    csv_path = os.path.join(settings.data_directory, "series_experiment_results.csv")
    write_data_to_csv(data_rows, csv_path)
    print(f"Experiment data saved to: {csv_path}")





#to test this script directly
if __name__ == "__main__":
    #define the functions, centres and number of terms to test
    test_functions = ["sin(x)", "cos(x)", "exp(x)", "ln(1 + x)"]
    test_centres = [0.0, 0.5, 1.0]
    test_num_terms_list = [1, 2, 3, 5, 10, 15]

    #run the experiment
    run_experiment(test_functions, test_centres, test_num_terms_list, x_min=settings.min_x, x_max=settings.max_x, num_x_points=settings.num_x_points)
