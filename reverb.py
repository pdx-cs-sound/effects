# Audio Compressor
# Bart Massey

# https://www.uaudio.com/blog/audio-compression-basics/

import argparse
import numpy as np
import soundfile

ap = argparse.ArgumentParser()
ap.add_argument(
    "-d", "--delay",
    help="Delay in ms.",
    type=float,
    default=100.0,
)
ap.add_argument(
    "-w", "--wet",
    help="Fraction of wet signal.",
    type=float,
    default=0.5,
)
ap.add_argument(
    "-r", "--reverb",
    help="Reverberation fraction.",
    type=float,
    default=0.2,
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

class RingBuffer(object):
    def __init__(self, length):
        self.length = length
        self.buffer = [0]*length
        self.head = 0
        self.tail = 0
        self.empty = True

    def enqueue(self, s):
        assert self.empty or self.head != self.tail
        self.buffer[self.tail] = s
        self.tail = (self.tail + 1) % self.length
        self.empty = False

    def dequeue(self):
        assert not self.empty
        s = self.buffer[self.head]
        self.head = (self.head + 1) % self.length
        self.empty = self.head == self.tail
        return s

    def is_empty(self):
        return self.empty

in_sound = soundfile.SoundFile(args.infile)
if in_sound.channels != 1:
    eprint("sorry, mono audio only")
    exit(1)
psignal = in_sound.read()
npsignal = len(psignal)

delay = int(args.delay * in_sound.samplerate)
wet = args.wet
reverb = args.reverb
buffer = RingBuffer(delay)
outsignal = []
for (i, s) in enumerate(psignal):
    if i < delay:
        sdelay = 0
    else:
        sdelay = buffer.dequeue()
    outsignal.append((1 - wet) * s + wet * sdelay)
    buffer.enqueue((1 - reverb) * s + reverb * sdelay)
outsignal = np.array(outsignal)

outfile = open(args.outfile, "wb")
soundfile.write(
    outfile,
    outsignal,
    in_sound.samplerate,
    subtype=in_sound.subtype,
    endian=in_sound.endian,
    format=in_sound.format,
)
