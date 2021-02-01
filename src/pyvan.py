#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import time
import os, sys
import shutil
import zipfile
import subprocess
import click

# In[ ]:


header_no_console = """import sys, os
if sys.executable.endswith('pythonw.exe'):
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.path.join(os.getenv(\'TEMP\'), \'stderr-{}\'.format(os.path.basename(sys.argv[0]))), "w")
    
"""


# In[ ]:


def execute_os_command(command, cwd=None):
    """Execute terminal command"""
    
    print("Running command: ", command)
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=os.getcwd() if cwd is None else cwd)

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


def put_code_in_dist_folder(source_dir, target_dir, build_dir):
    """Copy .py files and others to target folder"""
    if not os.path.isdir(os.path.dirname(target_dir)):
        os.makedirs(os.path.dirname(target_dir))
    print(f"Copying files from {source_dir} to {target_dir}!")
    shutil.copytree(
        src=source_dir,
        dst=target_dir,
        ignore=shutil.ignore_patterns(os.path.basename(build_dir), "__pycache__", "*.pyc"),
        dirs_exist_ok=True
    )
    print("Files copied!")


# In[ ]:


def prep_requirements(use_pipreqs, target_req_file, input_dir, build_dir):
    """ Create requirements.txt file from which to install modules on embeded python version """

    if use_pipreqs:
        print(f"Searching modules needed using 'pipreqs'...")
        execute_os_command(command=f"pipreqs {input_dir} --force --ignore {os.path.basename(build_dir)} --savepath {target_req_file}")
        print("Done!")
    else:
        print("Searching modules needed using 'pip freeze'...")
        execute_os_command(command=f"pip3.exe freeze > {target_req_file}", cwd=input_dir)
        print("Done!")


# In[ ]:


def filter_requirements(target_req_file, include_modules, exclude_modules):
    """Filter modules and keep only the ones needed"""
    
    print("Checking which modules to exclude or to keep")
    with open(target_req_file, 'r') as r:
        modules_to_install = r.read().splitlines()

    if any(exclude_modules):
        modules_to_install = list(set.difference(set(modules_to_install), set(exclude_modules)))

    if any(include_modules):
        modules_to_install = modules_to_install + include_modules

    print(f"Updating {target_req_file} file")
    with open(target_req_file, 'w') as f:
        f.write("\n".join(modules_to_install))

    print(f"File {target_req_file} done!")


# In[ ]:


def add_embeded_and_pip_to_dist(get_pip_file, embedded_python_file, pydist_dir):
    """ Copy embeded python and get-pip file to dist folder """
    
    print(f"Extracting {embedded_python_file} to {pydist_dir} folder")
    zip_ref = zipfile.ZipFile(embedded_python_file, 'r')
    zip_ref.extractall(pydist_dir)
    zip_ref.close()
    print("Zip file extracted!")

    shutil.copy2(get_pip_file, pydist_dir)
    print(f"File {get_pip_file} file copied to {pydist_dir}!")


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


def install_requirements(pydist_dir, build_dir, req_file, extra_pip_install_args = None):
    """
        Install pip and the modules from requirements.txt file
        - extra_pip_install_args (optional `List[str]`) : pass these additional arguments to the pip install command
    """
    print("Installing pip..")

    execute_os_command(command="python.exe get-pip.py --no-warn-script-location", cwd=pydist_dir)

    if not os.path.isdir(os.path.join(pydist_dir, "Scripts")):
        raise Exception("Module 'pip' didn't install corectly from 'get-pip.py' file!")

    print("Module pip installed!")

    scripts_dir = os.path.join(pydist_dir, "Scripts")

    if extra_pip_install_args is not None:
        extra_args_str = " " + " ".join(extra_pip_install_args)
    else:
        extra_args_str = ""

    try:
        cmd = f"pip3.exe install --no-cache-dir --no-warn-script-location -r {req_file}{extra_args_str}"
        execute_os_command(command=cmd, cwd=scripts_dir)
    except:
        print("Installing modules one by one..")

        with open(req_file, "r") as f:
            modules = f.read().splitlines()

        for module in modules:
            try:
                cmd = f"pip3.exe install --no-cache-dir --no-warn-script-location {module}{extra_args_str}"
                execute_os_command(command=cmd, cwd=scripts_dir)
            except:
                print("FAILED TO INSTALL ", module)
                with open(os.path.join(build_dir, "FAILED_TO_INSTALL_MODULES.txt"), "a") as f:
                    f.write(str(module + "\n"))


# In[ ]:


