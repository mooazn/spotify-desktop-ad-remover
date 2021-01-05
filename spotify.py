import requests
import json
import subprocess
# import re - necessary if commented code is uncommented
import os
import signal
import pyautogui
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time
import win32process
import atexit
import win32con
import win32gui


"""
below is not necessary. you can simply put the location of Spotify inside the loc
variable if you don't want to run the below commands

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
"""

loc = 'Location of Spotify, i.e. -> C:\\Users\\name\\AppData\\Roaming\\Spotify'  # just use your file location if making .bat file

installer = ChromeDriverManager().install()
options = Options()
options.headless = True
driver = webdriver.Chrome(installer, options=options)
driver.get('https://accounts.spotify.com/en/login/')
driver.find_element_by_xpath('//*[@id="login-username"]').send_keys('email')
driver.find_element_by_xpath('//*[@id="login-password"]').send_keys('password')
driver.find_element_by_xpath('//*[@id="login-button"]').click()
time.sleep(3)


def windowEnumerationHandler(hwnd, top):
    top.append((hwnd, win32gui.GetWindowText(hwnd)))


def generate_new_token():
    print('Generating new token...')
    driver.get('https://developer.spotify.com/console/get-users-currently-playing-track/')
    driver.find_element_by_xpath('//*[@id="console-form"]/div[3]/div/span/button').click()
    time.sleep(3)
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
    except Exception as e:
        if str(e) == '\'currently_playing_type\'':
            print('Encountered error. Re-registering token.')
            headers['Authorization'] = 'Bearer ' + generate_new_token()
            new_token_registered = int(time.time())
        else:
            print('ERROR:', e)
        time.sleep(5)
        continue
    if not is_track:
        print('Reopening Spotify...')
        data = subprocess.check_output(['wmic', 'process', 'list', 'brief'])
        a = str(data).replace('b\'', '').replace('\'', '')
        a_ = a.split('\\r\\r\\n')
        p_ids = []
        for i in a_:
            if "Spotify.exe" in i:
                cur_line_parts = i.split()
                p_ids.append(cur_line_parts[3])
        for p_id in p_ids:
            os.kill(int(p_id), signal.SIGTERM)
        si = win32process.STARTUPINFO()
        si.dwFlags = win32con.STARTF_USESHOWWINDOW
        si.wShowWindow = win32con.SW_MAXIMIZE
        h_proc, h_thr, pid, tid = win32process.CreateProcess(None, loc + '\\Spotify.exe', None, None, False, 0, None, None, si)
        time.sleep(2)
        top_windows = []
        win32gui.EnumWindows(windowEnumerationHandler, top_windows)
        for i in top_windows:
            if i[1] == 'Spotify Free':
                shell = win32com.client.Dispatch("WScript.Shell")
                shell.SendKeys('%')
                win32gui.SetForegroundWindow(i[0])
                win32gui.ShowWindow(i[0], win32con.SW_MAXIMIZE)
                break
        pyautogui.sleep(1)
        pyautogui.press('space')
        pyautogui.sleep(1)
        pyautogui.getActiveWindow().minimize()
    else:
        print('Playing track...')
    if int(time.time()) - new_token_registered >= 3600:
        headers['Authorization'] = 'Bearer ' + generate_new_token()
        new_token_registered = int(time.time())
        continue
    time.sleep(10)


@atexit.register
def close_driver():
    driver.quit()
