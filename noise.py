# Audio Compressor
# Bart Massey

# https://www.uaudio.com/blog/audio-compression-basics/

import sounddevice
import numpy as np

stream = sounddevice.OutputStream(samplerate=48000, channels=1, dtype='int16')
stream.start()

peak = 128
while True:
    error = stream.write(np.random.randint(-peak, peak, dtype=np.int16))
    assert not error, "underrun"

stream.stop()
stream.close()
