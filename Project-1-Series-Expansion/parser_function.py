from sympy import sympify, symbols, lambdify    #import the symplify parser and other sympy functions
import numpy  #import numpy for numeric arrays
import re     #import regular expressions to help sanitize input functions

x = symbols("x")

def sanitize_input_function(function_string):
    """
    Sanitizes the input function string to ensure it only contains allowed characters:
    - strips any whitespace
    - replace exponential symbol from ^ to **
    This is not a full-proof sanitization, but helps reduce common input errors.
    """
    string = function_string.strip() 
    string = string.replace("^", "**")
    return string

def parser_to_sympy(function_string):
    """
    Parses the sanitized input function string to a sympy expression.
    Returns a sympy expression object.
    """
    string = sanitize_input_function(function_string)
    expression = sympify(string)
    return expression
    
def make_function_numpy_callable(expression):
    """
    Converts a sympy expression into a numpy-callable function.
    Lambdify produces a function that accepts numpy arrays as input for efficient computation.
    Returns this numpy-callable function.
    """
    numpy_function = lambdify(x, expression, "numpy")
    return numpy_function
    
def parse_function_to_numpy_callable(function_string):
    """
    Combines parsing and conversion to produce a numpy-callable function from an input string.
    Returns (expression, numpy_function) where expression is the sympy expression and numpy_function is the numpy-callable function.
    """
    expression = parser_to_sympy(function_string)
    numpy_function = make_function_numpy_callable(expression)
    return expression, numpy_function

def is_function_valid(function_string, x_values):
    """
    Validates the input function string to ensure it only uses allowed functions.
    Returns True if valid, False otherwise.
    """
    expression, function = parse_function_to_numpy_callable(function_string)

    with numpy.errstate(all="ignore"):
        y = numpy.array(function(x_values), dtype=float)
    return expression, y