# Audio Compressor
# Bart Massey

# https://www.uaudio.com/blog/audio-compression-basics/

import argparse
import numpy as np
import soundfile

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
    "infile",
    help="Input audio file.",
)
ap.add_argument(
    "outfile",
    help="Output audio file.",
)
args = ap.parse_args()
normalize = not args.unnormalized

in_sound = soundfile.SoundFile(args.infile)
if in_sound.channels != 1:
    eprint("sorry, mono audio only")
    exit(1)
psignal = in_sound.read()
npsignal = len(psignal)

twindow = 0.001 * args.window
nwindow = int(twindow * in_sound.samplerate)

threshold = args.threshold
ratio = args.ratio

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
        block *= scale(peak_db, 1 - 1 / ratio)

outfile = open(args.outfile, "wb")
soundfile.write(
    outfile,
    psignal,
    in_sound.samplerate,
    subtype=in_sound.subtype,
    endian=in_sound.endian,
    format=in_sound.format,
)
