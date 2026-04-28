# Distortion
# Bart Massey 2022

import argparse, audio, sounddevice
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument(
    "-v", "--volume",
    help="Output volume multiplier.",
    type=float,
    default=1.0,
)
ap.add_argument(
    "-g", "--gain",
    help="Input gain multiplier.",
    type=float,
    default=1.0,
)
ap.add_argument(
    "-t", "--threshold",
    help="Clipping threshold as fraction.",
    type=float,
    default=0.5,
)
ap.add_argument(
    "-a", "--asymmetric",
    help="Only clip positive half of signal.",
    action="store_true",
)
ap.add_argument(
    "-s", "--smooth",
    help="Smooth clip as overdrive fraction.",
    type=float,
    default=None,
)
ap.add_argument(
    "-c", "--crunch",
    help="Bitcrunch to given number of bits.",
    type=int,
    default=None,
)
ap.add_argument(
    "-z", "--zero-crossing",
    help="quantize to 1-bit",
    action = "store_true",
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

rate, psignal = audio.read_wave(args.infile)
npsignal = len(psignal)

def smoother(a, x):
    return 2 * (1 / (1 + np.exp(-a * (0.5 * x + 0.5)))) - 1

psignal *= args.gain
threshold = args.threshold
asymmetric = args.asymmetric
if args.crunch is not None:
    crunch = 2 ** args.crunch
smooth = args.smooth
for i in range(npsignal):
    x = psignal[i]
    if args.zero_crossing:
        y = 1 if x > 0 else -1
    elif crunch:
        y = np.floor(crunch * (x - 1)) / crunch
    elif smooth:
        y = smoother(smooth, x) / smooth
    elif not asymmetric and x > threshold:
        y = threshold
    elif x < -threshold:
        y = -threshold
    else:
        y = x
    
    psignal[i] = y
psignal *= args.volume

if args.outfile is None:
    sounddevice.play(psignal, samplerate=rate, blocking=True)
else:
    audio.write_wave(args.outfile, psignal, rate)
