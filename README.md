# Script to randomize the weather between two games on the same mission for multiplayer

This is a python script. It will monitor the missions launched by a Dserver and trigger a function that will change the weather options of the mission once it is ending.
This way, the next time the mission gets launched in the mission rotation, the weather will be different

## Installation
### Allow log files in il2:
Make sure gamelog=1 in your startup.cfg file

### download the executable

### Mission files organization  
The Dogfight folder should not contain the .Mission file as it would be downloaded by players by default which is not optimal (slower download speed).
Instead the raw mission files should be in another folder. In my case:
 "C:\\Program Files (x86)\\1C Game Studios\IL-2 Sturmovik Great Battles\\data\\Multiplayer\\raw_missions"
You have an example of working Multiplayer folder in the project. To test the system, you can copy paste it in your data folder and run the script.

### Configuring the script
Change the paths to your il2 installation and to your dogfight and raw mission folder in the config.ini file that is present in the dist folder. (for developers, use the config.ini at the root of the project source code directory)

### Launch the script
In the dist folder, click on random_weather.exe. A command propmpt will appear, then right clicl on the header of the command prompt and clik on properties, then uncheck 'Quick Edit Mode', otherwise the process might pause.

## Installation for developers
### Python Installation 
Install git: https://git-scm.com/download
Install python 3.6 For instance, use Anaconda to install python on your server :
https://repo.anaconda.com/archive/Anaconda3-2019.10-Windows-x86_64.exe
To launch a command prompt: windows key + type anaconda + hit enter on  'anaconda prompt'.
In this prompt create and activate the environment with the required packages:
```
conda create -n il2 python=3.6 configparser numpy regex -y
activate il2
pip install git+https://github.com/lefufu/PylGBMiMec
```
If you already have a python installation, the required packages are numpy, regex
and https://github.com/lefufu/PylGBMiMec
### launch the script 
* In the anaconda prompt, go to the script folder (using the cd commandline)
* After your dserver is running, launch the script: 
```
python random_weather.py
```
The weather should change in between two missions

### Building 
install py2exe (pip install py2exe)
and at the root of the project:
```
python setup.py py2exe
```

### Thanks

Thanks to Murleen for the mlg2txt parser (https://github.com/Murleen/mlg2txt)
Thanks to lefufu for the PylGBMiMec tool to edit .mission files (https://github.com/lefufu/PylGBMiMec) 


 
