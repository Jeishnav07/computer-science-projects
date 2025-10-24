import numpy
import matplotlib.pyplot as plt     #for plotting
import os                           #for directory management like making the plots folder
import re                           #for sanitizing filenames

#import the parser functions to be tested (keep your original names)
from parser_function import parse_function_to_numpy_callable, is_function_valid

#makes a folder called "plots" if it doesn't already exist
os.makedirs("plots", exist_ok=True)

#Define example functions to test
test_functions = ["sin(x)", "exp(x)", "log(1+x)", "1/(1-x)"]

#Define 400 evenly spaced x values for testing and avoid exact value 1 to avoid division by zero errors
x_values = numpy.linspace(-0.99, 0.99, 400)


for function_str in test_functions:
    print(f"Testing function: {function_str}")

    #parse the function string to get sympy expression and numpy-callable function
    expression, numpy_function = parse_function_to_numpy_callable(function_str)
    print(f"Sympy Expression: {expression}")

    #validate the function and evaluate on the x grid
    expression, y_values = is_function_valid(function_str, x_values)
    #print a short sample from the start and end of the output for quick inspection
    print(f"Sample outputs (first 6): {y_values[:6]}")
    print(f"Sample outputs (last 6):  {y_values[-6:]}")

    #plot the function with improved formatting
    plt.figure(figsize=(5, 2.5))  #compact figure similar to your second script
    plt.plot(x_values, y_values, label=f"f(x) = {expression}")
    plt.title(f"Plot of {function_str}")
    plt.xlabel("x")
    plt.ylabel("f(x)")
    plt.legend(fontsize='small')
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.tight_layout()

    #produce a safe filename and save using os.path.join for portability
    safe = function_str.replace('/', '_div_')
    safe = re.sub(r'[^0-9A-Za-z._-]+', '_', safe).strip('_')
    png_path = os.path.join("plots", safe + ".png")
    plt.savefig(png_path, dpi=150)
    plt.close()

    print(f"Plot saved for function: {function_str} -> {png_path}\n")
