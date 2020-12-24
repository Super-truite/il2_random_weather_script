import os
import time
import regex as re
import random
import numpy as np
import subprocess
import shutil
from mlg2txt_function2 import parse_mlg
import configparser


config = configparser.ConfigParser()
config.read('config.ini')



exe_resaver = config['DEFAULT']['exe_resaver']
path_data = config['DEFAULT']['path_data']
path_mlg = config['DEFAULT']['path_mlg']
path_raw_missions = config['DEFAULT']['path_raw_missions']
path_dogfight = config['DEFAULT']['path_dogfight']


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
  }}""".format(*[random_windlayer[k][l] for k in ['ground', '500', '1000', '2000', '5000'] for l in ['direction', 'speed']])
    return s


def make_random_mission_options(season):
    '''
    Creating random data for mission options
    '''
    clouds_type = random.choice(['00_clear', '01_light', '02_medium', '03_heavy', '04_overcast'])
    PrecType = 0
    PrecLevel = 0
    scale_wind = 5
    random_wind_direction = random.randint(0, 359)
    random_wind_directions = []
    for i in range(5):
        random_wind_directions.append(random_wind_direction)
        random_wind_direction = int(random_wind_direction + 5 * np.random.normal()) % 360
    if season == 'su':
        max_level = 3500
        if clouds_type == '04_overcast':
            PrecType = random.randint(0, 1)
            if PrecType == 1:
                PrecLevel = random.randint(0, 100)
                max_level = 1000
                scale_wind = 7
        random_wind = scale_wind * np.abs(np.random.normal())  # mean value: 7m/s, rarely above 49m/s
        random_winds = []
        for i in range(5):
            random_winds.append(random_wind)
            random_wind = random_wind + np.abs(np.random.normal())
        random_winds = ['%.2f' % rw for rw in random_winds]
        dict_options = {'Time': '{0}:0:0'.format(random.randint(6, 17)),
                    'CloudLevel': random.randint(500, max_level),
                    'CloudConfig': "summer\\\{0}_0{1}\\sky.ini".format(clouds_type, random.randint(0, 9)),
                    'SeaState': random.randint(0, 6),
                    'Turbulence': random.randint(0, 1),
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
    elif season == 'wi':
        max_level = 3500
        if clouds_type == '04_overcast':
            PrecType = random.randint(0, 1)
            if PrecType == 2:
                PrecLevel = random.randint(0, 100)
                max_level = 1000
                scale_wind = 10
        random_wind = 8 * np.abs(np.random.normal())  # mean value: 7m/s, rarely above 49m/s
        random_winds = []
        for i in range(5):
            random_winds.append(random_wind)
            random_wind = random_wind + np.abs(np.random.normal())
        random_winds = ['%.2f' % rw for rw in random_winds]
        dict_options = {'Time': '{0}:30:0'.format(random.randint(6, 17)),
                    'CloudLevel': random.randint(500, max_level),
                    'CloudConfig': "winter\\\{0}_0{1}\\sky.ini".format(clouds_type, random.randint(0, 9)),
                    'SeaState': random.randint(0, 6),
                    'Turbulence': random.randint(0, 1),
                    'Temperature': random.randint(-35, 10),
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
    else:
        raise ValueError
    return dict_options


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
            print('new mission: ', mission)
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
    dict_options = make_random_mission_options(season)
    new_file = re.sub(r'CloudConfig = \"([^"]*)\";', 'CloudConfig = "{}";'.format(dict_options['CloudConfig']), original_file)
    new_file = re.sub(r'CloudLevel = ([^;]*);', 'CloudLevel = {};'.format(dict_options['CloudLevel']), new_file)
    new_file = re.sub(r'SeaState = ([^;]*);', 'SeaState = {};'.format(dict_options['SeaState']), new_file)
    new_file = re.sub(r'Turbulence = ([^;]*);', 'Turbulence = {};'.format(dict_options['Turbulence']), new_file)
    new_file = re.sub(r'Pressure = ([^;]*);', 'Pressure = {};'.format(dict_options['Pressure']), new_file)
    new_file = re.sub(r'Haze = ([^;]*);', 'Haze = {};'.format(dict_options['Haze']), new_file)
    new_file = re.sub(r'Temperature = ([^;]*);', 'Temperature = {};'.format(dict_options['Temperature']), new_file)
    new_file = re.sub(r'PrecType = ([^;]*);', 'PrecType = {};'.format(dict_options['PrecType']), new_file)
    new_file = re.sub(r'PrecLevel = ([^;]*);', 'PrecLevel = {};'.format(dict_options['PrecLevel']), new_file)
    new_file = re.sub(r'WindLayers\s*\{([^\}^\{]*)}', string_wind_layer(dict_options['WindLayers']), new_file)
    new_file = re.sub(r'Time = ([^;]*);[\s\S]*Date', 'Time = {};\n  Date'.format(dict_options['Time']), new_file)
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
        logs = list_mlg_logs()
        for log in logs:
            if not log in already_processed_mlg_logs:
                mlg_output = parse_mlg(log)
                current_mission = update_current_mission(current_mission, mlg_output)
                already_processed_mlg_logs.append(log)
                if check_if_mission_ended(mlg_output):
                    print('MISSION END: random weather script launched')
                    randomize_weather(current_mission)
                    path_original_mission = path_raw_missions + '\\' + current_mission
                    path_temp_mission = path_dogfight + '\\' + current_mission
                    shutil.copy(path_original_mission, path_temp_mission)
                    msnbin_conversion(path_temp_mission)
                    os.remove(path_temp_mission)
                    for extension in ['.list', '.chs', '.eng', '.fra', '.ger', '.pol', '.rus', '.spa']:
                        f = path_raw_missions + '\\' + current_mission.split('.')[0] + extension
                        f2 = path_dogfight + '\\' + current_mission.split('.')[0] + extension
                        shutil.copy(f, f2)

        time.sleep(1)
