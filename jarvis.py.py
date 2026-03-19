import socket
import time
import speech_recognition as sr
import pyttsx3
import subprocess
import webbrowser
import ctypes
import pygetwindow as gw
import pyautogui
import os
from typing import Optional
import ollama

# ---------------------- SETTINGS ----------------------
CHROME_PATH = "C:/Program Files/Google/Chrome/Application/chrome.exe"

# ---------------------- OLLAMA ----------------------
def chat_with_ollama(prompt):
    try:
        response = ollama.chat(
            model="mistral",
            messages=[
                {"role": "system", "content": "Reply in Hindi and English mix."},
                {"role": "user", "content": prompt}
            ]
        )
        return response['message']['content'].strip()
    except Exception as e:
        print("Ollama Error:", e)
        return "Mujhe jawab dene me problem ho rahi hai."

# ---------------------- INTERNET ----------------------
def check_internet():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except:
        return False

def wait_for_internet():
    print("Checking internet...")
    while not check_internet():
        print("Waiting for internet...")
        time.sleep(3)

# ---------------------- VOICE ----------------------
recognizer = sr.Recognizer()
engine = pyttsx3.init()
engine.setProperty('rate', 165)

voices = engine.getProperty('voices')
if voices:
    engine.setProperty('voice', voices[0].id)

def speak(text):
    print("Chaman:", text)
    try:
        engine.stop()
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print("TTS Error:", e)

# ---------------------- MICROPHONE SAFE INIT ----------------------
try:
    mic = sr.Microphone()
    print("Mic initialized ✅")
except Exception as e:
    print("Mic Error:", e)
    speak("Microphone detect nahi ho raha.")
    exit()

with mic as source:
    recognizer.adjust_for_ambient_noise(source, duration=1)

# ---------------------- LISTEN ----------------------
def listen() -> Optional[str]:
    with mic as source:
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=6)
            text = recognizer.recognize_google(audio)
            print("You:", text)
            return text.lower()
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            print("Samaj nahi aaya")
            return None
        except Exception as e:
            print("Listen Error:", e)
            return None

def listen_wake_word():
    with mic as source:
        try:
            audio = recognizer.listen(source, timeout=3, phrase_time_limit=3)
            text = recognizer.recognize_google(audio)
            return "chaman" in text.lower()
        except:
            return False

# ---------------------- UTIL ----------------------
def open_chrome(url):
    try:
        if os.path.exists(CHROME_PATH):
            subprocess.Popen([CHROME_PATH, url])
        else:
            webbrowser.open(url)
    except Exception as e:
        print("Chrome Error:", e)

def open_app(path, name):
    try:
        subprocess.Popen(path)
        speak(f"{name} open kar raha hoon.")
    except Exception as e:
        print("App Error:", e)
        speak(f"{name} open nahi ho raha.")

# ---------------------- COMMAND HANDLER ----------------------
def handle_command(cmd):
    print("Command:", cmd)

    if any(x in cmd for x in ["exit", "stop", "close"]):
        speak("Command mode band.")
        return "exit"

    elif "notepad" in cmd:
        open_app("notepad.exe", "Notepad")

    elif "calculator" in cmd:
        open_app("calc.exe", "Calculator")

    elif "chrome" in cmd:
        open_chrome("https://google.com")
        speak("Chrome open kar diya.")

    elif "youtube" in cmd:
        open_chrome("https://youtube.com")
        speak("YouTube open.")

    elif "explorer" in cmd:
        open_app("explorer.exe", "File Explorer")

    elif "cmd" in cmd:
        open_app("cmd.exe", "Command Prompt")

    elif "shutdown" in cmd:
        speak("System shutdown ho raha hai.")
        os.system("shutdown /s /t 5")

    elif "restart" in cmd:
        speak("Restart kar raha hoon.")
        os.system("shutdown /r /t 5")

    elif "lock" in cmd:
        speak("System lock kar raha hoon.")
        ctypes.windll.user32.LockWorkStation()

    elif "close window" in cmd:
        win = gw.getActiveWindow()
        if win:
            win.close()
            speak("Window close kiya.")
        else:
            speak("Koi window active nahi hai.")

    elif "minimize" in cmd:
        win = gw.getActiveWindow()
        if win:
            win.minimize()
            speak("Window minimize.")

    elif "maximize" in cmd:
        win = gw.getActiveWindow()
        if win:
            win.maximize()
            speak("Window maximize.")

    elif "volume up" in cmd:
        pyautogui.press("volumeup", presses=5)
        speak("Volume badhaya.")

    elif "volume down" in cmd:
        pyautogui.press("volumedown", presses=5)
        speak("Volume kam kiya.")

    elif "mute" in cmd:
        pyautogui.press("volumemute")
        speak("Mute kar diya.")

    elif "screenshot" in cmd:
        path = os.path.join(os.environ["USERPROFILE"], "Pictures", "shot.png")
        pyautogui.screenshot().save(path)
        speak("Screenshot save ho gaya.")

    elif "play song" in cmd or "play music" in cmd:
        speak("Konsa gana?")
        song = listen()
        if song:
            url = f"https://youtube.com/results?search_query={song}"
            open_chrome(url)
            speak(f"{song} search kar diya.")

    elif "gpt" in cmd:
        speak("GPT mode start. Exit bolke band karo.")

        while True:
            user = listen()

            if user is None:
                speak("Dobara bolo.")
                continue

            if "exit" in user:
                speak("GPT mode band.")
                break

            reply = chat_with_ollama(user)
            speak(reply)

    else:
        speak("Samaj nahi aaya.")

    return None

# ---------------------- MAIN ----------------------
if __name__ == "__main__":
    wait_for_internet()
    speak("Hello Nilesh, Chaman 2.0 ready hai.")

    command_mode = False

    while True:
        if not command_mode:
            if listen_wake_word():
                speak("Yes boss, bolo.")
                command_mode = True

        if command_mode:
            cmd = listen()
            if cmd:
                result = handle_command(cmd)
                if result == "exit":
                    command_mode = False