#!/usr/bin/python3
import argparse
import numpy as np
from scipy import signal
import sys, wave

# Read a tone from a wave file.
def read_wave(filename):
    w = wave.open(filename, "rb")
    info = w.getparams()
    fbytes = w.readframes(info.nframes)
    w.close()
    sampletypes = {
        1: (np.uint8, -(1 << 7), 1 << 8),
        2: (np.int16, 0.5, 1 << 16),
        4: (np.int32, 0.5, 1 << 32),
    }
    if info.sampwidth not in sampletypes:
        raise IOException()
    sampletype, sampleoff, samplewidth = sampletypes[info.sampwidth]
    samples = np.frombuffer(fbytes, dtype=sampletype)
    scale = 2.0 / samplewidth
    fsamples = scale * (samples + sampleoff)
    channels = np.reshape(fsamples, (-1, info.nchannels))
    return (info, np.transpose(channels))

# Write a tone to a wave file.
def write_wave(filename, info, channels):
    samples = np.reshape(np.transpose(channels), (-1,))
    sampletypes = {
        1: ('u1', (1 << 7), 1 << 8),
        2: ('<i2', 0.5, 1 << 16),
        4: ('<i4', 0.5, 1 << 32),
    }
    if info.sampwidth not in sampletypes:
        raise IOException()
    sampletype, sampleoff, samplewidth = sampletypes[info.sampwidth]
    scale = samplewidth / 2.0
    fsamples = scale * samples + sampleoff
    hsamples = np.array(fsamples, dtype=sampletype)
    w = wave.open(filename, "wb")
    w.setparams(info)
    w.writeframes(hsamples)
    w.close()

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
    help="Output wave filename.",
)
args = parser.parse_args()

lap = 4
wah_rate = lap / args.rate
info, channels = read_wave(args.infile)

blocksize = info.framerate // 100
window = signal.windows.hann(blocksize)
ncontour = int(wah_rate * info.framerate / blocksize)
scale = args.height - args.depth
cspace = np.linspace(0, np.pi, ncontour)
contour = scale * np.log2(2 - np.sin(cspace)) + args.depth
fws = [ signal.firwin(128, c, window=('kaiser', 0.5))
        for c in contour ]

icontour = 0
waheds = []
for channel in channels:
    wahed = np.zeros(info.nframes)
    start = 0
    while start < info.nframes:
        end = min(start + blocksize, info.nframes)
        block = channel[start:end]
        icontour = (icontour + 1) % ncontour
        block = signal.convolve(block, fws[icontour], mode='same')
        invlap = 1.0 / lap
        for i in range(start, end):
            wahed[i] +=  invlap * block[i - start] * window[i - start]
        start += blocksize // lap
    waheds.append(wahed)

write_wave(args.outfile, info, np.array(waheds))
