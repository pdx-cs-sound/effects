#!/usr/bin/python3
import argparse, audio, sounddevice
import numpy as np
from scipy import signal

# Parse arguments.
parser = argparse.ArgumentParser()
parser.add_argument(
    "--freq",
    help="Vibrato rate in Hz.",
    type=float,
    default=2.0,
)
parser.add_argument(
    "--depth",
    help="Vibrato depth as fraction of full signal.",
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

t = np.linspace(0, len(channel) / float(rate), len(channel));
lfo = args.depth * np.sin(2 * np.pi * args.freq * t)
channel *= 1.0 - args.depth + lfo / 2

if args.outfile is None:
    sounddevice.play(channel, samplerate=rate, blocking=True)
else:
    audio.write_wave(args.outfile, info, channel)
