<p align="center">
  <img src="pyvan.png">
</p>

<p align="center">
  <h4> Make runnable desktop/cmd apps from your python scripts!</h4>
</p>


[![Downloads](https://pepy.tech/badge/pyvan)](https://pepy.tech/project/pyvan)


### Install
```
pip install pyvan
```
### Usage

Make a "van.py" file next to the "main.py" file (entry point of your program) 

Paste the code bellow:

```
import pyvan 

OPTIONS = {"main_file_name": "main.py", 
            "show_console": False,
            "use_pipreqs": True,
            "install_only_these_modules": [],
            "exclude_modules":[],
            "include_modules":[],
            "path_to_get_pip_and_python_embeded_zip": ""
            }

pyvan.build(OPTIONS)
 
```

### Configurations

* **main_file_name**: "main.py", ==> the entry point of the application

* **show_console**: True,        ==> show console window or not (for a service or GUI app)

* **use_pipreqs**: True,         ==> pipreqs tries to minimize the size of your app by looking at your imports 
                                (best way is to use a virtualenv to ensure a smaller size, if fails will do pip freeze)

* **install_only_these_modules**: [] ==> pyvan will install only the modules mentioned here

* **exclude_modules**:[],        ==> modules to exclude from bundle 

* **include_modules**:[],        ==> modules to include in the bundle

* **path_to_get_pip_and_python_embeded_zip** ==> by default is the Download path (path to 'get-pip.py' and 'python-x.x.x-embed-amdxx.zip' files)

* **icon_location**: "TODO" ==> for now pyvan will create a .bat file which links the main_file_name with python.exe
                            in the future will add something that will convert the .bat to .exe and you will be able to set it an icon too

If pyvan didn't managed to install all the modules needed go in dist/Scripts folder and install them manually with `pip install module`


### Why pyvan?

**pyvan** it's just one file which takes the embedded python version, installs the modules you need and makes a link using a .bat file between python(w).exe and your main.py script.
<br>
It's easy if something goes wrong for whatever reason you can just go in the dist folder and solve the issue the python way (because there is just python and your scripts :).
<br>
If you want and .exe instead of a .bat file you can convert your .bat file to .exe (even put an icon) using the tools you will find online.















