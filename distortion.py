# Distortion
# Bart Massey 2022

import argparse, sounddevice, soundfile
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument(
    "-t", "--threshold",
    help="Compression threshold as fraction.",
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
    help="Smooth clip.",
    action="store_true",
)
ap.add_argument(
    "-c", "--crunch",
    help="Bitcrunch to given number of bits.",
    type=int,
    default=None,
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

in_sound = soundfile.SoundFile(args.infile)
if in_sound.channels != 1:
    eprint("sorry, mono audio only")
    exit(1)
if in_sound.subtype != 'PCM_16':
    eprint("sorry, 16-bit only")
    exit(1)
psignal = in_sound.read()
npsignal = len(psignal)

def smooth(x):
    return 2 * (1 / (1 + np.exp(-(x + 1)/2))) - 1

threshold = args.threshold
asymmetric = args.asymmetric
crunch = args.crunch
for i in range(npsignal):
    x = psignal[i]
    if crunch:
        x = 0.25 * int(2 ** crunch * x) / 2 ** crunch
    elif not asymmetric and x > threshold:
        x = threshold
    elif x < -threshold:
        x = -threshold
    
    psignal[i] = x

if args.outfile is None:
    sounddevice.play(psignal, samplerate=in_sound.samplerate, blocking=True)
else:
    outfile = open(args.outfile, "wb")
    soundfile.write(
        outfile,
        psignal,
        in_sound.samplerate,
        subtype=in_sound.subtype,
        endian=in_sound.endian,
        format=in_sound.format,
    )