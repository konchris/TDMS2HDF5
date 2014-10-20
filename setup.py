# A simple setup script to create an executable using PyQt4. This also
# demonstrates the method for creating a Windows executable that does not have
# an associated console.
#
# PyQt4app.py is a very simple type of PyQt4 application
#
# Run the build process by running the command 'python setup.py build'
#
# If everything works well you should find a subdirectory in the build
# subdirectory that contains the files needed to run the application

#application_title = "TDMS 2 HDF5 Converter" 
#what you want to application to be called
#main_python_file = "tdms2hdf5.pyw"
#the name of the python file you use to run the program

import sys

from cx_Freeze import setup, Executable

#base = None
#if sys.platform == "win32":

includefiles = ["data_structures.py","gui_elements.py"]
excludes = []
packages = []
includes = []

exe = Executable(
    # what to build
    script = "tdms2hdf5.pyw", # the name of your main python script goes here 
    initScript = None,
    base = "Win32GUI",
    targetName = "TDMS_2_HDF5.exe", # this is the name of the executable file
    copyDependentFiles = True,
    compress = True,
    appendScriptToExe = True,
    appendScriptToLibrary = True,
    icon = None # if you want to use an icon file, specify the file name here
)

setup(
    # the actual setup & the definition of other misc. info
    name = "TDMS 2 HDF5 Converter", # program name
    version = "0.3",
    description = "View and convert TDMS files to HDF5 format.",
    author = "Christopher Espy",
    author_email = "christopher.espy@uni-konstnaz.de",
    options = {"build_exe": {"excludes":excludes,"packages":packages,
                             "include_files":includefiles}},
    executables = [exe]
)
