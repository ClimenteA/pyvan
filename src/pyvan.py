#!/usr/bin/env python3
import re
import time
import os
import sys
import shutil
import zipfile
import subprocess
import click
import requests
from pathlib import Path
from genexe.generate_exe import generate_exe


# python_version can be anything of the form: `x.x.x` where any x may be set to a positive integer.
PYTHON_VERSION_REGEX = re.compile(r"^(\d+|x)\.(\d+|x)\.(\d+|x)$")
GET_PIP_URL = "https://bootstrap.pypa.io/get-pip.py"
PYTHON_URL = "https://www.python.org/ftp/python"
HEADER_NO_CONSOLE = """import sys, os
if sys.executable.endswith('pythonw.exe'):
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.path.join(os.getenv(\'TEMP\'), \'stderr-{}\'.format(os.path.basename(sys.argv[0]))), "w")
    
"""


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
    exit_code = process.returncode

    if exit_code == 0:
        print(output)
        return output
    else:
        raise Exception(command, exit_code, output)


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


def add_embeded_and_pip_to_dist(get_pip_file, embedded_python_file, pydist_dir):
    """ Copy embeded python and get-pip file to dist folder """
    
    print(f"Extracting {embedded_python_file} to {pydist_dir} folder")
    zip_ref = zipfile.ZipFile(embedded_python_file, 'r')
    zip_ref.extractall(pydist_dir)
    zip_ref.close()
    print("Zip file extracted!")

    shutil.copy2(get_pip_file, pydist_dir)
    print(f"File {get_pip_file} file copied to {pydist_dir}!")


def prepare_for_pip_install(pth_file, zip_pyfile, pydist_sub_dir_str, source_sub_dir_str):
    """
        Prepare the extracted embedded python version for pip installation
        - Uncommented 'import site' line from pythonXX._pth file
        - Extract pythonXX.zip zip file to pythonXX.zip folder and delete pythonXX.zip zip file
    """
    print(f"Generated '{pth_file}' file with uncommented 'import site' line.")
    with open(pth_file, 'w') as f:
        rel_path_to_sources = ("." if pydist_sub_dir_str == "" else "..") + source_sub_dir_str
        f.write(f'{os.path.basename(zip_pyfile)}\n{rel_path_to_sources}\n\n# Uncomment to run site.main() automatically\nimport site\n')

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


def make_startup_exe(main_file_name, show_console, build_dir, relative_pydist_dir, relative_source_dir, icon_file=None):
    """ Make the startup exe file needed to run the script """
    print("Making startup exe file")
    exe_fname = os.path.join(build_dir, main_file_name.split(".py")[0] + ".exe")
    python_entrypoint = "python.exe"
    command_str = f"{{EXE_DIR}}\\{relative_pydist_dir}\\{python_entrypoint} {{EXE_DIR}}\\{relative_source_dir}\\{main_file_name}"
    generate_exe(target=Path(exe_fname), command=command_str, icon_file=None if icon_file is None else Path(icon_file), show_console=show_console)

    if not show_console:
        with open(main_file_name, "r", encoding="utf8", errors="surrogateescape") as f:
            main_content = f.read()
        if HEADER_NO_CONSOLE not in main_content:
            with open(main_file_name, "w", encoding="utf8", errors="surrogateescape") as f:
                f.write(str(HEADER_NO_CONSOLE + main_content))

    print("Done!")


def download_url(url, save_path, chunk_size=128):
    """Download streaming a file url to save_path"""

    r = requests.get(url, stream=True)
    with open(save_path, 'wb') as fd:
        for chunk in r.iter_content(chunk_size=chunk_size):
            fd.write(chunk)


def get_all_available_python_versions():
    r = requests.get("https://www.python.org/ftp/python/")
    result = [tuple([int(e) for e in v.split(".")]) for v in re.findall(r">(\d+\.\d+\.\d+)/<", r.text)]
    return [v for v in sorted(result)]  # lowest to highest


