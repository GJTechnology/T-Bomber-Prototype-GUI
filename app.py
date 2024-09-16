import os
import shutil
import sys
import subprocess
import string
import random
import json
import re
import time
import argparse
import zipfile
from io import BytesIO
from flask import Flask, render_template, request, redirect
import webbrowser
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from utils.decorators import MessageDecorator
from utils.provider import APIProvider

try:
    import requests
    from colorama import Fore, Style
except ImportError:
    print("\tSome dependencies could not be imported (possibly not installed)")
    print(
        "Type `pip3 install -r requirements.txt` to "
        " install all required packages")
    sys.exit(1)

mesgdcrt = MessageDecorator("icon")
__CONTRIBUTORS__ = ['GJ Technologies', 'Jatin Yadav', 'Gabbar Singh']

ALL_COLORS = [Fore.GREEN, Fore.RED, Fore.YELLOW, Fore.BLUE,
              Fore.MAGENTA, Fore.CYAN, Fore.WHITE]
RESET_ALL = Style.RESET_ALL

ASCII_MODE = False
DEBUG_MODE = False

description = """TBomb - Your Friendly Spammer Application

TBomb can be used for many purposes which incudes -
\t Exposing the vulnerable APIs over Internet
\t Friendly Spamming
\t Testing Your Spam Detector and more ....

TBomb is not intented for malicious uses.
"""

results = {
    'su': 0,
    'fa': 0,
    'requested': 0
}

first_data = {
    'apiv': 0,
    'c': 0,
    'tar': 0,
    'cou': 0,
    'de': 0,
    'ma': 0
}

thread_run = False
process_completed = False 

app = Flask(__name__)
def open_browser():
    # Wait for 2 seconds to ensure the Flask server has started
    time.sleep(2)
    webbrowser.open_new('http://127.0.0.1:5000/')

def readisdc():
    with open("isdcodes.json") as file:
        isdcodes = json.load(file)
    return isdcodes

def get_version():
    try:
        return open(".version", "r").read().strip()
    except Exception:
        return '1.0'
    
__VERSION__ = get_version()

def clr():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")

def bann_text():
    clr()
    logo = """
   ████████ █████                 ██
   ▒▒▒██▒▒▒ ██▒▒██                ██
      ██    ██  ██        ██   ██ ██
      ██    █████▒  ████  ███ ███ █████
      ██    ██▒▒██ ██  ██ ██▒█▒██ ██▒▒██
      ██    ██  ██ ██  ██ ██ ▒ ██ ██  ██
      ██    █████▒ ▒████▒ ██   ██ █████▒
      ▒▒    ▒▒▒▒▒   ▒▒▒▒  ▒▒   ▒▒ ▒▒▒▒▒
                                         """
    if ASCII_MODE:
        logo = ""
    version = "Version: "+__VERSION__
    contributors = "Contributors: "+" ".join(__CONTRIBUTORS__)
    print(random.choice(ALL_COLORS) + logo + RESET_ALL)
    mesgdcrt.SuccessMessage(version)
    mesgdcrt.SectionMessage(contributors)
    print()

def check_intr():
    try:
        requests.get("https://motherfuckingwebsite.com")
    except Exception:
        bann_text()
        mesgdcrt.FailureMessage("Poor internet connection detected")
        sys.exit(2)

def format_phone(num):
    num = [n for n in num if n in string.digits]
    return ''.join(num).strip()

def do_zip_update():
    success = False
    if DEBUG_MODE:
        zip_url = "https://github.com/TheSpeedX/TBomb/archive/dev.zip"
        dir_name = "TBomb-dev"
    else:
        zip_url = "https://github.com/TheSpeedX/TBomb/archive/master.zip"
        dir_name = "TBomb-master"
    print(ALL_COLORS[0]+"Downloading ZIP ... "+RESET_ALL)
    response = requests.get(zip_url)
    if response.status_code == 200:
        zip_content = response.content
        try:
            with zipfile.ZipFile(BytesIO(zip_content)) as zip_file:
                for member in zip_file.namelist():
                    filename = os.path.split(member)
                    if not filename[1]:
                        continue
                    new_filename = os.path.join(
                        filename[0].replace(dir_name, "."),
                        filename[1])
                    source = zip_file.open(member)
                    target = open(new_filename, "wb")
                    with source, target:
                        shutil.copyfileobj(source, target)
            success = True
        except Exception:
            mesgdcrt.FailureMessage("Error occured while extracting !!")
    if success:
        mesgdcrt.SuccessMessage("TBomb was updated to the latest version")
        mesgdcrt.GeneralMessage(
            "Please run the script again to load the latest version")
    else:
        mesgdcrt.FailureMessage("Unable to update TBomb.")
        mesgdcrt.WarningMessage(
            "Grab The Latest one From GJ technologies")

    sys.exit()

