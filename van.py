import pyvan 

"""
==================================
pyvan.build parameters described
==================================

"main_file_name": "main.py", ==> the entry point of the application

"show_console": True,        ==> show console window or not

"use_pipreqs": True,         ==> pipreqs tries to minimize the size of your app by looking at your imports 
                                (best way is to use a virtualenv to ensure a smaller size)

"exclude_modules":[],        ==> modules to exclude from bundle

"include_modules":[],        ==> modules to include in the bundle

"get_pip_location": "https://bootstrap.pypa.io/get-pip.py", ==> location of the 'get_pip.py' file 
                                                                either put the url or a local path to that file


==> location of the embeded python distribution, either put the url or a local path to the embeded python zip
"embeded_python_location": "https://www.python.org/ftp/python/3.7.3/python-3.7.3-embed-amd64.zip",   

"""



try:
    pyvan.build({"main_file_name": "main.py", 
                "show_console": True,
                "use_pipreqs": True,
                "exclude_modules":[],
                "include_modules":[],
                "get_pip_location": "https://bootstrap.pypa.io/get-pip.py",
                "embeded_python_location": "https://www.python.org/ftp/python/3.7.3/python-3.7.3-embed-amd64.zip",   
            })
except Exception as err:
    pyvan.show_traceback(err)
    input("\nPress enter to exit..")

