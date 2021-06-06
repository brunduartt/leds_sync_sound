import pyaudio
import wave
import os
import numpy as np
import requests
defaultframes = 512
import socket
class textcolors:
    if not os.name == 'nt':
        blue = '\033[94m'
        green = '\033[92m'
        warning = '\033[93m'
        fail = '\033[91m'
        end = '\033[0m'
    else:
        blue = ''
        green = ''
        warning = ''
        fail = ''
        end = ''

recorded_frames = []
device_info = {}
useloopback = False
recordtime = 5

#Use module
p = pyaudio.PyAudio()

#Set default to first in list or ask Windows
try:
    default_device_index = p.get_default_input_device_info()
except IOError:
    default_device_index = -1

#Select Device
print (textcolors.blue + "Available devices:\n" + textcolors.end)
for i in range(0, p.get_device_count()):
    info = p.get_device_info_by_index(i)
    print (textcolors.green + str(info["index"]) + textcolors.end + ": \t %s \n \t %s \n" % (info["name"], p.get_host_api_info_by_index(info["hostApi"])["name"]))

    if default_device_index == -1:
        default_device_index = info["index"]

#Handle no devices available
if default_device_index == -1:
    print (textcolors.fail + "No device available. Quitting." + textcolors.end)
    exit()


#Get input or default
device_id = int(input("Choose device [" + textcolors.blue + str(default_device_index) + textcolors.end + "]: ") or default_device_index)
print ("")

#Get device info
try:
    device_info = p.get_device_info_by_index(device_id)
except IOError:
    device_info = p.get_device_info_by_index(default_device_index)
    print (textcolors.warning + "Selection not available, using default." + textcolors.end)

#Choose between loopback or standard mode
is_input = device_info["maxInputChannels"] > 0
is_wasapi = (p.get_host_api_info_by_index(device_info["hostApi"])["name"]).find("WASAPI") != -1
if is_input:
    print (textcolors.blue + "Selection is input using standard mode.\n" + textcolors.end)
else:
    if is_wasapi:
        useloopback = True;
        print (textcolors.green + "Selection is output. Using loopback mode.\n" + textcolors.end)
    else:
        print (textcolors.fail + "Selection is input and does not support loopback mode. Quitting.\n" + textcolors.end)
        exit()

recordtime = int(input("Record time in seconds [" + textcolors.blue + str(recordtime) + textcolors.end + "]: ") or recordtime)

#Open stream
channelcount = device_info["maxInputChannels"] if (device_info["maxOutputChannels"] < device_info["maxInputChannels"]) else device_info["maxOutputChannels"]
selectedIndex = device_info["index"];
deviceRate = int(device_info["defaultSampleRate"])
framesPerBuffer = int(deviceRate/60)
stream = p.open(format = pyaudio.paInt16,
                channels = 1,
                rate = deviceRate,
                input = True,
                frames_per_buffer = framesPerBuffer,
                input_device_index = selectedIndex,
                as_loopback = useloopback)

#Start Recording
print (textcolors.blue + "Starting..." + textcolors.end)
oldValue = 0
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sensitivity = 45
for i in range(0, int(deviceRate / framesPerBuffer * recordtime)):
    readed = stream.read(defaultframes, exception_on_overflow = False)
    data = np.frombuffer(readed, dtype=np.int16)
    peak = np.max(np.abs(data)) * sensitivity
    v = (peak / 2 ** 16)
    if v > 1:
        v = 1
    pixels = int(255 * v)
    sock.sendto(bytes([pixels]), ("192.168.0.246", 7777))
    # url = 'http://192.168.0.246/soundReactive?value='+str(bars)
    # requests.post(url)


print (textcolors.blue + "End." + textcolors.end)
#Stop Recording

stream.stop_stream()
stream.close()

#Close module
p.terminate()