def make_startup_batch(main_file_name, show_console, build_dir, relative_pydist_dir, relative_source_dir):
    """ Make the startup batch files needed to run the script """
    
    print("Making startup batch files")

    bat_fname = os.path.join(build_dir, main_file_name.split(".py")[0] + ".bat")

    if show_console:
        with open(bat_fname, "w") as f:
            f.write(str(f"START %~dp0/{relative_pydist_dir}python %~dp0/{relative_source_dir}{main_file_name} %*"))
    else:
        with open(main_file_name, "r", encoding="utf8", errors="surrogateescape") as f:
            main_content = f.read()

        if header_no_console not in main_content:
            with open(main_file_name, "w", encoding="utf8", errors="surrogateescape") as f:
                f.write(str(header_no_console + main_content))

        with open(bat_fname, "w") as f:
            f.write(str(f"START %~dp0/{relative_pydist_dir}pythonw %~dp0/{relative_source_dir}{main_file_name} %*"))

    print("Done!")


# In[ ]:


def find_required_install_files(path_to_get_pip_and_python_embedded_zip):
    
    #Get the path to python emebeded zip file and get-pip.py file
    if path_to_get_pip_and_python_embedded_zip == "":
        FILES_PATH = os.path.join(os.getenv('USERPROFILE'), 'Downloads')
    else:
        FILES_PATH = path_to_get_pip_and_python_embedded_zip

    if 'get-pip.py' not in os.listdir(FILES_PATH):
        raise FileNotFoundError(f"'get-pip.py' not found in {FILES_PATH}")
    else:
        GET_PIP_PATH = os.path.join(FILES_PATH, 'get-pip.py')

    PYTHON_EMBEDED_PATH = None
    for file in os.listdir(FILES_PATH):
        if "python" in file and "embed" in file and file.endswith(".zip"):
            PYTHON_EMBEDED_PATH = os.path.join(FILES_PATH, file)
            PYTHON_VERSION = "python" + file.split("-")[1].replace(".", "")[:2]
            break

    if not PYTHON_VERSION:
        raise FileNotFoundError(f"'python-x.x.x-embed-xxxxx.zip' not found in {FILES_PATH}")

    pth_file   = PYTHON_VERSION + "._pth"
    zip_pyfile = PYTHON_VERSION + ".zip"

    print(f"Using {PYTHON_VERSION} from:\n {GET_PIP_PATH} \n {PYTHON_EMBEDED_PATH}")
    
    return GET_PIP_PATH, PYTHON_EMBEDED_PATH, pth_file, zip_pyfile


# In[ ]:


def display_pyvan_build_config(input_dir, build_dir, exclude_modules, extra_pip_install_args, include_modules,
                               install_only_these_modules, main_file_name, pydist_sub_dir, show_console, source_sub_dir,
                               use_existing_requirements, use_pipreqs):
    print(f"===PYVAN BUILD CONFIGURATION===")
    print(f"Input dir: {input_dir}")
    print(f"Build dir: {build_dir}")
    print(f"Python distribution will be installed in: {pydist_sub_dir}")
    print(f"App source code will be installed in: {source_sub_dir}")
    print(f"===REQUIREMENTS===")
    if use_existing_requirements:
        print(f"pyvan will try to install from existing requirements.txt at {input_dir}")
    elif any(install_only_these_modules):
        print("pyvan will generate a requirements.txt for you based on the following specified modules:")
        print(f"install_only_these_modules: {install_only_these_modules}")
    else:
        print("pyvan will try to resolve requirements for you using pipreqs and/or pip freeze:")
        print(f"use_pip_reqs: {use_pipreqs}")
        print(f"include_modules: {include_modules}")
        print(f"exclude_modules: {exclude_modules}")
    print("===BUILD OPTIONS===")
    print(f"requirements will be installed with{'' if any(extra_pip_install_args) else 'out'} additional pip arguments")
    if any(extra_pip_install_args):
        print(f"extra_pip_install_args: {extra_pip_install_args}")
    print(f"===BATCH FILE===")
    print(f"pyvan will generate a batch file for you in {build_dir}")
    print(f"pyvan will use the following settings:")
    print(f"main_file_name: {main_file_name}")
    print(f"show_console: {show_console}")
    print()
    print(f"===START PYVAN BUILD===")


# In[ ]:


def prepare_empty_build_dir(build_dir):
    # Delete build folder if it exists
    if os.path.isdir(build_dir):
        print(f"Existing build directory found, removing contents... {build_dir}")
        shutil.rmtree(build_dir)
    os.makedirs(build_dir)


# In[ ]:


