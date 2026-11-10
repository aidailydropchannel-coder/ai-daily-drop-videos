"""AI Daily Drop voice engine.

Kokoro v1.0 (ONNX) speech model + misaki pronunciation dictionaries (data only).
Usage:
    python3 voice.py --voice af_heart --speed 1.05 --out line.wav "Text to speak."
"""
import argparse, json, re, wave
from pathlib import Path

import numpy as np
import onnxruntime as ort

HERE = Path(__file__).parent / "tts_data"   # filled by engine/setup.sh
SR = 24000
VOCAB = json.load(open(HERE / "config.json"))["vocab"]

LEXICONS = {}
for lang in ("us", "gb"):
    LEXICONS[lang] = {}
    for name in (f"{lang}_gold.json", f"{lang}_silver.json"):
        for k, v in json.load(open(HERE / name)).items():
            LEXICONS[lang].setdefault(k, v)
_LEX = LEXICONS["us"]

# Extra pronunciations for brand / tech words (misaki symbols: A=eɪ I=aɪ O=oʊ W=aʊ Y=ɔɪ).
CUSTOM = {
    "a": "ɐ", "A": "ɐ",
    "AI": "ˈAˈI", "AIs": "ˈAˈIz", "ChatGPT": "ʧˈæt ʤˌiˌpiˈti", "GPT": "ʤˌiˌpiˈti",
    "OpenAI": "ˈOpᵊn ˌAˈI", "Claude": "klˈɔd", "Anthropic": "ænθɹˈɑpɪk",
    "Gemini": "ʤˈɛmᵻnI", "Midjourney": "mˈɪdʤˌɜɹni", "Nvidia": "ɛnvˈɪdiə",
    "NVIDIA": "ɛnvˈɪdiə", "app": "ˈæp", "apps": "ˈæps", "API": "ˌAˌpiˈI",
    "Kimi": "kˈimi", "Qwen": "kwˈɛn", "DeepSeek": "dˈipsik", "Copilot": "kˈOpIlət",
    "Perplexity": "pɚplˈɛksᵻti", "Sora": "sˈɔɹə", "Grok": "ɡɹˈɑk", "xAI": "ˈɛks ˌAˈI",
    "LLM": "ˌɛlˌɛlˈɛm", "LLMs": "ˌɛlˌɛlˈɛmz", "CEO": "sˌiˌiˈO", "GIF": "ɡˈɪf", "GIFs": "ɡˈɪfs", "Codex": "kˈOdɛks",
    "copies": "kˈɑpiz",
}

LETTERS = {c: p for c, p in zip("ABCDEFGHIJKLMNOPQRSTUVWXYZ", [
    "ˈA", "bˈi", "sˈi", "dˈi", "ˈi", "ˈɛf", "ʤˈi", "ˈAʧ", "ˈI", "ʤˈA", "kˈA", "ˈɛl", "ˈɛm",
    "ˈɛn", "ˈO", "pˈi", "kjˈu", "ˈɑɹ", "ˈɛs", "tˈi", "jˈu", "vˈi", "dˈʌbᵊljˌu", "ˈɛks", "wˈI", "zˈi"])}

ONES = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split()
TENS = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()


