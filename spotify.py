import requests
import json
import subprocess
import os
import signal
import pyautogui
from selenium.webdriver.chrome.options import Options
import time
import win32process
import atexit
import win32con
import win32gui
import win32com.client
import undetected_chromedriver as uc
# import re - necessary if commented code below is uncommented

"""
below is not necessary. you can simply put the location of Spotify inside the loc
variable if you don't want to run the below commands. if you do run below, it is only
meant to be run ONCE since result is stored in a file. once ran, it can be commented
again (except for the file reading part which reads the location into a variable).

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
    # driver stays active while script is running (faster since you don't have to keep logging in each time)
    return token


SPOTIFY_OPENED_SCREEN_WIDTH = pyautogui.size().width  # width of screen where Spotify was opened.

loc = 'C:\\Users\\USERNAME\\AppData\\Roaming\\Spotify'  # location of where Spotify is stored.

options = Options()
options.add_argument('log-level=3')
options.add_argument('window-size=1920x1080')  # this helps with headless browser
# options.headless = True
driver = uc.Chrome(options=options)
driver.get('https://www.spotify.com/us/')
driver.implicitly_wait(5)
driver.find_element_by_xpath('//*[@id="__next"]/div[1]/header/div/nav/ul/li[6]/a').click()
driver.implicitly_wait(2)
driver.find_element_by_xpath('//*[@id="app"]/body/div[1]/div[2]/div/div[2]/div/a').click()
driver.implicitly_wait(2)
driver.find_element_by_xpath('//*[@id="email"]').send_keys('email')  # facebook email
driver.find_element_by_xpath('//*[@id="pass"]').send_keys('password')  # facebook password
driver.find_element_by_xpath('//*[@id="loginbutton"]').click()
time.sleep(3)

headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': 'Bearer <token>'
}

if '<token>' in headers['Authorization']:  # first time generation
    headers['Authorization'] = 'Bearer ' + generate_new_token()

new_token_registered = int(time.time())
song_id = ''

while True:  # this can be replaced with a check to see if Spotify is running
    print(headers['Authorization'])
    response = requests.get('https://api.spotify.com/v1/me/player/currently-playing', headers=headers)
    try:
        is_track = True if json.loads(response.text)['currently_playing_type'] == 'track' else False
        if is_track:
            song_id = json.loads(response.text)['item']['id']
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
        cur = None
        if pyautogui.position().x > SPOTIFY_OPENED_SCREEN_WIDTH:  # this is a biggggggg assumption. doesn't even matter if you're only on local machine.
            cur = pyautogui.position()  # so we can move cursor back to where it was
            pyautogui.moveTo(0, 200)  # should be adjusted based on screen (this assumes 1 monitor on right side)
            pyautogui.click()
        data = subprocess.check_output(['wmic', 'process', 'list', 'brief'])
        a = str(data).replace('b\'', '').replace('\'', '')
        a_ = a.split('\\r\\r\\n')
        p_ids = []
        for i in a_:
            if "Spotify.exe" in i:
                cur_line_parts = i.split()
                p_ids.append(cur_line_parts[3])
        for p_id in p_ids:
            os.kill(int(p_id), signal.SIGTERM)  # nice
        win32process.CreateProcess(None, loc + '\\Spotify.exe', None, None, False, 0, None, None,
                                   win32process.STARTUPINFO())
        time.sleep(2)
        # ------ start code that is really helpful and mostly from SO
        # https://stackoverflow.com/questions/54918333/how-to-maximize-an-inactive-window - cosminm's post
        top_windows = []
        win32gui.EnumWindows(windowEnumerationHandler, top_windows)
        for i in top_windows:
            if i[1] == 'Spotify Free':  # this is the title of the Spotify window when nothing is playing
                shell = win32com.client.Dispatch("WScript.Shell")
                shell.SendKeys('%')
                # why do above 2 lines work? found it here: https://stackoverflow.com/questions/14295337/win32gui-setactivewindow-error-the-specified-procedure-could-not-be-found
                time.sleep(1)
                win32gui.SetForegroundWindow(i[0])
                time.sleep(0.4)
                win32gui.ShowWindow(i[0], win32con.SW_MAXIMIZE)
                break
        # ------ end code that is really helpful and mostly from SO
        pyautogui.sleep(1)
        pyautogui.press('space')
        pyautogui.sleep(1)
        try:  # an extra try catch. isn't necessary to automatically skip track if program is crashing. can be manually skipped in such a case.
            if int(
                    time.time()) - new_token_registered >= 3500:  # in the rare case that the token expires while checking for repeat
                headers['Authorization'] = 'Bearer ' + generate_new_token()
                new_token_registered = int(time.time())
            new_response = requests.get('https://api.spotify.com/v1/me/player/currently-playing', headers=headers)
            is_new_thing_track = True if json.loads(new_response.text)['currently_playing_type'] == 'track' else False
            if is_new_thing_track:
                new_song_id = json.loads(new_response.text)['item']['id']
                if str(song_id) == str(
                        new_song_id):  # if the song is the same as the one that was playing before the ad, skip it (ctrl + right) is the shortcut
                    print('Skipping song...')
                    pyautogui.keyDown('ctrl')
                    pyautogui.sleep(0.2)
                    pyautogui.press('right')
                    pyautogui.sleep(0.2)
                    pyautogui.keyUp('ctrl')
                    pyautogui.sleep(0.1)
            pyautogui.getActiveWindow().minimize()
            if cur is not None:
                pyautogui.moveTo(cur.x, cur.y)  # move cursor to where it was
        except Exception as e:
            pyautogui.getActiveWindow().minimize()  # minimize just in case the program crashes in the try (since track is already playing)
            if cur is not None:  # move cursor back to the other screen just in case the program crashes
                pyautogui.moveTo(cur.x, cur.y)
            print('ERROR:', e)
            time.sleep(5)
            continue
    else:
        print('Playing track...')
    if int(time.time()) - new_token_registered >= 3500:
        headers['Authorization'] = 'Bearer ' + generate_new_token()
        new_token_registered = int(time.time())
        continue
    time.sleep(5)  # send the req every 5 secondssss


@atexit.register
def close_driver():
    driver.close()
    driver.quit()  # close