def resolve_python_version(python_version):
    """
    Based on a python_version string resolve all the unknowns
    python_version (str) :
        can be None or of the form `x.x.x` where x may be an positive integer
        This method will attempt to resolve all the x's to the highest possible numbers.

        Note: In the case None is passed as the input
        the highest version of Python before the last minor release will be used.

    """

    if python_version is not None:
        if not re.match(PYTHON_VERSION_REGEX, python_version):
            raise ValueError("Specified python_version does not have the correct format, it should be of format: `x.x.x` where x can be replaced with a positive number.")
        version_strs = python_version.split(".")
        needs_resolving = any([e == "x" for e in version_strs])
        if not needs_resolving:
            return tuple(map(int, version_strs))
    # all other options need resolving
    all_py_versions = get_all_available_python_versions()
    if len(all_py_versions) == 0:
        raise RuntimeError("All available Python versions returned an empty list, this should not happen!")
    if python_version is None:
        max_py_version = all_py_versions[-1]
        py_versions = [v for v in all_py_versions if max_py_version[1] - 1 == v[1]]  # pick candidates one minor version less than the max
        return py_versions[-1]
    else:
        py_versions = all_py_versions
        for i, e in enumerate(python_version.split(".")):
            if e != "x":
                py_versions = [v for v in py_versions if v[i] == int(e)]
        if len(py_versions) > 0:
            return py_versions[-1]
        else:
            raise ValueError(f"Python version: {python_version} does not exists within the available Python versions list.")


def find_or_download_required_install_files(path_to_get_pip_and_python_embedded_zip, python_version):
    # Get the path to python embedded zip file and get-pip.py file
    if path_to_get_pip_and_python_embedded_zip == "":
        files_path = os.path.join(os.getenv('USERPROFILE'), 'Downloads')
    else:
        files_path = path_to_get_pip_and_python_embedded_zip

    get_pip_path = os.path.join(files_path, 'get-pip.py')
    if 'get-pip.py' not in os.listdir(files_path):
        print(f"'get-pip.py' not found in {files_path}, attempting to download it...")
        download_url(url=GET_PIP_URL, save_path=get_pip_path)
        if not os.path.isfile(get_pip_path):
            raise RuntimeError(f"Could not find get-pip.py in folder: {files_path}, and the download failed...")

    resolved_python_version = resolve_python_version(python_version=python_version)
    print(f"Resolved python_version {python_version}: {resolved_python_version}")

    python_version_str = "{v[0]}.{v[1]}.{v[2]}".format(v=resolved_python_version)
    embedded_file_name = f"python-{python_version_str}-embed-amd64.zip"
    embedded_path_file = os.path.join(files_path, embedded_file_name)
    if not os.path.isfile(embedded_path_file):
        print(f"{embedded_file_name} not found int {files_path}, attempting to download it.")
        download_url(url=f"{PYTHON_URL}/{python_version_str}/{embedded_file_name}", save_path=embedded_path_file)
        if not os.path.isfile(embedded_path_file):
            raise RuntimeError(f"Could not find {embedded_file_name} in folder: {files_path}, and the download failed...")

    short_python_version_str = "python" + python_version_str.replace(".", "")[:2]
    pth_file   = short_python_version_str + "._pth"
    zip_pyfile = short_python_version_str + ".zip"

    print(f"Using Python-{python_version_str} from:\n {get_pip_path} \n {embedded_path_file}")
    
    return get_pip_path, embedded_path_file, pth_file, zip_pyfile


def display_pyvan_build_config(input_dir, build_dir, exclude_modules, extra_pip_install_args, include_modules,
                               install_only_these_modules, main_file_name, pydist_sub_dir, show_console, source_sub_dir,
                               use_existing_requirements, use_pipreqs, python_version, icon_file):
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
    if python_version is not None:
        print(f"pyvan will attempt to install python version: {python_version}")
    else:
        print(f"no python version specified - pyvan will attempt to install latest stable python version")
    print(f"requirements will be installed with{'' if any(extra_pip_install_args) else 'out'} additional pip arguments")
    if any(extra_pip_install_args):
        print(f"extra_pip_install_args: {extra_pip_install_args}")
    print(f"===EXE FILE===")
    print(f"pyvan will generate an exe file for you in {build_dir}")
    print(f"pyvan will use the following settings:")
    print(f"main_file_name: {main_file_name}")
    print(f"show_console: {show_console}")
    if icon_file is not None:
        print(f"icon_file: {icon_file}")
    else:
        print("no icon file was set.")
    print()
    print(f"===START PYVAN BUILD===")


