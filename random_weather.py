import os
import time
import regex as re
import random
import numpy as np
import subprocess
import shutil
from mlg2txt_function2 import parse_mlg
import config_weather_script

exe_resaver = config_weather_script.exe_resaver
path_data = config_weather_script.path_data
path_mlg = config_weather_script.path_mlg
path_raw_missions = config_weather_script.path_raw_missions
path_dogfight = config_weather_script.path_dogfight
random_windlayers = config_weather_script.random_windlayers



def string_wind_layer(random_windlayer):
    '''
    Structuring the wind layer data in the same format as in the .Mission file
    '''
    s = """WindLayers 
  {{
    0 :     {0} :     {1};
    500 :     {2} :     {3};
    1000 :     {4} :     {5};
    2000 :     {6} :     {7};
    5000 :     {8} :     {9};
  }}""".format(
        *[random_windlayer[k][l] for k in ['ground', '500', '1000', '2000', '5000'] for l in ['direction', 'speed']])
    return s


def make_random_mission_options(season):
    '''
    Creating random data for mission options
    '''
    if season == 'su':
        clouds_type = random.choice(['00_clear', '01_light', '02_medium', '03_heavy', '04_overcast'])
        PrecType = 0
        PrecLevel = 0
        if clouds_type == '04_overcast':
            PrecType = random.randint(0, 1)
            if PrecType == 1:
                PrecLevel = random.randint(0, 100)
        random_wind = 10 * np.abs(np.random.normal())  # mean value: 7m/s, rarely above 49m/s
        random_winds = []
        for i in range(5):
            random_winds.append(random_wind)
            random_wind = random_wind + np.abs(np.random.normal())
        random_winds = ['%.2f' % rw for rw in random_winds]
        random_wind_direction = random.randint(0, 359)
        random_wind_directions = []
        for i in range(5):
            random_wind_directions.append(random_wind_direction)
            random_wind_direction = int(random_wind_direction + 5 * np.random.normal()) % 360
        d_summer = {'Time': '{0}:30:0'.format(random.randint(6, 17)),
                    'CloudLevel': random.randint(500, 3500),
                    'CloudConfig': "summer\\\{0}_0{1}\\sky.ini".format(clouds_type, random.randint(0, 9)),
                    'SeaState': random.randint(0, 6),
                    'Turbulence': random.randint(0, 10),
                    'Temperature': random.randint(20, 35),
                    'Pressure': random.randint(682, 796),
                    'Haze': str(random.random())[0:3],
                    'PrecType': PrecType,
                    'PrecLevel': PrecLevel,
                    'WindLayers': {'ground': {'direction': random_wind_directions[0], 'speed': random_winds[0]},
                                   '500': {'direction': random_wind_directions[1], 'speed': random_winds[1]},
                                   '1000': {'direction': random_wind_directions[2], 'speed': random_winds[2]},
                                   '2000': {'direction': random_wind_directions[3], 'speed': random_winds[3]},
                                   '5000': {'direction': random_wind_directions[4], 'speed': random_winds[4]}}
                    }
        return d_summer


def list_mlg_logs():
    '''
    Creates a list of mlg log files paths
    '''
    l = []
    for file in os.listdir(path_mlg):
        if file.endswith(".mlg"):
            l.append(os.path.join(path_mlg, file))
    return l


def clean_mlg_log():
    '''
    Remove already processed log files. Warning -> this can be a problem if the logs are needed for another process
    '''
    for f in os.listdir(path_mlg):
        if f.endswith(".mlg"):
            try:
                os.remove(os.path.join(path_mlg, f))
            except OSError as e:
                # print(e)
                pass
            except:
                raise


def check_if_mission_ended(mlg_output):
    '''
    check if the mission is finished byt looking for the mission end code in the logs
    '''
    for output in mlg_output:
        if 'AType:7' in output:
            return True
    return False


def mission_file(mlg_output):
    '''
    return the mission name if present in the logs (at the beginning of the mission)
    '''
    for output in mlg_output:
        if 'MFile:' in output:
            mission = output.split('\\')[-1].split('.msnbin')[0]
            return mission
    return ''


def update_current_mission(current_mission, mlg_output):
    '''
    update the current mission name
    '''
    mission = mission_file(mlg_output)
    if mission != '':
        current_mission = mission + '.Mission'
    return current_mission


def randomize_weather(mission):
    '''
    create randomised weather conditions and replace in the original file
    '''
    original_file = open(path_raw_missions + '\\' + mission, 'r').read()
    season = re.findall(r'SeasonPrefix = \"([^;]*)\";', original_file)[0]
    d_summer = make_random_mission_options(season)
    new_file = re.sub(r'CloudConfig = \"([^"]*)\";', 'CloudConfig = "{}";'.format(d_summer['CloudConfig']),
                      original_file)
    new_file = re.sub(r'CloudLevel = ([^;]*);', 'CloudLevel = {};'.format(d_summer['CloudLevel']), new_file)
    new_file = re.sub(r'SeaState = ([^;]*);', 'SeaState = {};'.format(d_summer['SeaState']), new_file)
    new_file = re.sub(r'Turbulence = ([^;]*);', 'Turbulence = {};'.format(d_summer['Turbulence']), new_file)
    new_file = re.sub(r'Pressure = ([^;]*);', 'Pressure = {};'.format(d_summer['Pressure']), new_file)
    new_file = re.sub(r'Haze = ([^;]*);', 'Haze = {};'.format(d_summer['Haze']), new_file)
    new_file = re.sub(r'Temperature = ([^;]*);', 'Temperature = {};'.format(d_summer['Temperature']), new_file)
    new_file = re.sub(r'PrecType = ([^;]*);', 'PrecType = {};'.format(d_summer['PrecType']), new_file)
    new_file = re.sub(r'PrecLevel = ([^;]*);', 'PrecLevel = {};'.format(d_summer['PrecLevel']), new_file)
    new_file = re.sub(r'WindLayers\s*\{([^\}^\{]*)}', string_wind_layer(d_summer['WindLayers']), new_file)
    # writing the new mission file to a temp.Mission file
    # output_path = path_raw_missions + '\\temp.Mission'
    with open(path_raw_missions + '\\' + mission, 'w') as f:
        f.write(new_file)


def msnbin_conversion(path_file_to_convert):
    subprocess.run([exe_resaver, "-d", path_data, "-f", path_file_to_convert], capture_output=True)


if __name__ == '__main__':

    current_mission = ''
    already_processed_mlg_logs = []
    logs = list_mlg_logs()
    for log in logs:
        mlg_output = parse_mlg(log)
        current_mission = update_current_mission(current_mission, mlg_output)
    clean_mlg_log()
    while True:
        print(current_mission)
        logs = list_mlg_logs()
        for log in logs:
            if not log in already_processed_mlg_logs:
                mlg_output = parse_mlg(log)
                current_mission = update_current_mission(current_mission, mlg_output)
                already_processed_mlg_logs.append(log)
                if check_if_mission_ended(mlg_output):
                    print('MISSION END: random weather script launched')
                    randomize_weather(current_mission)
                    path_temp_mission = path_raw_missions + '\\' + current_mission
                    msnbin_conversion(path_temp_mission)
                    path_temp_msnbin = path_raw_missions + '\\' + current_mission.split('.')[0] + '.msnbin'
                    path_final_msnbin = path_dogfight + '\\' + current_mission.split('.')[0] + '.msnbin'
                    shutil.move(path_temp_msnbin, path_final_msnbin)

        time.sleep(1)
    """

    TODO: check why the final .msnbin is not working. Try compiling diretly in the dogfight folder?