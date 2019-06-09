# import urllib.request

# # Copy get_pip.py

# url = "https://bootstrap.pypa.io/get-pip.py"
# headers = {}

# url_request = urllib.request.Request(url, headers=headers)
# url_connect = urllib.request.urlopen(url_request)

# #remember to open file in bytes mode
# with open("get_pip.py", 'wb') as f:
#     while True:
#         buffer = url_connect.read(1024)
#         if not buffer: break

#         #an integer value of size of written data
#         data_wrote = f.write(buffer)

# #you could probably use with-open-as manner
# url_connect.close()


# # Copy the embeded python zip 
# pyurl = "https://www.python.org/ftp/python/3.7.3/python-3.7.3-embed-amd64.zip"
# headers = {}

# url_request = urllib.request.Request(pyurl, headers=headers)
# url_connect = urllib.request.urlopen(url_request)

# #remember to open file in bytes mode
# with open("python-3.7.3-embed-amd64.zip", 'wb') as f:
#     while True:
#         buffer = url_connect.read(1024)
#         if not buffer: break

#         #an integer value of size of written data
#         data_wrote = f.write(buffer)

# #you could probably use with-open-as manner
# url_connect.close()


# # Extract the embeded python files
# import os
# import zipfile

# path_to_zip_file = "python-3.7.3-embed-amd64.zip"
# directory_to_extract_to = "py37-app"
# os.mkdir(directory_to_extract_to)

# zip_ref = zipfile.ZipFile(path_to_zip_file, 'r')
# zip_ref.extractall(directory_to_extract_to)
# zip_ref.close()


# # Go to extracted folder and delete the pythonxy._pth" file
# import os

# os.remove(os.path.join(directory_to_extract_to, "python37._pth"))


# # Move get_pip.py to extracted dir
# import os, shutil

# shutil.copy2('get_pip.py', os.path.join(directory_to_extract_to, 'get_pip.py'))


# Change dir to emebeded python

# import os

# os.chdir("{}".format(directory_to_extract_to))

# print(os.getcwd())


# # Install get_pip.py in the extracted folder

# os.system("get_pip.py")


# CD to Scripts and start installing needed modules

# os.chdir("Scripts")

# print(os.getcwd())

# os.system("pip install flaskwebgui")


# in the future set noe available to environment path
# make posible commands like 
# noe --noconsole main.py

# 

