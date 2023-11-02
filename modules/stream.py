# Import Libraries 
from app import app
from flask import render_template

# Define route "/file/".
@app.route('/file/')
def file():
  # Renders a HTML file. (For web page streaming.)
  return render_template('simple.html')

# Define route "/file/index/".
@app.route('/file/index/')
def file_index():
  # Renders a HTML file. (For web page streaming.)
  return render_template('index.html')
