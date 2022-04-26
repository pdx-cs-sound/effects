# Audio White Noise Player
# Bart Massey 2022

import argparse, numpy, sounddevice
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument(
    "-a", "--amplitude",
    help="Noise amplitude as fraction",
    type=float,
    default=0.25,
)
ap.add_argument(
    "-b", "--blocksize",
    help="Block size",
    type=int,
    default=128,
)
args = ap.parse_args()

blocksize = args.blocksize

stream = sounddevice.OutputStream(
    samplerate=48000,
    channels=1,
    blocksize=blocksize,
    dtype='int16',
)
stream.start()

peak = int(32767 * args.amplitude)
while True:
    error = stream.write(np.random.randint(
        -peak,
        peak,
        size=blocksize,
        dtype=np.int16,
    ))
    assert not error, "underrun"

stream.stop()
stream.close()
