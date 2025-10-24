from sympy import sympify, symbols, series, lambdify   
import numpy
from parser_function import sanitize_input_function     #import the sanitization function
import settings     #import settings for configuration values

x = symbols("x")

def series_expression(expression, centre, num_terms):
    """
    Given a symbolic expression, centre and order (num_terms)
    Returns a symbolic taylor/maclaurin polynomial approximation
    - uses sympy.series to compute the series expansion
    - removes the big O notation using removeO() method
    - sympy.series uses n = num_terms + 1 to include the right number of terms up to x^num_terms
    """
    series_expr = series(expression, x, centre, num_terms + 1).removeO()
    return series_expr

def series_expression_numpy_callable(expression, centre, num_terms):
    """
    Given the series polynomial expression, centre and order (num_terms)
    Return a numpy-callable function for the series expansion
    """
    series_expr = series_expression(expression, centre, num_terms)
    numpy_expr = lambdify(x, series_expr, "numpy")
    return numpy_expr

def evaluate_series_function(function_string, centre=0.0, maclaurin_num_terms=settings.default_num_terms, taylor_num_terms=settings.default_num_terms, x_min=settings.min_x, x_max=settings.max_x, num_x_points=settings.num_x_points):
    """
    This function does the following:
    - parses the input function string to a sympy expression
    - creates a numpy-callable function from the sympy expression
    - creates numpy-callable functions for the maclaurin and taylor series expansions
    - evaluates each of these on a numeric x-grid defined by x_min, x_max, num_x_points
    Returns: 
    - (x_grid, y_true, y_maclaurin, y_taylor, meta)
    - meta is a dictionary with information useful for reporting and plotting labels
    If configurations like num_terms are not input, default values from settings.py are used
    """
    #parse the function string to sympy expression and numpy-callable function
    sanitized_string = sanitize_input_function(function_string)
    expression = sympify(sanitized_string)
    numpy_function = lambdify(x, expression, "numpy")

    #prepare grid for evaluating functions
    x_grid = numpy.linspace(x_min, x_max, num_x_points)

    #create numpy-callable functions for maclaurin and taylor series
    maclaurin_function = series_expression_numpy_callable(expression, 0.0, maclaurin_num_terms) #maclaurin is always centred at 0
    taylor_function = series_expression_numpy_callable(expression, centre, taylor_num_terms)

    #evaluate the true function on the grid
    with numpy.errstate(all="ignore"):
        y_actual = numpy.array(numpy_function(x_grid), dtype=float)

    #evaluate the maclaurin series on the grid
    with numpy.errstate(all="ignore"):
        y_maclaurin = numpy.array(maclaurin_function(x_grid), dtype=float)

    #evaluate the taylor series on the grid
    with numpy.errstate(all="ignore"):
        y_taylor = numpy.array(taylor_function(x_grid), dtype=float)

    #create meta information as dictionary
    meta = {
        "function_string": function_string,
        "expression": str(expression),
        "centre": centre,
        "maclaurin_num_terms": maclaurin_num_terms,
        "taylor_num_terms": taylor_num_terms,
        "x_min": x_min,
        "x_max": x_max,
        "num_x_points": num_x_points
    }

    return x_grid, y_actual, y_maclaurin, y_taylor, meta