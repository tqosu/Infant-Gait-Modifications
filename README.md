# Code Prepare

__1. Set up miniconda3 on macOS__ \
1.1 To install miniconda, you can follow the instructions provided in the official documentation at this link: [Miniconda Installation Guide for macOS](https://docs.conda.io/projects/conda/en/latest/user-guide/install/macos.html). \
1.2  First, download the Miniconda installer for macOS from the following location: [Miniconda3-latest-MacOSX-x86_64.sh](https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh). Make sure to save the installer to the path `~/Miniconda3-latest-MacOSX-x86_64.sh`. \
1.3 After downloading the installer, open your terminal and run the following command to install miniconda: \
```
bash ~/Miniconda3-latest-MacOSX-x86_64.sh -b -p ~/miniconda3
```
__2. Install conda virtual environment and python3.6__ 
```
source ~/miniconda3/bin/activate 
conda create -n myenv python=3.6
```
__3. Activate myenv environment__ 
```
source ~/miniconda3/bin/activate 
conda activate myenv
```

__4. Install required python packages__ \
4.1 reference https://github.com/azieren/DevEv \
4.2 open terminal with step 5

```
pip install numpy scipy matplotlib opencv-python-headless==4.5.5.62 pyqtgraph PyQt5 PyOpenGL trimesh pandas labelme colorama gdown scikit-image onnxruntime
```

# Preparing the Data
1. Download the data and save it on your local computer.

2. Establish a symbolic link for the Flex data and substitute the existing empty Flex directory in the project using the guidance outlined in ./Flex/symlink.md.

3. Tips \
3.1. Download all files excluding dataset and dataset2 \
3.2. dataset folder \
2021_Flex1_Sxx_SlopeProtractor.mp4 is needed. You may copy it from local, rename it and place it in the corresponding path. \
3.3. dataset2 folder \ You may download the video you coded first.

# Execution
0. Terminal. \
0.1. Open a terminal and change the current directory to the FLEX path, which has the 1.py file.
```
cd .../FLEX
```
1. Initiate the environment by executing the following commands:
```
source ~/miniconda3/bin/activate
conda activate myenv
```
2. Launch the correction tool by running:
```
python 1.py
```
