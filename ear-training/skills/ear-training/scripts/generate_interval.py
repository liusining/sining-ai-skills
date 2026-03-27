#!/usr/bin/env python3
"""
Ear Training — Interval Audio Generator

Generates a WAV file containing two sequential piano-like tones forming a
musical interval. Uses FluidSynth + SoundFont for realistic piano timbre.

Dependencies:
  - fluidsynth CLI  (install: https://github.com/FluidSynth/fluidsynth/wiki/Download)
  - A General MIDI SoundFont (.sf2) file
  - Python packages: numpy, scipy, midiutil
"""

import argparse
import json
import os
import random
import shutil
import string
import subprocess
import sys
import tempfile

import numpy as np
from midiutil import MIDIFile
from scipy.io.wavfile import read as read_wav
from scipy.io.wavfile import write as write_wav

# ---------------------------------------------------------------------------
# Music theory constants
# ---------------------------------------------------------------------------

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

NOTE_ALIASES = {
    "Db": "C#", "Eb": "D#", "Fb": "E", "Gb": "F#",
    "Ab": "G#", "Bb": "A#", "Cb": "B",
}

INTERVALS = [
    {"code": "P1", "en": "Perfect Unison",  "zh": "纯一度",       "semitones": 0},
    {"code": "m2", "en": "Minor Second",    "zh": "小二度",       "semitones": 1},
    {"code": "M2", "en": "Major Second",    "zh": "大二度",       "semitones": 2},
    {"code": "m3", "en": "Minor Third",     "zh": "小三度",       "semitones": 3},
    {"code": "M3", "en": "Major Third",     "zh": "大三度",       "semitones": 4},
    {"code": "P4", "en": "Perfect Fourth",  "zh": "纯四度",       "semitones": 5},
    {"code": "TT", "en": "Tritone",         "zh": "三全音/增四度", "semitones": 6},
    {"code": "P5", "en": "Perfect Fifth",   "zh": "纯五度",       "semitones": 7},
    {"code": "m6", "en": "Minor Sixth",     "zh": "小六度",       "semitones": 8},
    {"code": "M6", "en": "Major Sixth",     "zh": "大六度",       "semitones": 9},
    {"code": "m7", "en": "Minor Seventh",   "zh": "小七度",       "semitones": 10},
    {"code": "M7", "en": "Major Seventh",   "zh": "大七度",       "semitones": 11},
    {"code": "P8", "en": "Perfect Octave",  "zh": "纯八度",       "semitones": 12},
]

INTERVAL_BY_CODE = {iv["code"]: iv for iv in INTERVALS}

# ---------------------------------------------------------------------------
# SoundFont search paths
# ---------------------------------------------------------------------------

SOUNDFONT_SEARCH_PATHS = [
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "soundfonts"),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."),
    "/usr/share/sounds/sf2",
    "/usr/share/soundfonts",
    "/usr/local/share/sounds/sf2",
    "/opt/homebrew/share/sounds/sf2",
]

SOUNDFONT_NAMES = [
    "FluidR3_GM.sf2", "FluidR3_GM2-2.sf2",
    "GeneralUser_GS.sf2", "default.sf2",
]

# ---------------------------------------------------------------------------
# Note helpers
# ---------------------------------------------------------------------------

def note_to_midi(note_str: str) -> int:
    """Parse 'C#4', 'Db3', 'A5' etc. → MIDI note number."""
    note_str = note_str.strip()
    if len(note_str) < 2:
        raise ValueError(f"Invalid note: {note_str}")
    if note_str[1] in ("#", "b"):
        name = note_str[:2]
        octave = int(note_str[2:])
    else:
        name = note_str[0]
        octave = int(note_str[1:])
    name = NOTE_ALIASES.get(name, name)
    if name not in NOTE_NAMES:
        raise ValueError(f"Unknown note name: {name}")
    return NOTE_NAMES.index(name) + (octave + 1) * 12


def midi_to_note(midi: int) -> str:
    octave = midi // 12 - 1
    name = NOTE_NAMES[midi % 12]
    return f"{name}{octave}"

# ---------------------------------------------------------------------------
# FluidSynth helpers
# ---------------------------------------------------------------------------

def find_soundfont(explicit_path: str = None) -> str:
    if explicit_path and os.path.isfile(explicit_path):
        return explicit_path
    for search_dir in SOUNDFONT_SEARCH_PATHS:
        for sf_name in SOUNDFONT_NAMES:
            path = os.path.join(search_dir, sf_name)
            if os.path.isfile(path):
                return path
    raise FileNotFoundError(
        "No SoundFont (.sf2) file found. Place a GM SoundFont in the "
        "skill's soundfonts/ directory, or pass --soundfont <path>."
    )


def check_fluidsynth():
    if not shutil.which("fluidsynth"):
        print(json.dumps({
            "error": "fluidsynth not found",
            "message": "FluidSynth is required but not installed. "
                       "Install it from: https://github.com/FluidSynth/fluidsynth/wiki/Download",
        }))
        sys.exit(1)

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

