#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import time
import os, sys
import shutil
import zipfile
import subprocess


# In[ ]:


header_no_console = """import sys, os
if sys.executable.endswith('pythonw.exe'):
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.path.join(os.getenv(\'TEMP\'), \'stderr-{}\'.format(os.path.basename(sys.argv[0]))), "w")
    
"""


# In[ ]:


def execute_os_command(command):
    """Execute terminal command"""
    
    print("Running command: ", command)
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    # Poll process for new output until finished
    while True:
        nextline = process.stdout.readline().decode('UTF-8')
        if nextline == '' and process.poll() is not None:
            break
        sys.stdout.write(nextline)
        sys.stdout.flush()

    output = process.communicate()[0]
    exitCode = process.returncode

    if (exitCode == 0):
        print(output)
        return output
    else:
        raise Exception(command, exitCode, output)


# In[ ]:


def put_code_in_dist_folder():
    """Copy .py files and others to dist folder"""
    #Delete dist folder
    if os.path.isdir("dist"):
        shutil.rmtree('dist')
    print("Copying files..")
    shutil.copytree(os.getcwd(), os.path.join(os.getcwd(), "dist"))
    print("Files copied to dist folder!")


# In[ ]:


def prep_requirements(OPTIONS):
    """ Create requirements.txt file from which to install modules on embeded python version """
    
    if OPTIONS["use_pipreqs"]:
        print("Searching modules needed using 'pipreqs'...")
        execute_os_command("pipreqs . --force --ignore dist")
        print("Done!")
    else:
        print("Searching modules needed using 'pip freeze'...")
        execute_os_command("pip3.exe freeze > requirements.txt")
        print("Done!")


# In[ ]:


def filter_requirements(OPTIONS):
    """Filter modules and keep only the ones needed"""
    
    print("Checking which modules to exclude or to keep")
    with open('requirements.txt', 'r') as r:
        modules_to_install = r.read().splitlines()

    if OPTIONS["exclude_modules"]:
        modules_to_install = list(set.difference(set(modules_to_install), set(OPTIONS["exclude_modules"])))

    if OPTIONS["include_modules"]:
        modules_to_install = modules_to_install + OPTIONS["include_modules"]

    print("Updating 'requirements.txt' file")
    with open('requirements.txt', 'w') as f:
        f.write("\n".join(modules_to_install))

    print("File requirements.txt done!")


# In[ ]:


def add_embeded_and_pip_to_dist(GET_PIP_PATH, PYTHON_EMBEDED_PATH):
    """ Copy embeded python and get-pip file to dist folder """
    
    print(f"Extracting {PYTHON_EMBEDED_PATH} to dist folder")
    zip_ref = zipfile.ZipFile(PYTHON_EMBEDED_PATH, 'r')
    zip_ref.extractall('dist')
    zip_ref.close()
    print("Zip file extracted!")

    shutil.copy2(GET_PIP_PATH, "dist")
    print("File 'get-pip.py' file copied to dist!")


# In[ ]:


def prepare_for_pip_install(pth_file, zip_pyfile):
    """
        Prepare the extracted embeded python version for pip instalation
        - Uncommented 'import site' line from pythonXX._pth file
        - Extract pythonXX.zip zip file to pythonXX.zip folder and delete pythonXX.zip zip file
    """
    print(f"Uncommented 'import site' line from '{pth_file}' file")
    with open(pth_file, 'w') as f:
        f.write(f'{zip_pyfile}\n.\n\n# Uncomment to run site.main() automatically\nimport site\n')

    print(f"Extracting {zip_pyfile} file")

    temp_folder = str(zip_pyfile + "_temp")
    os.mkdir(temp_folder)

    zip_ref = zipfile.ZipFile(zip_pyfile, 'r')
    zip_ref.extractall(temp_folder)
    zip_ref.close()

    os.remove(zip_pyfile)

    for n in range(10):
        try:
            #Try 10 times to delete the file 
            os.rename(temp_folder, zip_pyfile)
        except: #Permision error
            time.sleep(0.3)

    print(f"Zip file extracted to {zip_pyfile} folder!")


# In[ ]:


def install_requirements():
    """Install pip and the modules from requirements.txt file"""
    
    print("Installing pip..")

    execute_os_command("python.exe get-pip.py --no-warn-script-location")

    if not os.path.isdir("Scripts"):
        raise Exception("Module 'pip' didn't install corectly from 'get-pip.py' file!")

    print("Module pip installed!")

    os.chdir("Scripts")
    print("Moved runtime to Scripts folder: ", os.getcwd())

    try:
        cmd = "pip3.exe install --no-cache-dir --no-warn-script-location -r ../requirements.txt"
        execute_os_command(cmd)
    except:
        
        print("Installing modules one by one..")
        
        with open("../requirements.txt", "r") as f:
            modules = f.read().splitlines()
        
        for module in modules:
            try:
                cmd = "pip3.exe install --no-cache-dir --no-warn-script-location " + module
                execute_os_command(cmd)
            except:
                print("FAILED TO INSTALL ", module)
                with open("FAILED_TO_INSTALL_MODULES.txt", "a") as f:
                    f.write(str(module + "\n"))