def prepare_empty_build_dir(build_dir):
    # Delete build folder if it exists
    if os.path.isdir(build_dir):
        print(f"Existing build directory found, removing contents... {build_dir}")
        shutil.rmtree(build_dir)
    os.makedirs(build_dir)


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


def build(
    main_file_name,
    show_console = False,
    input_dir = os.getcwd(),
    build_dir = os.path.join(os.getcwd(), "dist"),
    pydist_sub_dir = "pydist",
    source_sub_dir = "",
    python_version = None,
    use_pipreqs = True,
    include_modules = (),
    exclude_modules = (),
    install_only_these_modules = (),
    use_existing_requirements = False,
    extra_pip_install_args = (),
    path_to_get_pip_and_python_embedded_zip = "",
    icon_file = None
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
                               use_existing_requirements, use_pipreqs, python_version, icon_file)
    GET_PIP_PATH, PYTHON_EMBEDED_PATH, pth_file, zip_pyfile = find_or_download_required_install_files(
        path_to_get_pip_and_python_embedded_zip=path_to_get_pip_and_python_embedded_zip, python_version=python_version
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
    make_startup_exe(
        main_file_name=main_file_name,
        show_console=show_console,
        build_dir=build_dir,
        relative_pydist_dir="" if pydist_sub_dir == build_dir else pydist_sub_dir.replace(build_dir, "") + "\\",
        relative_source_dir="" if source_sub_dir == build_dir else source_sub_dir.replace(build_dir, "") + "\\",
        icon_file=icon_file
    )
    prepare_for_pip_install(
        pth_file=os.path.join(pydist_sub_dir, pth_file),
        zip_pyfile=os.path.join(pydist_sub_dir, zip_pyfile),
        pydist_sub_dir_str=pydist_sub_dir.replace(build_dir, ""),
        source_sub_dir_str=source_sub_dir.replace(build_dir, "")
    )
    install_requirements(
        pydist_dir=pydist_sub_dir,
        build_dir=build_dir,
        req_file=build_req_file,
        extra_pip_install_args=extra_pip_install_args
    )
    
    print(f"\n\nFinished! Folder '{build_dir}' contains your runnable application!\n\n")
    print("===END PYVAN BUILD===")


def validate_python_version_input(ctx, param, value):
    if value is None:
        return None
    if re.match(PYTHON_VERSION_REGEX, value):
       return value
    else:
        raise click.BadParameter("Python version must be of format: `x.x.x` where x may be a positive integer.")


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
    help="Specify to skip using pipreqs for resolving the requirements.txt file. Default: use pipreqs."
)
@click.option(
    "--python-version",
    "-py",
    "python_version",
    type=str,
    default=None,
    help="Specify to fix the embedded python version number, format x.x.x with x a positive integer. Default: use highest available stable python version.",
    callback=validate_python_version_input
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
@click.option(
    "--icon-file",
    "--icon",
    "icon_file",
    default=None,
    type=click.Path(exists=True, dir_okay=False, file_okay=True, resolve_path=True),
    help="An optional icon file to add to the generated executable for the stand-alone distribution. Default: don't use an icon"
)
def cli(
    main_file_name,
    show_console,
    input_dir,
    build_dir,
    pydist_sub_dir,
    source_sub_dir,
    use_pipreqs,
    python_version,
    include_modules,
    exclude_modules,
    install_only_these_modules,
    use_existing_requirements,
    extra_pip_install_args,
    path_to_get_pip_and_python_embedded_zip,
    icon_file,
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
        python_version=python_version,
        include_modules=include_modules,
        exclude_modules=exclude_modules,
        install_only_these_modules=install_only_these_modules,
        use_existing_requirements=use_existing_requirements,
        extra_pip_install_args=extra_pip_install_args,
        icon_file=icon_file,
        path_to_get_pip_and_python_embedded_zip="" if path_to_get_pip_and_python_embedded_zip is None else path_to_get_pip_and_python_embedded_zip
    )


if __name__ == "__main__":
    cli()
