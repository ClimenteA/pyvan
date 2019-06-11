import sys, os
if sys.executable.endswith('pythonw.exe'):
  sys.stdout = open(os.devnull, 'w')
  sys.stderr = open(os.path.join(os.getenv('TEMP'), 'stderr-{}'.format(os.path.basename(sys.argv[0]))), "w")

import sys, os
if sys.executable.endswith('pythonw.exe'):
  sys.stdout = open(os.devnull, 'w')
  sys.stderr = open(os.path.join(os.getenv('TEMP'), 'stderr-{}'.format(os.path.basename(sys.argv[0]))), "w")

import sys, os
if sys.executable.endswith('pythonw.exe'):
  sys.stdout = open(os.devnull, 'w')
  sys.stderr = open(os.path.join(os.getenv('TEMP'), 'stderr-{}'.format(os.path.basename(sys.argv[0]))), "w")

import sys, os
if sys.executable.endswith('pythonw.exe'):
  sys.stdout = open(os.devnull, 'w')
  sys.stderr = open(os.path.join(os.getenv('TEMP'), 'stderr-{}'.format(os.path.basename(sys.argv[0]))), "w")

import sys, os
if sys.executable.endswith('pythonw.exe'):
  sys.stdout = open(os.devnull, 'w')
  sys.stderr = open(os.path.join(os.getenv('TEMP'), 'stderr-{}'.format(os.path.basename(sys.argv[0]))), "w")

import sys, os
if sys.executable.endswith('pythonw.exe'):
  sys.stdout = open(os.devnull, 'w')
  sys.stderr = open(os.path.join(os.getenv('TEMP'), 'stderr-{}'.format(os.path.basename(sys.argv[0]))), "w")

from flask import Flask  
from flask import render_template
from flaskwebgui import FlaskUI

app = Flask(__name__)
ui = FlaskUI(app, browser_path=r"E:\_python_macro\SpecialistRef - find failures\SpecialistRef\SPECIALISTREF\chrome\chrome.exe", executable_name="main.exe", width=500, height=500)


@app.route("/")
def hello():  
    return render_template('index.html')



@app.route("/home", methods=['GET'])
def home(): 
    return "Home"



if __name__ == "__main__":
    ui.run()
   
