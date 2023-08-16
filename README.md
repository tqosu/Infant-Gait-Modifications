# Code Prepare
__1. Install Homebrew__ \
1.1 reference: https://brew.sh/
1.2 open terminal
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

__2. Install wget__ \
2.1 reference: https://brew.sh/ \
2.2 open terminal
brew install wget

__3. Install miniconda__ \
3.1 https://docs.conda.io/projects/conda/en/latest/user-guide/install/macos.html \
3.2 open terminal
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh -O ~/miniconda.sh
bash ~/miniconda.sh -b -p $HOME/miniconda

__4. Install conda virtual environment and python3.6__ \
conda create -n myenv python=3.6

__5. Activate myenv environment__ 
```
source ~/miniconda/bin/activate 
conda activate myenv
```

__6. Install required python packages__ \
6.1 reference https://github.com/azieren/DevEv \
6.2 open terminal with step 5

```
pip install numpy scipy matplotlib opencv-python-headless==4.5.5.62 pyqtgraph PyQt5 PyOpenGL trimesh
```

# Data Prepare
1. Download the data in the google drive folder Flex to a local machine. 
2. Create a symlink for the Flex and replace the empty Flex directory in the project.