def num_words(n):
    if n < 20: return ONES[n]
    if n < 100: return TENS[n // 10] + ("" if n % 10 == 0 else " " + ONES[n % 10])
    if n < 1000: return ONES[n // 100] + " hundred" + ("" if n % 100 == 0 else " " + num_words(n % 100))
    for div, word in ((10**9, "billion"), (10**6, "million"), (1000, "thousand")):
        if n >= div:
            r = n % div
            return num_words(n // div) + " " + word + ("" if r == 0 else " " + num_words(r))


def year_words(n):
    if 2000 <= n < 2010: return num_words(n)
    if 1100 <= n < 2100: return num_words(n // 100) + " " + (num_words(n % 100) if n % 100 >= 10 else ("hundred" if n % 100 == 0 else "oh " + num_words(n % 100)))
    return num_words(n)


def normalize(text):
    text = text.replace("’", "'").replace("–", ", ").replace("&", " and ")
    text = re.sub(r"\$(\d+(?:\.\d+)?)\s*(billion|million|thousand)", r"\1 \2 dollars", text)
    text = re.sub(r"\$(\d+)", r"\1 dollars", text)
    text = re.sub(r"(\d+)%", r"\1 percent", text)
    text = re.sub(r"(\d+)x\b", r"\1 times", text)

    def dec(m):
        a, b = m.group(1), m.group(2)
        return num_words(int(a)) + " point " + " ".join(ONES[int(d)] for d in b)
    text = re.sub(r"(\d+)\.(\d+)", dec, text)
    text = re.sub(r"\b(1[1-9]\d\d|20\d\d)\b", lambda m: year_words(int(m.group(1))), text)
    text = re.sub(r"\d{1,3}(?:,\d{3})+|\d+", lambda m: num_words(int(m.group(0).replace(",", ""))), text)
    return text


def lookup(word):
    for w in (word, word.lower(), word.capitalize()):
        if w in CUSTOM: return CUSTOM[w]
        v = _LEX.get(w)
        if isinstance(v, dict): v = v.get("DEFAULT") or next((x for x in v.values() if x), None)
        if v: return v
    return None


VOICELESS = set("ptkfθ")
SIBILANT = set("szʃʒʧʤ")


def g2p_word(word):
    p = lookup(word)
    if p: return p
    low = word.lower()
    if low.endswith("'s") and (b := g2p_word(word[:-2])):
        return b + ("ᵻz" if b[-1] in SIBILANT else "s" if b[-1] in VOICELESS else "z")
    for suf in ("es", "s"):
        if low.endswith(suf) and len(low) > len(suf) + 2 and (b := lookup(word[: -len(suf)])):
            return b + ("ᵻz" if b[-1] in SIBILANT else "s" if b[-1] in VOICELESS else "z")
    if low.endswith("ed") and len(low) > 4:
        for stem in (word[:-2], word[:-1], word[:-3]):
            if (b := lookup(stem)):
                return b + ("ᵻd" if b[-1] in "td" else "t" if b[-1] in VOICELESS | SIBILANT - set("zʒʤ") else "d")
    if low.endswith("ing") and len(low) > 5:
        for stem in (word[:-3], word[:-3] + "e", word[:-4]):
            if (b := lookup(stem)): return b + "ɪŋ"
    if low.endswith("ly") and (b := lookup(word[:-2])): return b + "li"
    if word.isupper() and len(word) <= 5:
        return "".join(LETTERS[c] for c in word if c in LETTERS)
    MISSING.add(word)
    return "".join(LETTERS[c] for c in word.upper() if c in LETTERS)


MISSING = set()


def phonemize(text):
    text = normalize(text)
    out = []
    for tok in re.findall(r"[A-Za-z][A-Za-z']*|[.,!?;:—…]", text):
        if tok[0].isalpha():
            tok = tok.strip("'")
            out.append(" " + g2p_word(tok))
        else:
            out.append(tok)
    s = "".join(out).strip()
    return "".join(ch for ch in s if ch in VOCAB)


class Voice:
    def __init__(self):
        opts = ort.SessionOptions()
        opts.intra_op_num_threads = 4
        self.sess = ort.InferenceSession(str(HERE / "kokoro-v1.0.onnx"), opts)
        self.voices = np.load(HERE / "voices-v1.0.bin")

    def _chunks(self, phon, limit=480):
        if len(phon) <= limit: return [phon]
        parts, cur = [], ""
        for piece in re.split(r"(?<=[.!?,;])\s", phon):
            if len(cur) + len(piece) + 1 > limit and cur:
                parts.append(cur); cur = piece
            else:
                cur = (cur + " " + piece).strip()
        if cur: parts.append(cur)
        return parts

    def speak(self, text, voice="af_heart", speed=1.0):
        global _LEX
        _LEX = LEXICONS["gb" if voice.startswith("b") else "us"]
        style_all = self.voices[voice]
        audio = []
        for chunk in self._chunks(phonemize(text)):
            toks = [VOCAB[c] for c in chunk if c in VOCAB]
            style = style_all[min(len(toks), len(style_all)) - 1]
            out = self.sess.run(None, {"tokens": np.array([[0, *toks, 0]], dtype=np.int64),
                                       "style": style.astype(np.float32),
                                       "speed": np.array([speed], dtype=np.float32)})
            audio.append(np.asarray(out[0]).ravel())
        return np.concatenate(audio)


def save_wav(path, audio):
    pcm = (np.clip(audio, -1, 1) * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("text"); ap.add_argument("--voice", default="af_heart")
    ap.add_argument("--speed", type=float, default=1.0); ap.add_argument("--out", default="out.wav")
    a = ap.parse_args()
    save_wav(a.out, Voice().speak(a.text, a.voice, a.speed))
    if MISSING: print("Not in dictionary (spelled out):", ", ".join(sorted(MISSING)))
    print("saved", a.out)
