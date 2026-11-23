#!/usr/bin/env python3
"""Gera duas versões curtas de "Saída da Caverna".

Arquivos produzidos:
  - saida_sem_resposta.mid / .wav (referência)
  - saida_contracanto.mid / .wav (violoncelo nos compassos 5–6)

A resposta cantável é: Mi–Dó / Si–Sol (E3–C3 / B2–G2).
"""

from __future__ import annotations

from pathlib import Path

import fluidsynth
import mido
import numpy as np
import soundfile as sf
from music21 import chord, instrument, key, meter, note, stream, tempo


BPM = 84
SAMPLE_RATE = 44_100
MELODY_VELOCITY = 76
RESPONSE_VELOCITY = 64  # 12 abaixo da melodia
ROOT = Path(__file__).resolve().parent
SOUNDFONT = Path("/usr/share/sounds/sf2/TimGM6mb.sf2")


MELODY = {
    1: [("E4", 1), ("G4", 1), ("C5", 2)],
    2: [("D5", 1), ("B4", 1), ("G4", 2)],
    3: [("A4", 1), ("C5", 1), ("E5", 2)],
    4: [("C5", 1), ("A4", 1), ("F4", 2)],
    5: [("A4", 1), ("C5", 1), ("E5", 2)],
    6: [("G5", 2), ("D5", 1), ("B4", 1)],
    7: [("A4", 1), ("G4", 1), ("F4", 2)],
    8: [("E4", 1), ("D4", 1), ("C4", 2)],
}

HARMONY = {
    1: ["C3", "E3", "G3"],
    2: ["G2", "B2", "D3"],
    3: ["A2", "C3", "E3"],
    4: ["F2", "A2", "C3"],
    5: ["A2", "C3", "E3"],
    6: ["G2", "B2", "D3"],
    7: ["F2", "A2", "C3"],
    8: ["C3", "E3", "G3"],
}

RESPONSE = {
    5: [(None, 2), ("E3", 1), ("C3", 1)],
    6: [(None, 1), ("B2", 1), ("G2", 2)],
}


def make_measure(number: int) -> stream.Measure:
    measure = stream.Measure(number=number)
    if number == 1:
        measure.insert(0, meter.TimeSignature("4/4"))
        measure.insert(0, key.Key("C"))
    return measure


def make_melody() -> stream.Part:
    part = stream.Part(id="melodia")
    part.partName = "Melodia principal"
    inst = instrument.Flute()
    inst.midiChannel = 0
    part.insert(0, inst)
    for measure_number, events in MELODY.items():
        measure = make_measure(measure_number)
        for pitch_name, duration in events:
            item = note.Note(pitch_name, quarterLength=duration)
            item.volume.velocity = 70 if measure_number == 8 else MELODY_VELOCITY
            measure.append(item)
        part.append(measure)
    return part


def make_harmony() -> stream.Part:
    part = stream.Part(id="harmonia")
    part.partName = "Acordes"
    inst = instrument.Piano()
    inst.midiChannel = 2
    part.insert(0, inst)
    for measure_number, pitches in HARMONY.items():
        measure = make_measure(measure_number)
        item = chord.Chord(pitches, quarterLength=4)
        item.volume.velocity = 46
        measure.append(item)
        part.append(measure)
    return part


def make_response() -> stream.Part:
    part = stream.Part(id="resposta")
    part.partName = "Resposta — Violoncelo"
    inst = instrument.Violoncello()
    inst.midiChannel = 1
    part.insert(0, inst)
    for measure_number in range(1, 9):
        measure = make_measure(measure_number)
        events = RESPONSE.get(measure_number, [(None, 4)])
        for pitch_name, duration in events:
            if pitch_name is None:
                measure.append(note.Rest(quarterLength=duration))
            else:
                item = note.Note(pitch_name, quarterLength=duration)
                item.volume.velocity = RESPONSE_VELOCITY
                measure.append(item)
        part.append(measure)
    return part


def build_score(with_response: bool) -> stream.Score:
    score = stream.Score(id="saida_da_caverna")
    score.metadata = None
    score.insert(0, tempo.MetronomeMark(number=BPM))
    score.append(make_melody())
    score.append(make_harmony())
    if with_response:
        score.append(make_response())
    return score


def force_midi_channels(path: Path, with_response: bool) -> None:
    """Garante canais próprios: melodia=0, resposta=1, harmonia=2."""
    midi = mido.MidiFile(path)
    assignments = {
        "Flute": (0, 73),       # melody
        "Piano": (2, 0),        # harmony / acoustic grand piano
        "Violoncello": (1, 42), # response
    }
    found: set[str] = set()
    for track in midi.tracks:
        track_name = next(
            (msg.name for msg in track if msg.type == "track_name"), ""
        )
        for label, (channel, program) in assignments.items():
            if label not in track_name:
                continue
            found.add(label)
            for msg in track:
                if hasattr(msg, "channel"):
                    msg.channel = channel
                if msg.type == "program_change":
                    msg.program = program
    required = {"Flute", "Piano"}
    if with_response:
        required.add("Violoncello")
    if not required.issubset(found):
        raise RuntimeError(f"Faixas MIDI não identificadas: {required - found}")
    midi.save(path)


