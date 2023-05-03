#!/usr/bin/python3
import argparse, audio, sounddevice
import numpy as np
from scipy import signal

# Parse arguments.
parser = argparse.ArgumentParser()
parser.add_argument(
    "--freq",
    help="Tremolo rate in Hz.",
    type=float,
    default=2.0,
)
parser.add_argument(
    "--depth",
    help="Tremolo depth in msecs.",
    type=float,
    default=0.10,
)
parser.add_argument(
    "infile",
    help="Input wave filename.",
)
parser.add_argument(
    "outfile",
    nargs="?",
    help="Output wave filename.",
)
args = parser.parse_args()

info, channel = audio.read_wave(args.infile)
rate = info.framerate

nchannel = len(channel)
t = np.linspace(0, nchannel / float(rate), nchannel);
lfo = np.sin(2 * np.pi * args.freq * t)
output = np.zeros(nchannel)
depth = args.depth / 1000.0
for i in range(nchannel):
    ti = i + depth * lfo[i] * rate
    if ti < 0 or ti >= nchannel:
        c = 0
    else:
        fli = int(np.floor(ti))
        cei = int(np.ceil(ti))
        dt = ti - fli
        c = (1.0 - dt) * channel[fli] + dt * channel[cei]
        output[i] = c

if args.outfile is None:
    sounddevice.play(output, samplerate=rate, blocking=True)
else:
    audio.write_wave(args.outfile, info, output)