def prepare_build_requirements_file(input_dir, build_dir, build_req_file, use_existing_requirements, exclude_modules,
                                    install_only_these_modules, include_modules, use_pipreqs):
    base_dir_req_file = os.path.join(input_dir, "requirements.txt")
    if use_existing_requirements:
        if not os.path.isfile(base_dir_req_file):
            raise FileNotFoundError(
                f"No requirements.txt file was found in: {input_dir}\nuse_existing_requirements requires one.")
        print(f"Using/copying existing requirements.txt file from: {input_dir}")
        shutil.copy(src=base_dir_req_file, dst=build_req_file)
    elif not any(install_only_these_modules):
        try:
            prep_requirements(use_pipreqs=use_pipreqs, target_req_file=build_req_file, input_dir=input_dir, build_dir=build_dir)
        except:
            failed = not use_pipreqs
            if not failed:
                try:
                    prep_requirements(use_pipreqs=False, target_req_file=build_req_file, input_dir=input_dir, build_dir=build_dir)
                except:
                    failed = True
            if failed:
                raise RuntimeError(
                    "pyvan was unable to generate a requirements.txt. Please add modules needed in OPTIONS['include_modules'] or provide a requirements.txt file and specify OPTIONS['use_existing_requirements']!")

        filter_requirements(target_req_file=build_req_file, include_modules=include_modules,
                            exclude_modules=exclude_modules)
    else:
        with open(build_req_file, 'w') as f:
            f.write("\n".join(install_only_these_modules))


# In[ ]:


def build(
    main_file_name,
    show_console = False,
    input_dir = os.getcwd(),
    build_dir = os.path.join(os.getcwd(), "dist"),
    pydist_sub_dir = "",
    source_sub_dir = "",
    use_pipreqs = True,
    include_modules = (),
    exclude_modules = (),
    install_only_these_modules = (),
    use_existing_requirements = False,
    extra_pip_install_args = (),
    path_to_get_pip_and_python_embedded_zip = ""
):
    """ Calling all funcs needed and processing options """
    if isinstance(main_file_name, dict):
        raise ValueError("Old interface was passed to `pyvan.build`, please "
                         "dereference the options dictionary using: `pyvan.build(**OPTIONS)`")
    input_dir = os.path.abspath(input_dir)
    build_dir = os.path.abspath(build_dir)
    pydist_sub_dir = build_dir if pydist_sub_dir == "" else os.path.join(build_dir, pydist_sub_dir)
    source_sub_dir = build_dir if source_sub_dir == "" else os.path.join(build_dir, source_sub_dir)
    build_req_file = os.path.join(build_dir, "requirements.txt")

    display_pyvan_build_config(input_dir, build_dir, exclude_modules, extra_pip_install_args, include_modules,
                               install_only_these_modules, main_file_name, pydist_sub_dir, show_console, source_sub_dir,
                               use_existing_requirements, use_pipreqs)
    GET_PIP_PATH, PYTHON_EMBEDED_PATH, pth_file, zip_pyfile = find_required_install_files(
        path_to_get_pip_and_python_embedded_zip=path_to_get_pip_and_python_embedded_zip
    )
    prepare_empty_build_dir(build_dir=build_dir)
    prepare_build_requirements_file(
        input_dir=input_dir,
        build_dir=build_dir,
        build_req_file=build_req_file,
        use_existing_requirements=use_existing_requirements,
        use_pipreqs=use_pipreqs,
        exclude_modules=exclude_modules,
        include_modules=include_modules,
        install_only_these_modules=install_only_these_modules
    )
    put_code_in_dist_folder(
        source_dir=input_dir,
        target_dir=source_sub_dir,
        build_dir=build_dir
    )
    add_embeded_and_pip_to_dist(
        get_pip_file=GET_PIP_PATH,
        embedded_python_file=PYTHON_EMBEDED_PATH,
        pydist_dir=pydist_sub_dir
    )
    make_startup_batch(
        main_file_name=main_file_name,
        show_console=show_console,
        build_dir=build_dir,
        relative_pydist_dir="" if pydist_sub_dir == build_dir else pydist_sub_dir.replace(build_dir, "") + "\\",
        relative_source_dir="" if source_sub_dir == build_dir else source_sub_dir.replace(build_dir, "") + "\\"
    )
    prepare_for_pip_install(
        pth_file=os.path.join(pydist_sub_dir, pth_file),
        zip_pyfile=os.path.join(pydist_sub_dir, zip_pyfile)
    )
    install_requirements(
        pydist_dir=pydist_sub_dir,
        build_dir=build_dir,
        req_file=build_req_file,
        extra_pip_install_args=extra_pip_install_args
    )
    
    print(f"\n\nFinished! Folder '{build_dir}' contains your runnable application!\n\n")
    print("===END PYVAN BUILD===")


# In[ ]:


