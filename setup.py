from setuptools import setup, find_packages

#python setup.py bdist_wheel sdist
#cd dist 
#twine upload *


with open("README.md", "r") as fh:
    long_description = fh.read()


setup (
	name="pyvan",
	version="0.0.5",
	description="Make runnable desktop apps from your python scripts more easily with pyvan!",
	url="https://github.com/ClimenteA/pyvan",
	author="Climente Alin",
	author_email="climente.alin@gmail.com",
	license='MIT',
	py_modules=["pyvan"],
	install_requires=['pipreqs'],
	packages=find_packages(),
	long_description=long_description,
    long_description_content_type="text/markdown",
	package_dir={"":"src"},
)