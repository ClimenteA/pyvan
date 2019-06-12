from datetime import datetime
import traceback

import zipfile
import os, shutil, subprocess

import urllib.request


print("\npyvan - version 0.0.1\nDelivering your python apps to the people!\n\n")

if os.name == 'nt':
    DOWNLOADS_PATH = os.path.join(os.getenv('USERPROFILE'), 'Downloads')
else:
    DOWNLOADS_PATH = os.path.join(os.path.expanduser('~'), 'downloads')


def run_cmd(command):
    print("Running cmd: ", command)
    subprocess.call(command, shell=True)
    print("cmd executed")



def show_traceback(err):
    """Write the error on a error txt file show the traceback of the error"""
    err_time = str(datetime.now()) #'2011-05-03 17:45:35.177000'
    tb_error_msg = traceback.format_exc()
    errormessage = "###########\n{}\nERROR:\n{}\n\nDetails:\n{}\n###########\n\n\n".format(err_time, err, tb_error_msg)

    print(errormessage)

    with open("ERRORS.txt", "a") as errfile:
        errfile.write(errormessage)

    return errormessage



def get_static():
    try:
        shutil.rmtree('./dist')
    except:
        pass
    print("Copying static files..")
    src = os.getcwd()
    dst = os.path.join(src, "dist")
    shutil.copytree(src, dst)
    print("Done!")


def prepare_dist(options):
    """
        Create the 'dist' folder where the app will be bundled
        Gather needed imports into a requirements.txt file
    """

    get_static()

    if options["use_pipreqs"]:
        print("Searching modules needed using 'pipreqs'...")
        cmd = "pipreqs . --force --ignore dist"
        run_cmd(cmd)
        shutil.move('requirements.txt', 'dist/requirements.txt')

        print("Done!")
    else:
        print("Searching modules needed using 'pip freeze'...")
        cmd = "pip3 freeze > requirements.txt"
        run_cmd(cmd)
        shutil.move('requirements.txt', 'dist/requirements.txt')
        print("Done!")


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
            if module.endswith("info"):
                continue 
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

    os.chdir("./dist")
    print("CD to dist")
    print("Running get_pip.py from ", os.getcwd())
    os.system("get_pip.py")

    if not os.path.isdir("Scripts"):
        raise Exception("ERROR: pip not installed!")

    print("PIP installed!")
    os.chdir("./Scripts")
    print("CD to Scripts", os.getcwd())

    cmd = "pip3 install -r ../requirements.txt --no-cache-dir --no-warn-script-location"
    run_cmd(cmd)
    print("Done!")

    os.chdir("..")
    print("CD back to 'dist'")
    print("\nFinished installing dependencies!")



def prepare_main(options):
    """
        Prepare main entry point of the app by copying all needed files to
        the extracted embeded python folder and creating a .bat file which will run the script
    """

    print("Preparing .bat/ executable file in ", os.getcwd())

    if options["show_console"]:
        bat_command = "START python " + options["main_file_name"]
    else:
        print("--noconsole ", os.getcwd())
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
