# Audio Compressor
# Bart Massey

# https://www.uaudio.com/blog/audio-compression-basics/

import argparse
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument(
    "-t", "--threshold",
    help="Compression threshold in dB.",
    type=float,
    default=-40.0,
)
ap.add_argument(
    "-r", "--ratio",
    help="Compression ratio.",
    type=float,
    default=8.0,
)
ap.add_argument(
    "-w", "--window",
    help="Window in ms.",
    type=float,
    default=5.0,
)
ap.add_argument(
    "-u", "--unnormalized",
    help="Disable gain normalization.",
    action="store_true",
)
args = ap.parse_args()
normalize = not args.unnormalized

samplerate = 48000
twindow = 0.001 * args.window
nwindow = int(twindow * samplerate)

threshold = args.threshold
ratio = args.ratio

secs = 5
npsignal = secs * samplerate
psignal = 0.5 * np.sin(np.linspace(0, 2 * np.pi * 1000 * secs, npsignal))
db = np.linspace(-140, 0, npsignal, endpoint=True)
ampl = np.power(10, db / 20)
psignal *= ampl.transpose()

def inv_db(p):
    return np.power(10, p / 20)

def scale(p, r):
    excess = p - threshold
    scale_db = excess * (1 / r - 1)
    if normalize:
        scale_db += threshold * (1 / ratio - 1)
    return inv_db(scale_db)

for i in range(0, npsignal - nwindow, nwindow):
    j = min(i + nwindow, npsignal)
    block = psignal[i:j]
    peak = np.max(block) - np.min(block)
    peak_db = 20 * np.log10(peak)
    if peak_db >= threshold:
        block *= scale(peak_db, ratio)
    elif normalize:
        block *= scale(peak_db, 1)

for i in range(0, npsignal - nwindow, nwindow):
    j = min(i + nwindow, npsignal)
    block = psignal[i:j]
    peak = np.max(block) - np.min(block)
    peak_db = 20 * np.log10(peak)
    print(db[j-1], peak_db)
