#!/usr/bin/python3
import argparse, audio, sounddevice
import numpy as np
from scipy import signal

# Parse arguments.
parser = argparse.ArgumentParser()
parser.add_argument(
    "--rate",
    help="Wah rate in wahs per second.",
    type=float,
    default=0.2,
)
parser.add_argument(
    "--depth",
    help="Wah minimum unit frequency (must be > 0).",
    type=float,
    default=0.02,
)
parser.add_argument(
    "--height",
    help="Wah maximum unit frequency (must be > depth, < 1).",
    type=float,
    default=0.9,
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

lap = 4
wah_rate = lap / args.rate
info, channel = audio.read_wave(args.infile)
rate = info.framerate

blocksize = rate // 100
window = signal.windows.hann(blocksize)
ncontour = int(wah_rate * rate / blocksize)
scale = args.height - args.depth
cspace = np.linspace(0, np.pi, ncontour)
contour = scale * np.log2(2 - np.sin(cspace)) + args.depth
fws = [ signal.firwin(128, c, window=('kaiser', 0.5))
        for c in contour ]

icontour = 0
wahed = np.zeros(info.nframes)
start = 0
while start < info.nframes:
    end = min(start + blocksize, info.nframes)
    block = channel[start:end]
    icontour = (icontour + 1) % ncontour
    block = signal.convolve(block, fws[icontour], mode='same')
    invlap = 1.0 / lap
    for i in range(start, end):
        wahed[i] += invlap * block[i - start] * window[i - start]
    start += blocksize // lap

if args.outfile is None:
    sounddevice.play(wahed, samplerate=rate, blocking=True)
else:
    audio.write_wave(args.outfile, info, wahed)
