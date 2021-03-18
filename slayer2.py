import configparser
import datetime
import os
import re
import sys
import time
import warnings
import webbrowser
from random import randint
from threading import Thread

import keyboard
import pyttsx3
import pywinauto
import requests
import soundfile as sf
import speech_recognition as sr
from pywinauto.application import Application

app_settings = {'jabber_dump_path': 'C:\\Users\\jgrijalva\\JabberAudioDump\\',
                'log_calls': True,
                'new_leads_only': True,
                'user_name': '',
                'api_key': '',
                'app_uri': '',
                'call_list_tag': 'slayer'}

warnings.simplefilter('ignore', category=UserWarning)
sys.stdout = open("log.txt", "a+")

jabber_dump_path = 'C:\\Users\\jgrijalva\\JabberAudioDump\\'

LOG_CALLS = False
NEW_ONLY = False
CREATE_NOTES = True

USER_NAME = ''
API_KEY = ''
uri = ''
ASSIGNED_TO = ''
TAG = "slayer"
LOOPS = 44
TIME_1 = 31
TIME_2 = 55
NEXT_CALL_TIME_MAX = 3
URL = ''
QUERY = ''
MODEL = ''
SORTING = ''
TIMER_1 = randint(TIME_1, TIME_2)

WAVE_OUTPUT_FILENAME = "file.wav"
TARGET = 0
TOTAL_COUNT = 0
TOTAL_TIME = 0
JABBER_ALIVE = 0
WINDOW_ALIVE = 0
DEMO = False

# Initialize the recognizer
r = sr.Recognizer()


def read_raw_sound():
    # Read Jabber client
    _path = app_settings['jabber_dump_path']
    try:
        file = f'{_path}mOutToSpeaker.raw'

        data, sample_rate = sf.read(file, channels=1, samplerate=44100,
                                    subtype='FLOAT')

        sf.write('recording.wav', data, sample_rate)
    except RuntimeError as e:
        pp(e)


def speak_text(command):
    # Initialize the engine
    engine = pyttsx3.init()
    engine.say(command)
    engine.runAndWait()


# Loop infinitely for user to
# speak
def speech_to_text_baby():
    # Exception handling to handle
    # exceptions at the runtime
    try:

        # use the microphone as source for input.
        # with sr.Microphone() as source2:
        with sr.AudioFile('recording.wav') as source:
            audio = r.record(source)  # read the entire audio file

            # wait for a second to let the recognizer
            # adjust the energy threshold based on
            # the surrounding noise level
            # r.adjust_for_ambient_noise(source2, duration=0.2)

            # listens for the user's input
            # audio2 = r.listen(source2)

            # Using ggogle to recognize audio
            # MyText = r.recognize_google(audio2)
            MyText = r.recognize_google(audio)
            MyText = MyText.lower()

            pp(f'Speech2Text: {MyText}')
            return MyText
            # speak_text(MyText)

    except sr.RequestError as e:
        pp("Could not request results; {0}".format(e))

    except sr.UnknownValueError:
        pp("unknown error occured")


def clean_up_files():
    files = os.listdir(jabber_dump_path)
    for file in files:
        if '.raw' in file:
            os.remove(f'{jabber_dump_path}{file}')


def load_settings():
    config = configparser.ConfigParser()
    config.read('Config.ini')
    pp('Loading user settings...')
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


def set_history():
    config = configparser.ConfigParser()
    config.write('History.ini')
    # log('Loading user settings...')
    global TOTAL_COUNT
    config['HISTORY']['TOTAL_COUNT'] = TOTAL_COUNT + config['HISTORY']['TOTAL_COUNT']
    global TOTAL_TIME
    config['HISTORY']['TOTAL_TIME'] = TOTAL_TIME + config['HISTORY']['TOTAL_TIME']


def connect_to_jabber():
    pp('Looking for the Cisco Jabber window...')
    try:
        w_handle = pywinauto.findwindows.find_windows(title=u'Cisco Jabber', class_name='wcl_manager1', backend='uia')[
            0]
        pp('Success, the Cisco Jabber application was found...' + str(w_handle))
        pp('Connecting to Jabber...')
        app = Application().connect(handle=w_handle)
        pp(f'Jabber handle: {w_handle}')

    except IndexError as e:
        pp('Cisco Jabber window not found.  Try starting or restarting Cisco Jabber.')
        pp(e)


def call_window_active(window_title):
    n = str(window_title)
    n = str(re.sub("[^0-9]", "", n))
    # pp(n)
    try:

        w_handle = pywinauto.findwindows.find_windows(title=n, class_name='wcl_manager1', backend='uia')[0]
        app = Application().connect(handle=w_handle)
        call_dlg = app.top_window()
        actionable_dlg = call_dlg.wait("exists enabled visible ready")
        ids = call_dlg.pp_ctrl_ids

        # needs to sleep for 1 second for some reason.
        time.sleep(1)
        # SetForegroundWindow(call_dlg.wrapper_object())
        x = 1
        # pp('Must be on a call')
        return x

    except IndexError:
        x = 0
        # pp('Looking for the call window')
        time.sleep(1)
        return x

    # pwa_app = pywinauto.application.Application()
    # w_handle = pywinauto.findwindows.find_windows(title=u'89499392654', class_name='wcl_manager1')[0]


