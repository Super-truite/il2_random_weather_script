import os 
import time
import re
import random
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

def create_random_wind_layer():
    random_windlayer = random.choice(random_windlayers)
    s = """
WindLayers 
{{
    0 :     {0} :     {1};
    500 :     {2} :     {3};
    1000 :     {4} :     {5};
    2000 :     {6} :     {7};
    5000 :     {8} :     {9};
}}""".format(*[random_windlayer[k][l] for l in ['direction', 'speed'] for k in ['ground', '500', '1000', '2000', '5000']])
    return s

def list_mlg_logs():
    l = []
    for file in os.listdir(path_mlg):
        if file.endswith(".mlg"):
            l.append(os.path.join(path_mlg, file))
    return l

def clean_mlg_log():
    for f in os.listdir(path_mlg):
        if f.endswith(".mlg"):
            try:
                os.remove(os.path.join(path_mlg, f))
            except OSError as e:
                #print(e)
                pass
            except:
                raise

def check_if_mission_ended(mlg_output):
    for output in mlg_output:
        if 'AType:7' in output:
            return True
    return False

def mission_file(mlg_output):
    for output in mlg_output:
        if 'MFile:' in output:
            mission = output.split('\\')[-1].split('.msnbin')[0]
            return mission
    return ''

def update_current_mission(current_mission, mlg_output):
        mission = mission_file(mlg_output)
        if mission != '':
            current_mission = mission + '.Mission'
        return current_mission

def extract_options(file_path):
    start, end = 0, 0
    count_brackets = 0
    with open(file_path, 'r') as f:
        for i, line in enumerate(f.readlines()):
            if ('Options' in line) and start==0:
                start = i
            if '}' in line:
                count_brackets +=1
                if count_brackets == 3:
                    end = i+1
                    break

    with open(file_path, 'r') as f:
        s = ''.join(f.readlines()[start:end])
        return s

def extract_simple_subrackets(lines):
    start, end = 0, 0
    count_brackets = 0
    for i, line in enumerate(lines):
        if ('{' in line) and start==0:
            start = i-1
        if '}' in line:
            end = i+1
            break
    return '\n'.join(lines[start:end])

def decompose_options(filepath):
    s_options = extract_options(filepath)
    s_options = s_options.replace(';', ',')
    s_options = s_options.replace('=', ':')
    extract1 = extract_simple_subrackets(s_options.split('\n')[2:-2])
    s_options = s_options.replace(extract1, '')
    extract2 = extract_simple_subrackets(s_options.split('\n')[2:-2])
    s_options = s_options.replace(extract2, '') 
    options = {"options": s_options, "WindLayers": extract1, "Countries": extract2} 
    return options

def randomize_weather(mission):
    original_file = open(path_raw_missions + '\\' + mission, 'r').read()
    

    s = create_random_wind_layer()
    # creating random windlayer 
    wind2 = create_random_wind_layer()
    # replace the WindLayers in the original mission file data by the random one
    pattern = r'WindLayers\s*\{([^\}^\{]*)}'
    new_file = re.sub(pattern, wind2 , original_file)
    #writing the new mission file to a temp.Mission file
    output_path = path_raw_missions + '\\temp.Mission'
    with open(output_path, 'w') as f:
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
                    path_temp_mission = path_raw_missions + '\\' + 'temp.Mission'
                    msnbin_conversion(path_temp_mission)
                    path_temp_msnbin = path_raw_missions + '\\' + 'temp.msnbin'
                    path_final_msnbin = path_dogfight + '\\' + current_mission.split('.')[0]+ '.msnbin'
                    shutil.move(path_temp_msnbin, path_final_msnbin)
                
        time.sleep(1)


 