# pyvan [![Downloads](https://pepy.tech/badge/pyvan)](https://pepy.tech/project/pyvan)
#### Make runnable desktop apps from your python scripts more easily with pyvan!

<br>

### Install
```
pip install pyvan
```
### Usage

Make a "van.py" file next to the "main.py" file (entry point of your program) 
<br>
Paste the code bellow:

```
import pyvan 

try:
    pyvan.build({"main_file_name": "main.py", 
                "show_console": False,
                "use_pipreqs": True,
                "exclude_modules":[],
                "include_modules":[],
                "get_pip_location": "https://bootstrap.pypa.io/get-pip.py",
                "embeded_python_location": "https://www.python.org/ftp/python/3.7.3/python-3.7.3-embed-amd64.zip",   
            })
except Exception as err:
    pyvan.show_traceback(err)
    input("\nPress enter to exit..")
 
```

### Configurations

* "main_file_name": "main.py", ==> the entry point of the application

* "show_console": True,        ==> show console window or not (for a service or GUI app)

* "use_pipreqs": True,         ==> pipreqs tries to minimize the size of your app by looking at your imports 
                                (best way is to use a virtualenv to ensure a smaller size)

* "exclude_modules":[],        ==> modules to exclude from bundle 

* "include_modules":[],        ==> modules to include in the bundle

* "get_pip_location": "https://bootstrap.pypa.io/get-pip.py", ==> put the url, once the file is downloaded, pyvan will use the that downloaded file

* "embeded_python_location": "https://www.python.org/ftp/python/3.7.3/python-3.7.3-embed-amd64.zip",  ==> put the url, once the file is downloaded, pyvan will use that downloaded file

* "icon_location": "TODO" ==> for now pyvan will create a .bat file which links the main_file_name with python.exe
                            in the future will add something that will convert the .bat to .exe and you will be able to set it an icon too


### Why pyvan?

I used pyinstaller a lot.. but, many times, I got lots of issues.. 
<br>
**pyvan** it's just one file which takes the embedded python version, installs the modules you need and makes a link using a .bat file between python(w).exe and your main.py script.
<br>
It's easy if something goes wrong for whatever reason you can just go in the dist folder and solve the issue the python way (because there is just python and your scripts :).
<br>
If you want and .exe instead of a .bat file you can convert your .bat file to .exe (even put an icon) using the tools you will find online.

