def do_git_update():
    success = False
    try:
        print(ALL_COLORS[0]+"UPDATING "+RESET_ALL, end='')
        process = subprocess.Popen("git checkout . && git pull ",
                                   shell=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
        while process:
            print(ALL_COLORS[0]+'.'+RESET_ALL, end='')
            time.sleep(1)
            returncode = process.poll()
            if returncode is not None:
                break
        success = not process.returncode
    except Exception:
        success = False
    print("\n")

    if success:
        mesgdcrt.SuccessMessage("TBomb was updated to the latest version")
        mesgdcrt.GeneralMessage(
            "Please run the script again to load the latest version")
    else:
        mesgdcrt.FailureMessage("Unable to update TBomb.")
        mesgdcrt.WarningMessage("Make Sure To Install 'git' ")
        mesgdcrt.GeneralMessage("Then run command:")
        print(
            "git checkout . && "
            "git pull GJ Technologies HEAD")
    sys.exit()

def update():
    if shutil.which('git'):
        do_git_update()
    else:
        do_zip_update()

def check_for_updates():
    if DEBUG_MODE:
        mesgdcrt.WarningMessage(
            "DEBUG MODE Enabled! Auto-Update check is disabled.")
        return
    mesgdcrt.SectionMessage("Checking for updates")
    fver = requests.get(
        "https://raw.githubusercontent.com/TheSpeedX/TBomb/master/.version"
    ).text.strip()
    if fver != __VERSION__:
        mesgdcrt.WarningMessage("An update is available")
        mesgdcrt.GeneralMessage("Starting update...")
        update()
    else:
        mesgdcrt.SuccessMessage("TBomb is up-to-date")
        mesgdcrt.GeneralMessage("Starting TBomb")

def notifyen():
    try:
        if DEBUG_MODE:
            url = "https://github.com/TheSpeedX/TBomb/raw/dev/.notify"
        else:
            url = "https://github.com/TheSpeedX/TBomb/raw/master/.notify"
        noti = requests.get(url).text.upper()
        if len(noti) > 10:
            mesgdcrt.SectionMessage("NOTIFICATION: " + noti)
            print()
    except Exception:
        pass

def get_phone_info(code, number, times, second):
    while True:
        target = ""
        cc = code
        cc = format_phone(cc)
        if not country_codes.get(cc, False):
            mesgdcrt.WarningMessage(
                "The country code ({cc}) that you have entered"
                " is invalid or unsupported".format(cc=cc))
            continue
        target = number
        target = format_phone(target)
        if ((len(target) <= 6) or (len(target) >= 12)):
            mesgdcrt.WarningMessage(
                "The phone number ({target})".format(target=target) +
                "that you have entered is invalid")
            continue
        return (cc, target, times, second)

def get_mail_info(mail, times, sec):
    mail_regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    while True:
        target = mail
        if not re.search(mail_regex, target, re.IGNORECASE):
            mesgdcrt.WarningMessage(
                "The mail ({target})".format(target=target) +
                " that you have entered is invalid")
            continue
        return (target, times, sec)

def pretty_print(cc, target, success, failed):
    global results
    requested = success+failed
    results.update({
        'su': success,
        'fa': failed,
        'requested': requested
    })
    mesgdcrt.SectionMessage("Bombing is in progress - Please be patient")
    mesgdcrt.GeneralMessage(
        "Please stay connected to the internet during bombing")
    mesgdcrt.GeneralMessage("Target       : " + cc + " " + target)
    mesgdcrt.GeneralMessage("Sent         : " + str(requested))
    mesgdcrt.GeneralMessage("Successful   : " + str(success))
    mesgdcrt.GeneralMessage("Failed       : " + str(failed))
    mesgdcrt.WarningMessage(
        "This tool was made for fun and research purposes only")
    mesgdcrt.SuccessMessage("TBomb was created by GJ Technologies")

def workernode(mode, cc, target, count, delay, max_threads):

    global first_data
    api = APIProvider(cc, target, mode, delay=delay)
    apiv = api.api_version
    first_data.update({
        'apiv': apiv,
        'c': cc,
        'tar': target,
        'cou': count,
        'de': delay,
        'ma': max_threads,
    })
    clr()
    mesgdcrt.SectionMessage("Gearing up the Bomber - Please be patient")
    mesgdcrt.GeneralMessage(
        "Please stay connected to the internet during bombing")
    mesgdcrt.GeneralMessage("API Version   : " + apiv)
    mesgdcrt.GeneralMessage("Target        : " + cc + target)
    mesgdcrt.GeneralMessage("Amount        : " + str(count))
    mesgdcrt.GeneralMessage("Threads       : " + str(max_threads) + " threads")
    mesgdcrt.GeneralMessage("Delay         : " + str(delay) +
                            " seconds")
    mesgdcrt.WarningMessage(
        "This tool was made for fun and research purposes only")
    print()

    if len(APIProvider.api_providers) == 0:
        mesgdcrt.FailureMessage("Your country/target is not supported yet")
        mesgdcrt.GeneralMessage("Feel free to reach out to us")
        input(mesgdcrt.CommandMessage("Press [ENTER] to exit"))
        bann_text()
        sys.exit()

    success, failed = 0, 0
    while success < count:
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            jobs = []
            for i in range(count-success):
                jobs.append(executor.submit(api.hit))

            for job in as_completed(jobs):
                result = job.result()
                if result is None:
                    mesgdcrt.FailureMessage(
                        "Bombing limit for your target has been reached")
                    mesgdcrt.GeneralMessage("Try Again Later !!")
                    input(mesgdcrt.CommandMessage("Press [ENTER] to exit"))
                    bann_text()
                    sys.exit()
                if result:
                    success += 1
                else:
                    failed += 1
                clr()
                pretty_print(cc, target, success, failed)
    print("\n")
    mesgdcrt.SuccessMessage("Bombing completed!")

def selectnode(cd, tn, t, se, mode):
    
    mode = mode.lower().strip()
    try:
        clr()
        bann_text()
        check_intr()
        check_for_updates()
        notifyen()
        max_limit = {"sms": 500, "call": 15, "mail": 200}
        cc, target, times, sec = "", "", "", ""
        if mode in ["sms", "call"]:
            cc, target, times, sec = get_phone_info(cd, tn, t, se)
            if cc != "91":
                max_limit.update({"sms": 100})
        elif mode == "mail":
            target, times, sec = get_mail_info(tn, t, se)

            
        else:
            raise KeyboardInterrupt

        limit = max_limit[mode]
        while True:
            try:
                count = int(times.strip())
                if count > limit or count == 0:
                    mesgdcrt.WarningMessage("You have requested " + str(count)
                                            + " {type}".format(
                                                type=mode.upper()))
                    mesgdcrt.GeneralMessage(
                        "Automatically capping the value"
                        " to {limit}".format(limit=limit))
                    count = limit
                delay = float(sec.strip())
                # delay = 0
                max_thread_limit = (count//10) if (count//10) > 0 else 1
                max_threads = max_thread_limit
                max_threads = max_threads if (
                    max_threads > 0) else max_thread_limit
                if (count < 0 or delay < 0):
                    raise Exception
                break
            except KeyboardInterrupt as ki:
                raise ki
            except Exception:
                mesgdcrt.FailureMessage("Read Instructions Carefully !!!")
                print()
            break

        workernode(mode, cc, target, count, delay, max_threads)
    except KeyboardInterrupt:
        mesgdcrt.WarningMessage("Received INTR call - Exiting...")
        sys.exit()

if sys.version_info[0] != 3:
    mesgdcrt.FailureMessage("TBomb will work only in Python v3")
    sys.exit()

try:
    country_codes = readisdc()["isdcodes"]
except FileNotFoundError:
    update()

parser = argparse.ArgumentParser(description=description,
                                 epilog='Coded by GJ Technologies !!!')
parser.add_argument("-c", "--contributors", action="store_true",
                    help="show current TBomb contributors")
parser.add_argument("-v", "--version", action="store_true",
                    help="show current TBomb version")

@app.route('/')
def gui():
    return render_template('home.html')

@app.route('/handle_form', methods=['POST'])
def handle_form():
    try:
        global type_of_bomb
        type_of_bomb = request.form.get('type').lower()
        if type_of_bomb in ["sms", "call", "mail"]:
            return render_template(f'{type_of_bomb}.html')
        else:
            return "Invalid bomb type selected!", 400
    except Exception as e:
        return str(e), 500

@app.route('/process_sms', methods=['POST'])
def process_sms():
    try:
        # Get form data
        global code_sms, number_sms, times_sms, second_sms
        code_sms = request.form.get('Country Code')
        number_sms = request.form.get('Target Number')
        times_sms = request.form.get('Times')
        second_sms = request.form.get('second')
        
        # Validate all fields are provided
        if not all([code_sms, number_sms, times_sms, second_sms]):
            return redirect('/handle_form')
        
        # Pass values to the next route or function
        return redirect('/working_gui')
    except Exception as e:
        return str(e), 500

@app.route('/process_call', methods=['POST'])
def process_call():
    try:
        # Get form data
        global code_call, number_call, times_call, second_call
        code_call = request.form.get('Country Code')
        number_call = request.form.get('Target Number')
        times_call = request.form.get('Times')
        second_call = request.form.get('second')
        
        # Validate all fields are provided
        if not all([code_call, number_call, times_call, second_call]):
            return redirect('/handle_form')
        
        return redirect('/working_gui')
    except Exception as e:
        return str(e), 500

@app.route('/process_mail', methods=['POST'])
def process_mail():
    try:
        # Get form data
        global code_mail, mail, times_mail, second_mail
        code_mail = 0
        mail = request.form.get('Target Email')
        times_mail = request.form.get('Times')
        second_mail = request.form.get('second')
        
        # Validate all fields are provided
        if not all([mail, times_mail, second_mail]):
            return redirect('/handle_form')
        return redirect('/working_gui')
    except Exception as e:
        return str(e), 500

@app.route('/working_gui', methods=['GET'])
def working_gui():
    global thread_run, process_completed

    if process_completed:  # If the process is already done, show the completion page
        return render_template('final.html', **first_data, **results)

    if not thread_run:
        bomb_type = type_of_bomb
        thread_run = True  # Set the flag to prevent multiple runs

        # Start the thread and run the bombing logic asynchronously
        threading.Thread(target=run_bomb_process, args=(bomb_type,)).start()
        return render_template('try.html', **first_data, **results)  # Show progress page
    else:
        # Skip starting a new thread if one is already running
        print("Thread has already been run. Skipping.")
        return render_template('try.html', **first_data, **results)

def run_bomb_process(bomb_type):
    global process_completed

    if bomb_type == "sms":
        selectnode(code_sms, number_sms, times_sms, second_sms, bomb_type)
    elif bomb_type == "call":
        selectnode(code_call, number_call, times_call, second_call, bomb_type)
    elif bomb_type == "mail":
        selectnode(code_mail, mail, times_mail, second_mail, bomb_type)

    process_completed = True  # Mark the process as completed


@app.route('/home')
def home():
    global thread_run, process_completed, results, first_data
    thread_run = False
    process_completed = False 
    results.update({
        'su': 0,
        'fa': 0,
        'requested': 0
    })

    first_data.update({
        'apiv': 0,
        'c': 0,
        'tar': 0,
        'cou': 0,
        'de': 0,
        'ma': 0
    })
    return render_template('home.html')
    
if __name__ == "__main__":
    try:
        open_browser()  # Open browser before running Flask server
        app.run(debug=False, use_reloader=False)
        args = parser.parse_args()
        if args.version:
            print("Version: ", __VERSION__)
        elif args.contributors:
            print("Contributors: ", " ".join(__CONTRIBUTORS__))
    except KeyboardInterrupt:
        sys.exit()
