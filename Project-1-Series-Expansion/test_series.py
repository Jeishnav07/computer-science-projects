from series import evaluate_series_function
from plot_helper import plot_series_graphs
from parser_function import sanitize_input_function
import settings

def run_series_test():
    """
    Run two example runs:
    - maclaurin series for exp(x)
    - taylor series for exp(x) centred at x=1
    - num_terms = 5 for both
    Save the plots for both to the plots/ directory
    """
    #set function to test
    function_string = "exp(x)"

    #evaluate and plot maclaurin series
    x, y_true, y_maclaurin, y_taylor, meta = evaluate_series_function(function_string, centre=0.0, maclaurin_num_terms=5, taylor_num_terms=5)
    file1 = plot_series_graphs(x, y_true, y_maclaurin, y_taylor, meta)
    print(f"Maclaurin series plot saved to: {file1}")

    #evaluate and plot taylor series
    x, y_true, y_maclaurin, y_taylor, meta = evaluate_series_function(function_string, centre=1.0, maclaurin_num_terms=5, taylor_num_terms=5)
    file2 = plot_series_graphs(x, y_true, y_maclaurin, y_taylor, meta)
    print(f"Taylor series plot saved to: {file2}")

if __name__ == "__main__":
    run_series_test()
   