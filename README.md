# Vign_LETG

Installation
-------------

For ease of use, we recommend that you first install Git and Anaconda.

Pre-requis:

      Git
      Anaconda or miniconda

Git Windows:

      #For Windows distribution, you can install with this link :
      https://git-scm.com/download/win
We recommmend to choose the Standalone Installer

Git Linux (Debian/Ubuntu):

      # You can install git with this command:
      sudo apt install git-all
      
Git Linux (Fedora):
      
      # You can install git with this command:
      sudo dnf install git-all

Anaconda: 

      # You can download and install anaconda with this link :
      https://www.anaconda.com/download/success

Library Dependency
---------------
Once the prerequisites have been installed, you can launch the next section via Anaconda Prompt

```
# Clone the repo
git clone https://github.com/JP-LETG-Rennes/RandomForest_Hiear.git
cd RF_Hiearchique

# Create a new python environnement with conda  
conda create --name Hiclass python=3.9
conda activate Hiclass

# Prepare pip
conda install pip
pip install --upgrade pip

# Install requirements
pip install -r requirements_env.txt

```

Getting Started
---------------
If Using Notebook:

      1. Download build from source by following the previous steps in the conda prompt terminal.
      2. Activate Conda Environnement Hiclass with following command : activate Hiclass
      3. Launching jupyter notebook from conda terminal with following command : jupyter notebook
      4. Lauching via terminal Hiclass.ipynb 

If Using Terminal:

      1. Download build from source. 
      2. Activate Conda Environnement Hiclass
      3. Enter variables in configuration file : configuration_RF_hiearchique.json
      4. Launching via terminal Hiclass.py
