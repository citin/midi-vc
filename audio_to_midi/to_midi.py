import aubio
import numpy as num
import pyaudio
import wave
import mido

from mido import Message
from time import sleep
from threading import Thread

# todo: read from file and GUI
#### SETTINGS ####

# General Settings #
MIDI_DEVICE_NAME = 'AndresVirtualInstrument' 

# Aubio Settings #
AUBIO_METHOD      = "default"
AUBIO_BUFFER_SIZE = 2048
AUBIO_HOP_SIZE    = 2048//2
AUBIO_SAMPLE_RATE = 44100
AUBIO_UNIT        = "midi"
AUBIO_SILENCE     = -40
AUBIO_TOLERANCE   = 0.9

#####################

print("<<< Welcome to Midi Virtual Device >>>")
print("\n")

# Select Audio Device

print("Input Audio Device List:")
# get input devices
p = pyaudio.PyAudio()
info = p.get_host_api_info_by_index(0)
numdevices = info.get('deviceCount')

# show devices listfor i in range(0, numdevices):
for i in range(0, numdevices):
    if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
        print("(input) id: ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'))
print("\n")

# Read selected
try:
    mode=int(input('Please, select audio device by id: '))
except ValueError:
    print("Not a number")

# Create Virtual Midi Output Instrument
outport = mido.open_output(MIDI_DEVICE_NAME, virtual=True)

# Open stream.
stream = p.open(
    format=pyaudio.paFloat32,
    channels=1,
    rate=44100, 
    input=True,
    frames_per_buffer=1024, 
    input_device_index=int(mode))

# Aubio's pitch detection.
# methods: default|yinfft|yin|mcomb|fcomb|schmitt
pDetection = aubio.pitch(
    AUBIO_METHOD,
    AUBIO_BUFFER_SIZE,
    AUBIO_HOP_SIZE,
    AUBIO_SAMPLE_RATE)

# Set unit.
pDetection.set_unit(AUBIO_UNIT)
pDetection.set_silence(AUBIO_SILENCE)
pDetection.set_tolerance(AUBIO_TOLERANCE)

def stop_note_async(x, y):
    # sleep(1)
    outport.send(Message('note_off', note=int(x), velocity=int(y)))

def read_note():
    data = stream.read(1024, exception_on_overflow=False)
    samples = num.fromstring(data,
        dtype=aubio.float_type)
    pitch = pDetection(samples)[0]

    # Compute the energy (volume) of the
    # current frame.
    volume = num.sum(samples**2)/len(samples)
    # Format the volume output so that at most
    # it has six decimal numbers.
    volume = "{:.6f}".format(volume)

    return (int(pitch), float(volume))

# Read First note
current_note, current_vol = read_note()
previous_note = current_note
previous_vol  = current_vol

while True:
    if (current_note > 0.000000) and (current_note < 128.000000):

        # Play current note
        print("Play: ", current_note, " vol: ", current_vol)
        outport.send(Message('note_on', note=current_note, velocity=100 ))
        
        previous_note = current_note
        previous_vol  = current_vol

        # still playing same note
        while (previous_note == current_note):
            current_note, current_vol = read_note()

        # When note changes
        # Stop previous note in a thread
        subproceso = Thread(target=stop_note_async, args=(previous_note, 100))
        subproceso.start()
        print("Stopped: ", previous_note)

    else: 
        # No input sound (note: 0) or invalid note.
        # Read next
        previous_note = current_note
        previous_vol  = current_vol
        current_note, current_vol = read_note()