def request_tags_contacts(new_only=None):
    url = f'{uri}tags/{TAG}/X2Leads?_order=+lastActivity'
    # url = "http://54.149.103.44/index.php/api2/tags/" + TAG + "/Contacts?_order=+lastActivity"
    data = requests.get(url, auth=(USER_NAME, API_KEY)).json()

    # Trim out if NEW_ONLY True
    if NEW_ONLY:
        data = [person for person in data if person['phone'] and str(person['leadstatus']) == 'New']
    else:
        data = [person for person in data if person['phone']]

    # Trim call list
    data = data[:LOOPS]
    pp(f'{len(data)} leads in this call list. Thank you.')
    if new_only:
        data = [person for person in data if person['leadstatus'] == 'New']

    count = len(data)
    pp('Requesting your call list ...')
    pp('Downloading ' + str(count) + ' contacts')
    # log(data)
    return data


def mute(phone_number):
    n = clean_number(phone_number)
    t = 7
    x = 0
    while x < t:
        time.sleep(1)
        x += 1

        if not call_window_active(n):
            pp('(mute) - Cant find the call window...')
            break

    keyboard.send('ctrl+down')


def call(phone_number):
    pp('Dialing...' + phone_number)
    n = clean_number(phone_number)
    t = randint(TIME_1, TIME_2)
    pp(str(t))
    global TARGET
    TARGET = t
    x = 0
    # pp('Hanging up in... ' + str(t - x) + ' secs.')
    while x < t:
        time.sleep(1)
        x += 1
        # pp('Hanging up in... ' + str(t - x) + ' secs.')
        if not call_window_active(n):
            pp('Cant find the call window...')
            break
    # pp('Ending the call...')
    keyboard.send('ctrl+k')


def load_next_call():
    t = randint(3, NEXT_CALL_TIME_MAX)
    x = 0
    while x < t:
        time.sleep(1)
        x += 1
        # pp('Next call in...' + ' ' + str(t - x))


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


def current_time(as_int=True):
    if as_int:
        return int(time.time())
    else:
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def pp(msg):
    t = current_time(as_int=False)
    print(f'{t} {msg}')


def create_action(model, model_id, seconds):
    url = f'{uri}{model}/{model_id}/Actions'

    f1 = int(current_time() + seconds)
    f2 = int(f1 + 60)
    json_data = {
        'actionDescription': 'No answer.',
        'type': 'call',
        'assignedTo': '',
        'createDate': f2,
        'completeDate': f1,
        'completedBy': '',
        'updatedBy': '',
        'dueDate': current_time(as_int=True),
        "timeSpent": 0,
        "type": 'call'
    }
    pp(f'logging call')
    data = requests.post(url, auth=(USER_NAME, API_KEY), json=json_data).text
    return data


def update_lead_status(lead):
    lead_id = lead.get('id')
    url = f'{uri}X2Leads/{lead_id}.json'
    lead['leadstatus'] = 'Attempted Contact'
    data = requests.put(url, auth=(USER_NAME, API_KEY), json=lead).text
    return data


def create_note(model, model_id, message):
    url = f'{uri}{model}/{model_id}/Actions'
    f1 = int(current_time() + 60)
    f2 = int(f1 + 60)
    json_data = {
        'actionDescription': message,
        'type': 'note',
        'assignedTo': 'demobroker',
        'createDate': f2,
        'completeDate': f1,
        'completedBy': 'demobroker',
        'updatedBy': 'demobroker',
        'dueDate': current_time(),
        "timeSpent": 0
    }
    data = requests.post(url, auth=(USER_NAME, API_KEY), json=json_data).text
    return data


def call_workflow(data):
    start = time.time()
    counter = 1
    call_timer2 = 0
    fucked_up_calls = 0

    for item in data:
        start2 = time.time()
        name = item.get("name")
        pp(name)
        phone = item.get("phone")
        phone = clean_number(phone)
        c_id = item.get("id")
        if not DEMO:
            webbrowser.open('sip:' + phone)
            time.sleep(1.0)
            keyboard.send('enter')

            time.sleep(0.7)

        while call_window_active(phone):
            mute(clean_number(phone))
            call(clean_number(phone))
            load_next_call()

        end = time.time()
        call_timer = round((end - start) / 60, 2)
        call_timer2 = round((end - start2) / 60, 2)
        call_stats = [counter, name, phone, TARGET, call_timer2, call_timer, str(datetime.datetime.now())]

        read_raw_sound()
        transcribed_call = speech_to_text_baby()

        if LOG_CALLS:
            create_action('X2Leads', c_id, (call_timer2 * 60))

        if CREATE_NOTES and transcribed_call is not None:
            create_note('X2Leads', c_id, transcribed_call)
        update_lead_status(item)
        # with open(r'History.csv', 'a') as f:
        #     writer = csv.writer(f)
        #     writer.writerow(call_stats)
        pp(call_stats)
        # create_note('Contacts', c_id, note)
        if call_timer2 < 0.1:
            time.sleep(1.5)
            pp('Call was too short.  Hopefully a short break will correct this.')
            fucked_up_calls += 1
            pp(f'Fuck up call # {fucked_up_calls}')

        counter += 1
        if counter > LOOPS:
            sys.exit('Max loops...ending session')

        if fucked_up_calls > 3:
            sys.exit('Too many fucked up calls...aborting')

        if call_timer > 200:
            sys.exit('Too long of a session...aborting')


def main_loop():
    # data = request_tags_contacts()
    x = 0
    t = Thread(target=connect_to_jabber)
    t.start()
    x += 1
    time.sleep(1)

    data = request_tags_contacts(new_only=False)
    call_workflow(data)


if __name__ == '__main__':
    main_loop()
