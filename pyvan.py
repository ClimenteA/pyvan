from datetime import datetime
import traceback

import zipfile
import subprocess as sps
import os, shutil

import urllib.request




DOWNLOADS_PATH = os.path.join(os.getenv('USERPROFILE'), 'Downloads')

def show_traceback(err):
    """Write the error on a error txt file show the traceback of the error"""
    err_time = str(datetime.now()) #'2011-05-03 17:45:35.177000'
    tb_error_msg = traceback.format_exc()
    errormessage = "###########\n{}\nERROR:\n{}\n\nDetails:\n{}\n###########\n\n\n".format(err_time, err, tb_error_msg)
    
    # with open("ERRORS.txt", "a") as errfile:
    #     errfile.write(errormessage)
    print(errormessage)

    return errormessage


def prepare_dist(options):
    """
        Create the 'dist' folder where the app will be bundled
        Gather needed imports into a requirements.txt file
    """
    
    print("Copying static files..")
    src = os.getcwd()
    dst = os.path.join(src, "dist")
    shutil.copytree(src, dst)
    print("Done!")

    if options["use_pipreqs"]:
        print("Searching modules needed using 'pipreqs'...")
        sps.Popen(["pipreqs", "."], stdout=sps.PIPE, stderr=sps.PIPE, stdin=sps.PIPE).wait()
        # os.system("pipreqs --use-local .")
        shutil.move('requirements.txt', 'dist/requirements.txt')
    else:
        print("Searching modules needed using 'pip freeze'...")
        sps.Popen(["pip", "freeze", ">", "requirements.txt"], stdout=sps.PIPE, stderr=sps.PIPE, stdin=sps.PIPE).wait()
        # os.system("pip freeze > requirements.txt")
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

    if os.path.isfile(dst):
        print("Using already copied file", dst)
        return

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

    print("Succesfully copied to Downloads!")


def prepare_zip():
    """
        Extracting python embeded zip 
    """
    print("Extracting .zip file..")
    
    zip_ref = zipfile.ZipFile(os.path.join(DOWNLOADS_PATH, 'embeded_python.zip'), 'r')
    zip_ref.extractall('./dist')
    zip_ref.close()
    print("Done!")

    os.remove("./dist/python37._pth")
    print("Removed 'python37._pth' file")

    shutil.copy2(os.path.join(DOWNLOADS_PATH, 'get_pip.py'), './dist/get_pip.py')
    print("Copied get_pip.py to './dist'")


def get_modules(modules_to_install):
    """
        Install all needed modules
    """
    
    # sps.Popen(["cd dist"], stdout=sps.PIPE, stderr=sps.PIPE, stdin=sps.PIPE).wait()
    os.chdir('./dist')

    # Install get_pip.py in the dist folder
    # sps.Popen(["get_pip.py"], stdout=sps.PIPE, stderr=sps.PIPE, stdin=sps.PIPE).wait()
    os.system("get_pip.py")
    
    # sps.Popen(["cd", "Scripts"], stdout=sps.PIPE, stderr=sps.PIPE, stdin=sps.PIPE).wait()
    os.chdir("Scripts")
   
    for module in modules_to_install:
        print("Installing ", module)
        p = sps.Popen(["pip", "install", module], stdout=sps.PIPE, stderr=sps.PIPE, stdin=sps.PIPE)
        p.wait()
        # os.system("pip install {}".format(module))
        print("Done!")

    print("\nFinished installing dependencies!")



def prepare_main(options):
    """
        Prepare main entry point of the app by copying all needed files to 
        the extracted embeded python folder and creating a .bat file which will run the script
    """

    if options["show_console"]:
        bat_command = "START python " + options["main_file_name"]
    else:
        with open(options["main_file_name"], 'r') as p:
            out = p.read().splitlines()
            
        no_console_hack = ['import sys, os',
                            "if sys.executable.endswith('pythonw.exe'):",
                            "  sys.stdout = open(os.devnull, 'w')",
                            '  sys.stderr = open(os.path.join(os.getenv(\'TEMP\'), \'stderr-{}\'.format(os.path.basename(sys.argv[0]))), "w")',
                            '']
                   
        file_with_hack = no_console_hack + out

        with open(options["main_file_name"], "w") as m:    
            for line in file_with_hack:
                m.write(line)
                m.write("\n")
                bat_command = "START pythonw " + options["main_file_name"]
    
    
    os.chdir('..')
    bat_path = os.path.join(os.getcwd(), options["main_file_name"].replace(".py", ".bat"))
    
    with open(bat_path, "w") as b:
        b.write(bat_command)

    



def build(build_options):

    if not os.path.isfile(build_options["main_file_name"]):
        raise Exception("Entry point file(main_file_name) not found!")

    modules_to_install = prepare_dist(build_options)

    if "https://" in build_options["get_pip_location"]:
        get_files_from_url(build_options["get_pip_location"], os.path.join(DOWNLOADS_PATH, "get_pip.py"))
    else:
        print("Copying get_pip.py to dist..")
        shutil.copy2(build_options["get_pip_location"], "dist/get_pip.py")
        print("Done!")

    if "https://" in build_options["embeded_python_location"]:
        get_files_from_url(build_options["embeded_python_location"], os.path.join(DOWNLOADS_PATH, "embeded_python.zip"))
    else:
        print("Copying {} to dist..".format(build_options["embeded_python_location"]))
        shutil.copy2(build_options["embeded_python_location"], "dist/embeded_python.zip")
        print("Done!")

    dist_name = "dist/{}".format(build_options["main_file_name"].replace(".py", ""))

    prepare_zip()

    get_modules(modules_to_install)

    prepare_main(build_options)

    input("\n\nFinished! Folder 'dist' contains your runnable application!\n\nPress enter to exit...\n\n")


