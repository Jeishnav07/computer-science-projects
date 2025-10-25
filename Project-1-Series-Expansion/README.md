Project: Series Expansion Experiment

Project Description: An interactive Python program that computes and compares the Maclaurin & Taylor series for an input function displaying the graphs and simple error metrics.

Highlights:
  -User enters a function e.g.sin(x) 
  -User chooses the number of terms and expansion centre for the approximation series
  -A plot is computed and displayed with 3 graphs: the maclaurin series, taylor series and actual function in different colours
  -Simple error metrics are also displayed such as the max absolute error and mean squared error

How to run:
```bash
# 1. create and activate a virtual environment (optional but recommended)
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS / Linux:
# source .venv/bin/activate

# 2. install dependencies
pip install -r requirements.txt

# 3. run the app
python main.py
