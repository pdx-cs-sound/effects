# Audio Compressor
# Bart Massey

# https://www.uaudio.com/blog/audio-compression-basics/

import argparse, audio, sounddevice
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument(
    "-t", "--threshold",
    help="Compression threshold in dB.",
    type=float,
    default=-20.0,
)
ap.add_argument(
    "-r", "--ratio",
    help="Compression ratio in dB.",
    type=float,
    default=4.0,
)
ap.add_argument(
    "-w", "--window",
    help="Window in ms.",
    type=float,
    default=20.0,
)
ap.add_argument(
    "-u", "--unnormalized",
    help="Disable gain normalization.",
    action="store_true",
)
ap.add_argument(
    "-l", "--level",
    help="Level measurement mode.",
    choices = ("rms", "peak"),
    default = "peak",
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
normalize = not args.unnormalized

info, psignal = audio.read_wave(args.infile)
npsignal = len(psignal)
rate = info.framerate

twindow = 0.001 * args.window
nwindow = int(twindow * rate)

threshold = args.threshold
ratio = args.ratio

def inv_db(p):
    return np.power(10, p / 20)

def scale(p, r):
    excess = p - threshold
    scale_db = excess * (1 / r - 1)
    if normalize:
        scale_db += threshold * (1 / ratio - 1)
    return min(inv_db(scale_db), 1)

for i in range(0, npsignal - nwindow, nwindow):
    j = min(i + nwindow, npsignal)
    block = psignal[i:j]
    peak_level = np.max(block) - np.min(block)
    peak_db = 20 * np.log10(peak_level)
    rms_level = np.sqrt(np.sum(block**2) / nwindow)
    rms_db = 20 * np.log10(rms_level)
    if args.level == "peak":
        level_db = peak_db
    elif args.level == "rms":
        level_db = rms_db
    if level_db >= threshold:
        block *= scale(level_db, ratio)
    elif normalize:
        block *= scale(level_db, 1 - 1 / ratio)

if args.outfile is None:
    sounddevice.play(psignal, samplerate=rate, blocking=True)
else:
    audio.write_wave(args.outfile, info, psignal)
