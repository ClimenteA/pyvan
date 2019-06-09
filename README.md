# pyvan
IN PROGRESS - pack/freeze your scripts into runnable applications, in order to easly distribute python applications

## SUMMARY
<br>
This indends to be an alternative to the limited choises of freezing python applications and distribute them to other PC's without python installed.

<br>

## TODO

<br>

- [ ] detect needed python version and modules necessary to run the created script/s 
- [ ] download the embeded python version and delete from it pythonxy._pth file
- [ ] fetch get_pip.py file from the web and install it 
- [ ] install necessary modules using pip based on requirements.txt or pipenv file
- [ ] insert bellow code to the main.py file 
<br>

```
# Needed to run with no-console
import sys, os
if sys.executable.endswith("pythonw.exe"):
  sys.stdout = open(os.devnull, "w");
  sys.stderr = open(os.path.join(os.getenv("TEMP"), "stderr-"+os.path.basename(sys.argv[0])), "w")
```
- [ ] create a .bat file which will link the python.exe or pythonw.exe to the main.py file, bellow batch command:
```
START pythonw main.py
```
- [ ] convert the .bat file to .exe and set an icon

