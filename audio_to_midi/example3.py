import aubio
import numpy as num
import pyaudio
import wave

# PyAudio object.
p = pyaudio.PyAudio()

# Open stream.
stream = p.open(format=pyaudio.paFloat32,
    channels=1, rate=44100, input=True,
    frames_per_buffer=1024, input_device_index=2)

# Aubio's pitch detection.
pDetection = aubio.pitch("default", 2048,
    2048//2, 44100)
# Set unit.
pDetection.set_unit("midi")
pDetection.set_silence(-70)

while True:

    data = stream.read(1024)
    samples = num.fromstring(data,
        dtype=aubio.float_type)
    pitch = pDetection(samples)[0]
    # Compute the energy (volume) of the
    # current frame.
    volume = num.sum(samples**2)/len(samples)
    # Format the volume output so that at most
    # it has six decimal numbers.
    volume = "{:.6f}".format(volume)

    if (pitch != 0.000000): print(pitch)
    # if (volume != '0'): print(volume)