SAMPLE_RATE = 44100
TEMPO_BPM = 120
# At 120 BPM, 1 beat = 0.5 seconds, so 1 second = 2 beats
BEATS_PER_SECOND = TEMPO_BPM / 60.0


def main():
    parser = argparse.ArgumentParser(description="Generate an interval audio quiz")
    parser.add_argument("--output-dir", default="/tmp/ear-training",
                        help="Directory for output WAV files")
    parser.add_argument("--root-note", default=None,
                        help="Root note, e.g. C4, F#3 (random if omitted)")
    parser.add_argument("--interval", default=None,
                        help="Interval code, e.g. M3, P5 (random if omitted)")
    parser.add_argument("--direction", choices=["up", "down"], default="up",
                        help="Ascending or descending interval")
    parser.add_argument("--duration", type=float, default=1.0,
                        help="Duration of each note in seconds")
    parser.add_argument("--gap", type=float, default=0.3,
                        help="Silence between notes in seconds")
    parser.add_argument("--soundfont", default=None,
                        help="Path to SoundFont (.sf2) file")
    args = parser.parse_args()

    # --- Pre-flight checks ---
    check_fluidsynth()
    sf2_path = find_soundfont(args.soundfont)
    os.makedirs(args.output_dir, exist_ok=True)

    # --- Pick root note ---
    if args.root_note:
        root_midi = note_to_midi(args.root_note)
    else:
        root_midi = random.randint(48, 72)  # C3 to C5

    # --- Pick interval ---
    if args.interval:
        interval_info = None
        if args.interval in INTERVAL_BY_CODE:
            interval_info = INTERVAL_BY_CODE[args.interval]
        else:
            for iv in INTERVALS:
                if iv["code"].lower() == args.interval.lower() and iv["code"][0] not in ("m", "M"):
                    interval_info = iv
                    break
        if interval_info is None:
            print(json.dumps({"error": f"Unknown interval: {args.interval}"}))
            sys.exit(1)
    else:
        interval_info = random.choice(INTERVALS[1:])  # exclude P1

    semitones = interval_info["semitones"]

    # --- Compute second note ---
    if args.direction == "up":
        second_midi = root_midi + semitones
    else:
        second_midi = root_midi - semitones

    # Clamp to piano range (A0=21 to C8=108)
    if second_midi < 21 or second_midi > 108:
        if args.direction == "up":
            root_midi = max(48, 108 - semitones - 12)
        else:
            root_midi = min(72, 21 + semitones + 12)
        second_midi = root_midi + semitones if args.direction == "up" else root_midi - semitones

    # --- Build MIDI with midiutil ---
    dur_beats = args.duration * BEATS_PER_SECOND
    gap_beats = args.gap * BEATS_PER_SECOND

    midi = MIDIFile(1)
    midi.addTempo(0, 0, TEMPO_BPM)
    midi.addProgramChange(0, 0, 0, 0)  # Acoustic Grand Piano

    # Note 1
    midi.addNote(0, 0, root_midi, 0, dur_beats, 100)
    # Note 2 starts after note1 duration + gap
    note2_start = dur_beats + gap_beats
    midi.addNote(0, 0, second_midi, note2_start, dur_beats, 100)

    # --- Render with FluidSynth ---
    tag = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))

    with tempfile.TemporaryDirectory() as tmpdir:
        midi_path = os.path.join(tmpdir, "interval.mid")
        raw_wav_path = os.path.join(tmpdir, "interval_raw.wav")

        with open(midi_path, "wb") as f:
            midi.writeFile(f)

        cmd = [
            "fluidsynth", "-ni",
            "-F", raw_wav_path,
            "-r", str(SAMPLE_RATE),
            "-g", "1.0",
            sf2_path, midi_path,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            print(json.dumps({"error": f"fluidsynth failed: {result.stderr}"}))
            sys.exit(1)

        if not os.path.isfile(raw_wav_path):
            print(json.dumps({"error": "fluidsynth produced no output"}))
            sys.exit(1)

        # Read rendered WAV
        sr, data = read_wav(raw_wav_path)

    # Mix to mono if stereo
    if len(data.shape) > 1:
        data = data.astype(np.float64).mean(axis=1)
    else:
        data = data.astype(np.float64)

    # Normalize
    peak = np.max(np.abs(data))
    if peak > 0:
        data = data / peak
    audio_16bit = (data * 32767 * 0.85).astype(np.int16)

    # Write final WAV
    filename = f"interval_{tag}.wav"
    filepath = os.path.join(args.output_dir, filename)
    write_wav(filepath, SAMPLE_RATE, audio_16bit)

    # --- Output metadata ---
    result = {
        "root_note": midi_to_note(root_midi),
        "second_note": midi_to_note(second_midi),
        "interval": interval_info["code"],
        "interval_name_en": interval_info["en"],
        "interval_name_zh": interval_info["zh"],
        "semitones": semitones,
        "direction": args.direction,
        "file": filepath,
    }
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
