from datetime import datetime
import traceback

import zipfile
import os, shutil

import urllib.request


def write_traceback(err):
    """Write the error on a error txt file show the traceback of the error"""
    err_time = str(datetime.now()) #'2011-05-03 17:45:35.177000'
    tb_error_msg = traceback.format_exc()
    errormessage = "###########\n{}\nERROR:\n{}\n\nDetails:\n{}\n###########\n\n\n".format(err_time, err, tb_error_msg)
    
    with open("ERRORS.txt", "a") as errfile:
        errfile.write(errormessage)
    
    return errormessage


def prepare_dist(options):
    """
        Create the 'dist' folder where the app will be bundled
        Gather needed imports into a requirements.txt file
    """
    try:
        print("Making 'dist' folder")
        os.mkdir("dist")
    except:
        print("Folder 'dist' already exists!")


    if options["use_pipreqs"]:
        print("Using 'pipreqs' for a minimal bundle")
        os.system("pipreqs --use-local .")
        shutil.move('requirements.txt', 'dist/requirements.txt')
    else:
        print("Using 'pip freeze' to gather all modules")
        os.system("pip freeze > requirements.txt")
        shutil.move('requirements.txt', 'dist/requirements.txt')

    
    print("Checking which modules to exclude or to keep")

    with open('dist/requirements.txt', 'r') as r:
        modules_to_install = r.read().splitlines()

    if options["exclude_modules"]:
        modules_to_install = list(set.difference(set(modules_to_install), 
                                                 set(options["exclude_modules"]
                                                 )))
    
    if options["include_modules"]:
        modules_to_install = modules_to_install + options["include_modules"]
    
    print("Updating 'dist/requirements.txt' file")
    with open('dist/requirements.txt', 'w') as r:
        for module in modules_to_install:
            if not module == modules_to_install[-1]:
                r.write(str(module) + "\n")
            else:
                r.write(str(module))

    print("Requirements check done!")
    return modules_to_install



def get_files_from_url(url, dst):
    """
        Copy the file from the url specified to the dst specified
    """

    print("Copying data from ", url, " ..")

    headers = {}
    url_request = urllib.request.Request(url, headers=headers)
    url_connect = urllib.request.urlopen(url_request)

    with open(dst, 'wb') as f:
        while True:
            buffer = url_connect.read(1024)
            if not buffer: break
            f.write(buffer)

    url_connect.close()

    print("Succesfully copied to ", dst)


def prepare_zip(dist_name, options):
    """
        Extracting python embeded zip 
    """
    print("Extracting .zip file..")
    
    os.mkdir(dist_name)

    zip_ref = zipfile.ZipFile('dist/embeded_python.zip', 'r')
    zip_ref.extractall(dist_name)
    zip_ref.close()
    print("Files extracted to ", dist_name)

    os.remove(os.path.join(dist_name, "python37._pth"))
    print("Removed 'python37._pth' file")

    shutil.copy2('dist/get_pip.py', os.path.join(dist_name, 'get_pip.py'))
    print("Copied get_pip.py to extracted zip")

    return dist_name


def get_modules(dist_name, modules_to_install, options):
    """
        Install all needed modules
    """
    
    os.chdir("{}".format(dist_name))

    # Install get_pip.py in the extracted folder
    os.system("get_pip.py")
    os.chdir("Scripts")

    for module in modules_to_install:
        os.system("pip install {}".format(module))

    print("\nFinished installing dependencies!")




def copy_dirs(src, dst, symlinks=False, ignore=None):
    """Copy dirs and it's items from src to dst"""

    if not os.path.exists(dst):
        os.makedirs(dst)
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            copy_dirs(s, d, symlinks, ignore)
        else:
            if not os.path.exists(d) or os.stat(s).st_mtime - os.stat(d).st_mtime > 1:
                shutil.copy2(s, d)



def get_files(root_path="./"):
    """Walk thru a start path and return a list of paths to files"""

    allfiles = []
    for root, _, files in os.walk(root_path):
        for f in files:
            path_tofile = os.path.join(root, f)
            if "\\dist" in path_tofile or "\\__pycache__" in path_tofile or "\\.ipynb_checkpoints" in path_tofile or '\\van.py' in path_tofile:
                continue
            allfiles.append(path_tofile)
    
    return allfiles



def prepare_main(dist_name, options):
    """
        Prepare main entry point of the app by copying all needed files to 
        the extracted embeded python folder and creating a .bat file which will run the script
    """

    static_files = get_files()

    exename = dist_name.replace("dist/", "")

    for static_file in static_files:
        src = static_file
        dst = os.path.join("./dist/{}".format(exename), static_file)

        copy_dirs(src, dst)

    

    # if options["show_console"]:
    #     bat_command = "START python {}.py".format(exename)
    # else:
    #     with open("main.py", 'r') as p:
    #         out = p.read().splitlines()
            
    #     no_console_hack = ['import sys, os',
    #                         "if sys.executable.endswith('pythonw.exe'):",
    #                         "  sys.stdout = open(os.devnull, 'w')",
    #                         '  sys.stderr = open(os.path.join(os.getenv(\'TEMP\'), \'stderr-{}\'.format(os.path.basename(sys.argv[0]))), "w")',
    #                         '']
                   
    #     file_with_hack = no_console_hack + out

    #     with open("{}.py".format(exename), "w") as m:    
    #         for line in file_with_hack:
    #             m.write(line)
    #             m.write("\n")
    #             bat_command = "START pythonw {}.py".format(exename)
    
    
    # with open(exename + ".bat", "w") as b:
    #     b.write(bat_command)

    



def build(build_options):

    # modules_to_install = prepare_dist(build_options)

    # if "https://" in build_options["get_pip_location"]:
    #     get_files_from_url(build_options["get_pip_location"], "dist/get_pip.py")
    # else:
    #     print("Copying get_pip.py to dist..")
    #     shutil.copy2(build_options["get_pip_location"], "dist/get_pip.py")
    #     print("Done!")

    # if "https://" in build_options["embeded_python_location"]:
    #     get_files_from_url(build_options["embeded_python_location"], "dist/embeded_python.zip")
    # else:
    #     print("Copying {} to dist..".format(build_options["embeded_python_location"]))
    #     shutil.copy2(build_options["embeded_python_location"], "dist/embeded_python.zip")
    #     print("Done!")

    dist_name = "dist/{}".format(build_options["main_file_name"].replace(".py", ""))

    # prepare_zip(dist_name, build_options)

    # get_modules(dist_name, modules_to_install, build_options)

    prepare_main(dist_name, build_options)


