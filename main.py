import requests
import json
import subprocess
import re
import os
import signal
import pyautogui
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time
from ctypes import *

command = 'dir spotify.exe /s | findstr "Directory of .:[.]*"'
proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=None, shell=True, cwd='/')
out = proc.communicate()
loc_bad = str(out[0])
loc = re.search('.:\\\\', loc_bad)
loc = loc_bad[loc.start():].strip()
loc = loc[0:len(loc) - 5]
f = open('spotify_loc.txt', 'a')
f.write(loc)
f.close()
f = open('spotify_loc.txt', 'r')
loc = f.read()
f.close()
# loc = 'The Location Of Spotify'  # just use your file location if making .bat file, otherwise above is fine

installer = ChromeDriverManager().install()
options = Options()
options.headless = True
driver = webdriver.Chrome(installer, options=options)
driver.get('https://accounts.spotify.com/en/login/')
driver.find_element_by_xpath('//*[@id="login-username"]').send_keys('email')
driver.find_element_by_xpath('//*[@id="login-password"]').send_keys('password')
driver.find_element_by_xpath('//*[@id="login-button"]').click()
time.sleep(2)


def generate_new_token():
    print('Generating new token...')
    driver.get('https://developer.spotify.com/console/get-users-currently-playing-track/')
    driver.find_element_by_xpath('//*[@id="console-form"]/div[3]/div/span/button').click()
    time.sleep(2)
    driver.find_element_by_xpath('//*[@id="oauth-modal"]/div/div/div[2]/form/div[1]/div/div/div/div/label').click()
    driver.find_element_by_xpath('//*[@id="oauthRequestToken"]').click()
    token = driver.find_element_by_xpath('//*[@id="oauth-input"]').get_attribute('value')
    return token


headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': 'Bearer <token>'
}

if '<token>' in headers['Authorization']:
    headers['Authorization'] = 'Bearer ' + generate_new_token()

new_token_registered = int(time.time())

while True:
    print(headers['Authorization'])
    response = requests.get('https://api.spotify.com/v1/me/player/currently-playing', headers=headers)
    try:
        is_track = True if json.loads(response.text)['currently_playing_type'] == 'track' else False
    except KeyError:
        time.sleep(5)
        continue
    if not is_track:
        print('Reopening Spotify...')
        windll.user32.BlockInput(True)  # enable block
        data = subprocess.check_output(['wmic', 'process', 'list', 'brief'])
        a = str(data).replace('b\'', '').replace('\'', '')
        a_ = a.split('\\r\\r\\n')
        p_ids = []
        for i in a_:
            if "Spotify.exe" in i:
                cur_line = i
                cur_line_parts = cur_line.split(" ")
                fixed = []
                for j in range(len(cur_line_parts)):
                    if cur_line_parts[j] != '':
                        fixed.append(cur_line_parts[j])
                p_ids.append(fixed[3])

        for p_id in p_ids:
            os.kill(int(p_id), signal.SIGABRT)

        subprocess.Popen(loc + '\\Spotify.exe', cwd=loc, shell=True)
        pyautogui.sleep(7)
        windll.user32.BlockInput(False)  # disable block
        pyautogui.sleep(1)
        pyautogui.press('space')
        pyautogui.getActiveWindow().minimize()
    else:
        print('Playing track...')
    if int(time.time()) - new_token_registered >= 3600:
        headers['Authorization'] = 'Bearer ' + generate_new_token()
        new_token_registered = int(time.time())
        continue
    time.sleep(10)