def render_midi(midi_path: Path, wav_path: Path) -> None:
    """Renderiza offline com libFluidSynth e a SoundFont indicada."""
    if not SOUNDFONT.exists():
        raise FileNotFoundError(f"SoundFont não encontrada: {SOUNDFONT}")

    midi = mido.MidiFile(midi_path)
    synth = fluidsynth.Synth(samplerate=float(SAMPLE_RATE), gain=0.55)
    soundfont_id = synth.sfload(str(SOUNDFONT))
    for channel in range(16):
        if channel != 9:
            synth.program_select(channel, soundfont_id, 0, 0)

    tempo_us = mido.bpm2tempo(BPM)
    chunks: list[np.ndarray] = []
    for msg in mido.merge_tracks(midi.tracks):
        if msg.time:
            seconds = mido.tick2second(msg.time, midi.ticks_per_beat, tempo_us)
            frame_count = max(0, round(seconds * SAMPLE_RATE))
            if frame_count:
                chunks.append(np.asarray(synth.get_samples(frame_count), dtype=np.int16))
        if msg.type == "set_tempo":
            tempo_us = msg.tempo
        elif msg.type == "program_change":
            synth.program_select(msg.channel, soundfont_id, 0, msg.program)
        elif msg.type == "control_change":
            synth.cc(msg.channel, msg.control, msg.value)
        elif msg.type == "pitchwheel":
            synth.pitch_bend(msg.channel, msg.pitch)
        elif msg.type == "note_on" and msg.velocity > 0:
            synth.noteon(msg.channel, msg.note, msg.velocity)
        elif msg.type in {"note_off", "note_on"}:
            synth.noteoff(msg.channel, msg.note)

    chunks.append(np.asarray(synth.get_samples(round(0.75 * SAMPLE_RATE)), dtype=np.int16))
    synth.delete()
    interleaved = np.concatenate(chunks)
    stereo = interleaved.reshape(-1, 2)
    sf.write(wav_path, stereo, SAMPLE_RATE, subtype="PCM_16")


def export_version(stem: str, with_response: bool) -> tuple[Path, Path]:
    midi_path = ROOT / f"{stem}.mid"
    wav_path = ROOT / f"{stem}.wav"
    score = build_score(with_response)
    score.write("midi", fp=midi_path)
    force_midi_channels(midi_path, with_response)
    render_midi(midi_path, wav_path)
    return midi_path, wav_path


def midi_note_summary(path: Path) -> dict[int, list[tuple[int, int]]]:
    midi = mido.MidiFile(path)
    result: dict[int, list[tuple[int, int]]] = {}
    for track in midi.tracks:
        for msg in track:
            if msg.type == "note_on" and msg.velocity > 0:
                result.setdefault(msg.channel, []).append((msg.note, msg.velocity))
    return result


def validate(midi_path: Path, wav_path: Path) -> None:
    response_part = make_response()
    sounding = list(response_part.recurse().notes)
    assert len(sounding) == 4, "A resposta deve ter exatamente quatro notas"
    assert {n.measureNumber for n in sounding} <= {5, 6}
    assert all(n.volume.velocity == RESPONSE_VELOCITY for n in sounding)
    assert MELODY_VELOCITY - RESPONSE_VELOCITY == 12

    allowed = {5: {"A", "C", "E"}, 6: {"G", "B", "D"}}
    assert all(n.pitch.name in allowed[n.measureNumber] for n in sounding)

    channels = midi_note_summary(midi_path)
    assert 0 in channels and 1 in channels and 2 in channels
    assert len(channels[1]) == 4
    assert all(velocity == RESPONSE_VELOCITY for _, velocity in channels[1])

    audio, sample_rate = sf.read(wav_path, always_2d=True)
    duration = len(audio) / sample_rate
    assert 0 < duration < 30, f"Duração inválida: {duration:.2f}s"
    assert np.max(np.abs(audio)) > 0.01, "WAV silencioso"

    print(f"OK: {midi_path.name} | {wav_path.name} | {duration:.2f}s")
    print("Resposta: E3–C3 / B2–G2 | compassos 5–6 | canal MIDI 2 (índice 1)")


def main() -> None:
    reference_midi, reference_wav = export_version("saida_sem_resposta", False)
    result_midi, result_wav = export_version("saida_contracanto", True)
    validate(result_midi, result_wav)

    ref_audio, _ = sf.read(reference_wav, always_2d=True)
    result_audio, _ = sf.read(result_wav, always_2d=True)
    ref_rms = float(np.sqrt(np.mean(ref_audio**2)))
    result_rms = float(np.sqrt(np.mean(result_audio**2)))
    print(f"Comparação RMS: sem resposta={ref_rms:.4f}; com resposta={result_rms:.4f}")
    print("Escolha: versão com resposta — diálogo audível sem encobrir a melodia.")
    print(f"Referência preservada: {reference_midi.name}, {reference_wav.name}")


if __name__ == "__main__":
    main()
