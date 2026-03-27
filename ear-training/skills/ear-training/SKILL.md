---
name: ear-training
description: Interactive ear training for musical intervals. Use this skill whenever the user wants to practice identifying intervals, train their ear for music, do interval recognition exercises, or asks to play/identify intervals like "major third", "perfect fifth", etc. Also trigger when users mention 练耳, 音程听辨, ear training, interval quiz, or want to generate two notes and guess the interval between them.
---

# Ear Training — Interval Recognition

An interactive ear training skill that generates two-note audio clips and quizzes the user on the interval between them.

## How It Works

1. The skill generates a WAV audio file containing two sequential piano-like tones
2. The audio is sent to the user
3. The user listens and identifies the interval (e.g., "major third", "perfect fifth", "大三度", "纯五度")
4. The skill reveals the answer and provides feedback

## Quick Start

When the user wants to practice ear training, run the generator script:

```bash
python3 <skill-dir>/scripts/generate_interval.py [options]
```

This outputs a JSON line with the interval details and the path to the generated WAV file.

### Options

| Flag | Description | Default |
|------|-------------|---------|
| `--output-dir <path>` | Directory for generated audio files | `/tmp/ear-training` |
| `--root-note <note>` | Fix the root note (e.g., `C4`, `F#3`) | Random (C3–C5) |
| `--interval <name>` | Fix the interval (e.g., `P4`, `m3`) | Random |
| `--direction <up\|down>` | Ascending or descending | `up` |
| `--duration <seconds>` | Duration of each note | `1.0` |
| `--gap <seconds>` | Silence between the two notes | `0.3` |

### Output Format

The script prints a single JSON line:

```json
{
  "root_note": "C4",
  "second_note": "E4",
  "interval": "M3",
  "interval_name_en": "Major Third",
  "interval_name_zh": "大三度",
  "semitones": 4,
  "direction": "up",
  "file": "/tmp/ear-training/interval_abc123.wav"
}
```

## Session Flow

### 1. Start a Round

Run the script with no fixed interval (random selection):

```bash
python3 <skill-dir>/scripts/generate_interval.py
```

Send the generated WAV file to the user with a prompt like:
> 🎵 听一下这两个音，它们之间是什么音程？
> (Listen to these two notes — what interval is it?)

**Important:** Do NOT reveal the answer yet. Do NOT mention the note names or interval in your message.

### 2. Wait for the User's Answer

The user responds with their guess (in English or Chinese). Accept these formats:
- Full names: "major third", "perfect fourth", "大三度", "纯四度"
- Short codes: "M3", "P4", "m7"
- Casual: "a third", "三度"

### 3. Reveal and Explain

After the user answers, compare their guess to the actual interval from the JSON output. Respond with:
- ✅ or ❌
- The correct answer (both English and Chinese names)
- The two notes that were played
- Optionally: a brief music theory note about the interval's character

### 4. Continue or Stop

Ask if they want another round. If yes, generate a new random interval. Track their score across the session if they do multiple rounds (e.g., "4/5 correct so far").

## Interval Reference

The script supports all intervals within one octave:

| Code | English | 中文 | Semitones |
|------|---------|------|-----------|
| P1 | Perfect Unison | 纯一度 | 0 |
| m2 | Minor Second | 小二度 | 1 |
| M2 | Major Second | 大二度 | 2 |
| m3 | Minor Third | 小三度 | 3 |
| M3 | Major Third | 大三度 | 4 |
| P4 | Perfect Fourth | 纯四度 | 5 |
| TT | Tritone | 三全音/增四度 | 6 |
| P5 | Perfect Fifth | 纯五度 | 7 |
| m6 | Minor Sixth | 小六度 | 8 |
| M6 | Major Sixth | 大六度 | 9 |
| m7 | Minor Seventh | 小七度 | 10 |
| M7 | Major Seventh | 大七度 | 11 |
| P8 | Perfect Octave | 纯八度 | 12 |

## Difficulty Progression

For beginners, suggest starting with easier intervals:
- **Level 1:** P1, P4, P5, P8 (perfect intervals — very distinct)
- **Level 2:** Add M3, m3 (thirds are common and recognizable)
- **Level 3:** Add M2, m2, M6, m6
- **Level 4:** All intervals including M7, m7, TT

You can use `--interval` to focus on specific intervals the user struggles with.

## Dependencies

This skill requires **FluidSynth** and a **General MIDI SoundFont** for realistic piano audio.

### FluidSynth

The `fluidsynth` CLI must be installed and available on PATH. If it's not detected, the script will exit with an error and a link to the install guide.

- **macOS (Homebrew):** `brew install fluid-synth`
- **Linux (apt):** `sudo apt install fluidsynth`
- **Other platforms:** https://github.com/FluidSynth/fluidsynth/wiki/Download

### SoundFont (.sf2)

Place a General MIDI SoundFont file in the skill's `soundfonts/` directory (or pass `--soundfont <path>`). The script auto-searches common locations. Recommended: [FluidR3_GM.sf2](https://member.keymusician.com/Member/FluidR3_GM/index.html) (~142MB).

### Python Packages

```bash
pip install numpy scipy midiutil
```

## Audio Synthesis

The script generates a MIDI file with the two notes, then renders it to WAV via FluidSynth using the SoundFont's Acoustic Grand Piano preset. This produces realistic, sample-based piano tones — much better than pure sine wave synthesis.