@click.command(name="cli")
@click.argument(
    "main_file_name",
    type=click.Path(exists=False, dir_okay=False)
)
@click.option(
    "--no-console",
    "-nc",
    "show_console",
    is_flag=True,
    default=True,
    help="Specify to hide the console window when running the application, e.g. for a service or GUI app"
)
@click.option(
    "--use-existing-reqs",
    "use_existing_requirements",
    is_flag=True,
    default=False,
    help="Specify to use an exsiting requirements.txt in the `input_dir` instead of trying to resolve the requirements automatically. Default: try to resolve requirements."
)
@click.option(
    "--no-pipreqs",
    "use_pipreqs",
    is_flag=True,
    default=True,
    help="Specify to skip using pipreqs for resolving the requirements.txt file. Default use pipreqs."
)
@click.option(
    "--input-dir",
    default=os.path.abspath(os.getcwd()),
    type=click.Path(exists=True, dir_okay=True, file_okay=False, resolve_path=True),
    help="The directory with the `main_file_name` file and other files to install. Default: the current working directory."
)
@click.option(
    "--build-dir",
    default=os.path.abspath(os.path.join(os.getcwd(), "dist")),
    type=click.Path(exists=False, dir_okay=True, file_okay=False, resolve_path=True),
    help="The directory in which pyvan will create the stand-alone distribution. Default: ./dist"
)
@click.option(
    "--pydist-sub-dir",
    "pydist_sub_dir",
    default="pydist",
    type=click.Path(exists=False),
    help="A sub directory relative to `build_dir` where the stand-alone python distribution will be installed. Default: ./pydist"
)
@click.option(
    "--source-sub-dir",
    "source_sub_dir",
    default="",
    type=click.Path(exists=False),
    help="A sub directory relative to `build_dir` where the to execute python files will be installed. Default: `build_dir`"
)
@click.option(
    "--embedded-files-dir",
    "path_to_get_pip_and_python_embedded_zip",
    default=None,
    type=click.Path(exists=True, dir_okay=True, file_okay=False, resolve_path=True),
    help="The directory which should contain 'get-pip.py' and the 'python-x.x.x-embed-amdxx.zip' files. Default: is the users Download directory."
)
@click.option(
    "--req-install-only",
    "-r",
    "install_only_these_modules",
    default=(),
    multiple=True,
    type=str,
    help="Specify these to directly generate a requirements.txt file using the specified modules. Default: [], use pipreqs."
)
@click.option(
    "--req-include",
    "-i",
    "include_modules",
    default=(),
    multiple=True,
    type=str,
    help="Specify these to directly add additional modules to a generated requirements.txt file. Default: []."
)
@click.option(
    "--req-exclude",
    "-e",
    "exclude_modules",
    default=(),
    multiple=True,
    type=str,
    help="Specify these to directly remove modules from a generated requirements.txt file. Default: []."
)
@click.option(
    "--pip-install-arg",
    "-a",
    "extra_pip_install_args",
    default=(),
    multiple=True,
    type=str,
    help="These arguments will be added to the pip install command during the stand-alone distribution build and allow the user to specify additional arguments this way. Default: []."
)
def cli(
    main_file_name,
    show_console,
    input_dir,
    build_dir,
    pydist_sub_dir,
    source_sub_dir,
    use_pipreqs,
    include_modules,
    exclude_modules,
    install_only_these_modules,
    use_existing_requirements,
    extra_pip_install_args,
    path_to_get_pip_and_python_embedded_zip
):
    """
    Package your python script(s) as a stand-alone Windows application.

    Basic usage:

    $ pyvan main.py

    This command will try to make main.py the entrypoint of your application.
    It will automatically try to resolve the required requirements by running `pipreqs` in your `input_dir`.
    Next, it will attempt to search and install an embedded python distribution using the generated requirements.
    Finally, it will link the packaged sources to the packaged python distribution using a batch file.
    The stand-alone application can then be found inside the generated `build_dir` ("dist") folder.

    """
    build(
        main_file_name=main_file_name,
        show_console=show_console,
        input_dir=input_dir,
        build_dir=build_dir,
        pydist_sub_dir=pydist_sub_dir,
        source_sub_dir=source_sub_dir,
        use_pipreqs=use_pipreqs,
        include_modules=include_modules,
        exclude_modules=exclude_modules,
        install_only_these_modules=install_only_these_modules,
        use_existing_requirements=use_existing_requirements,
        extra_pip_install_args=extra_pip_install_args,
        path_to_get_pip_and_python_embedded_zip="" if path_to_get_pip_and_python_embedded_zip is None else path_to_get_pip_and_python_embedded_zip
    )


if __name__ == "__main__":
    cli()
