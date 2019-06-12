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