# In[ ]:


def make_startup_batch(OPTIONS):
    """ Make the startup batch files needed to run the script """
    
    print("Making startup batch files")

    mfname = OPTIONS["main_file_name"].split(".py")[0]

    if OPTIONS["show_console"]:
        with open(str(mfname + ".bat"), "w") as f:
            f.write(str("START python " + OPTIONS["main_file_name"]))
    else:
        with open(OPTIONS["main_file_name"], "r", encoding="utf8", errors="surrogateescape") as f:
            main_content = f.read()

        if header_no_console not in main_content:
            with open(OPTIONS["main_file_name"], "w", encoding="utf8", errors="surrogateescape") as f:
                f.write(str(header_no_console + main_content))

        with open(str(mfname + ".bat"), "w") as f:
            f.write(str("START pythonw " + OPTIONS["main_file_name"]))

    print("Done!")


# In[ ]:


def process_options(OPTIONS):
    
    #Get the path to python emebeded zip file and get-pip.py file
    if OPTIONS['path_to_get_pip_and_python_embeded_zip'] == "":
        FILES_PATH = os.path.join(os.getenv('USERPROFILE'), 'Downloads')
    else:
        FILES_PATH = OPTIONS['path_to_get_pip_and_python_embeded_zip']

    if 'get-pip.py' not in os.listdir(FILES_PATH):
        raise Exception(f"'get-pip.py' not found in {FILES_PATH}")
    else:
        GET_PIP_PATH = os.path.join(FILES_PATH, 'get-pip.py')

    PYTHON_EMBEDED_PATH = None
    for file in os.listdir(FILES_PATH):
        if "python" in file and "embed" in file and file.endswith(".zip"):
            PYTHON_EMBEDED_PATH = os.path.join(FILES_PATH, file)
            PYTHON_VERSION = "python" + file.split("-")[1].replace(".", "")[:2]
            break

    if not PYTHON_VERSION:
        raise Exception(f"'python-x.x.x-embed-xxxxx.zip' not found in {FILES_PATH}")

    pth_file   = PYTHON_VERSION + "._pth"
    zip_pyfile = PYTHON_VERSION + ".zip"

    print("Using", PYTHON_VERSION, "from:\n", GET_PIP_PATH, "\n", PYTHON_EMBEDED_PATH)
    
    return GET_PIP_PATH, PYTHON_EMBEDED_PATH, pth_file, zip_pyfile


# In[ ]:


def build(OPTIONS):
    """ Calling all funcs needed and processing options """
    
    BASE_DIR = os.getcwd()
    
    GET_PIP_PATH, PYTHON_EMBEDED_PATH, pth_file, zip_pyfile = process_options(OPTIONS)
    
    if not OPTIONS["install_only_these_modules"]:
        try:
            prep_requirements(OPTIONS)
        except:
            try:
                OPTIONS["use_pipreqs"] = False
                prep_requirements(OPTIONS)
            except:
                raise Exception("Please add modules needed in OPTIONS['include_modules']!")

        filter_requirements(OPTIONS)
    else:
        with open('requirements.txt', 'w') as f:
            f.write("\n".join(OPTIONS["install_only_these_modules"]))
            
    put_code_in_dist_folder()
    add_embeded_and_pip_to_dist(GET_PIP_PATH, PYTHON_EMBEDED_PATH)

    os.chdir("dist")
    print("Moved runtime to dist folder: ", os.getcwd())

    make_startup_batch(OPTIONS)
    prepare_for_pip_install(pth_file, zip_pyfile)
    install_requirements()
    
    os.chdir(BASE_DIR)
    
    print("\n\nFinished! Folder 'dist' contains your runnable application!\n\n")


# In[ ]:


# modules_to_install = ["flask",
#                       "pandas",
#                       "flaskwebgui",
#                       "plotly",
#                       "xlrd",
#                       "xlwt",
#                       "openpyxl",
#                      ]


# In[ ]:


# OPTIONS = {"main_file_name": "meckan.py", 
#            "show_console": False,
#            "use_pipreqs": True,
#            "install_only_these_modules": [],
#            "include_modules":[],
#            "exclude_modules":[],
#            "path_to_get_pip_and_python_embeded_zip": ""
#           }


# In[ ]:


# build(OPTIONS)


# In[ ]:




