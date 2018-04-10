import requests
from pywinauto.application import Application
import pyautogui
from random import randint
import pywinauto
import time
import webbrowser
import re
import sys
import configparser


DEBUG_MODE = True
USER_NAME = ' '
API_KEY = ' '
TAG = "slayer"
LOOPS = 0
RANDOM_1 = 0
RANDOM_2 = 0
URL = ''
QUERY = ''
MODEL = ''
SORTING = ''
TIME_1 = 25
TIME_2 = 65

TIMER_1 = 0


def load_settings():
    config = configparser.ConfigParser()
    config.read('Config.ini')
    log('Loading user settings...')
    global API_KEY
    API_KEY = config['DEFAULT']['API_KEY']
    global URL
    URL = config['DEFAULT']['URL']
    global QUERY
    QUERY = config['DEFAULT']['QUERY']
    global MODEL
    MODEL = config['DEFAULT']['MODEL']
    global SORTING
    SORTING = config['DEFAULT']['SORTING']
    global TIME_1
    SORTING = config['DEFAULT']['TIME_1']
    global TIME_2
    SORTING = config['DEFAULT']['TIME_2']
    global LOOPS
    LOOPS = config['DEFAULT']['LOOPS']
    global TIMER_1
    TIMER_1 = randint(TIME_1, TIME_2)


def connect_to_jabber():
    log('Looking for the Cisco Jabber window...')
    try:
        w_handle = pywinauto.findwindows.find_windows(title=u'Cisco Jabber', class_name='wcl_manager1')[0]
        log('Success, the Cisco Jabber application was found...' + str(w_handle))
        log('Connecting to Jabber...')
        app = Application().connect(handle=w_handle)
        dlg = app.PrintControlIdentifiers
        print(dlg)

    except IndexError:
        print('Cisco Jabber window not found.  Try starting or restarting Cisco Jabber.')



def call_window_active(window_title):
    n = str(window_title)
    n = re.sub("[^0-9]", "", n)
    try:

        w_handle = pywinauto.findwindows.find_windows(title=n, class_name='wcl_manager1')[0]
        app = Application().connect(handle=w_handle)
        call_dlg = app.top_window()
        actionable_dlg = call_dlg.wait("exists enabled visible ready")
        ids = call_dlg.print_ctrl_ids
        time.sleep(1)
        # SetForegroundWindow(call_dlg.wrapper_object())
        x = 1
        # print('Must be on a call')
        return x

    except IndexError:
        x = 0
        print('Looking for the call window')
        time.sleep(1)
        return x

    # pwa_app = pywinauto.application.Application()
    # w_handle = pywinauto.findwindows.find_windows(title=u'89499392654', class_name='wcl_manager1')[0]


def request_tags_contacts():
    url = "http://54.149.103.44/index.php/api2/tags/" + TAG + "/Contacts?_order=-name"
    data = requests.get(url, auth=(USER_NAME, API_KEY)).json()
    count = len(data)
    log('Requesting your call list ...')
    log('CALL SLAYER: Downloading ' + str(count) + ' contacts')
    # log(data)
    return data



def log(message):
    if DEBUG_MODE:
        print(message)
        return message


def mute(phone_number):
    n = clean_number(phone_number)
    t = 7.5
    x = 0
    while x < t:
        progress(x, t, 'Waiting to Mute')
        time.sleep(1)
        x += 1

        if not call_window_active(n):
            print('Cant find the call window...')
            break

    pyautogui.hotkey('ctrl', 'down')


def call(name, phone_number):
    print('Dialing...' + name)
    n = clean_number(phone_number)
    t = TIMER_1
    x = 0
    while x < t:
        time.sleep(1)
        x += 1
        print('Calling ' + str(t-x))

        if not call_window_active(n):
            print('Cant find the call window...')
            break

    pyautogui.hotkey('ctrl', 'k')


def load_next_call():
    t = randint(5, 15)
    x = 0
    while x < t:
        time.sleep(t)
        x += 1
        print('Next call in...' + ' ' + str(t-x))


def clean_number(phone_number):
    n = str(phone_number)
    n = re.sub("[^0-9]", "", n)
    return n


def progress(count, total, suffix=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', suffix))
    sys.stdout.flush()  # As suggested by Rom Ruben


def call_workflow(data):
    start = time.time()
    counter = 1
    call_timer2 = 0

    for item in data:
        start2 = time.time()
        name = item.get("name")
        phone = item.get("phone")
        log('CALL SLAYER: ' + str(counter) + '. ' + name + ' @ ' + str(clean_number(phone)))
        webbrowser.open('tel:' + phone)
        time.sleep(1.0)
        pyautogui.press('enter')
        time.sleep(0.3)
        while call_window_active(phone):
            mute(phone)
            call(name, phone)
            timer2 = randint(5, 15)
            time.sleep(timer2)
        end = time.time()
        call_timer = round(((end - start) / 60), 2)
        call_timer2 = round(((end - start2) / 60), 2)
        print('SUMMARY: ')
        print('Last call: ' + str(call_timer) + ' MINS')
        print('Session: ' + str(call_timer2) + 'MINS')
        counter += 1
        if counter > LOOPS:
            sys.exit('Max loops...ending session')


def main_loop():
    load_settings()
    connect_to_jabber()
    data = request_tags_contacts()
    call_workflow(data)

main_loop()