# Audio Compressor
# Bart Massey

# https://www.uaudio.com/blog/audio-compression-basics/

import argparse, audio, sounddevice
import numpy as np
from scipy import signal

ap = argparse.ArgumentParser()
ap.add_argument(
    "-d", "--direction",
    help="Upsample or downsample",
    default='upsample',
)
ap.add_argument(
    "infile",
    help="Input audio file.",
)
ap.add_argument(
    "outfile",
    nargs="?",
    help="Output audio file.",
)
args = ap.parse_args()

info, psignal = audio.read_wave(args.infile)
npsignal = len(psignal)
rate = info.framerate

filter = signal.iirfilter(32, 0.5, btype='lowpass', rp=1.0, rs=3.0, ftype='ellip', output='sos')

if args.direction == 'upsample':
    outsignal = np.zeros(2 * npsignal, dtype = np.float32)
    outsignal[::2] = 2 * signal.sosfilt(filter, psignal)
else:
    outsignal = signal.sosfilt(filter, psignal)[::2]

if args.outfile is None:
    sounddevice.play(outsignal, samplerate=rate, blocking=True)
else:
    audio.write_wave(args.outfile, info, outsignal)
