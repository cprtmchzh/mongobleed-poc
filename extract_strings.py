import re

def extract_ascii_strings(data: bytes, min_len: int = 4):
    pattern = rb"[ -~]{" + str(min_len).encode() + rb",}"
    return [m.decode("ascii", errors="ignore") for m in re.findall(pattern, data)]

def extract_utf16le_strings(data: bytes, min_len: int = 4):
    pattern = rb"(?:[\x20-\x7e]\x00){" + str(min_len).encode() + rb",}"
    out = []
    for m in re.findall(pattern, data):
        try:
            out.append(m.decode("utf-16le"))
        except UnicodeDecodeError:
            pass
    return out

with open("leaked.bin", "rb") as f:
    data = f.read()

ascii_part = extract_ascii_strings(data)
utf16_part = extract_utf16le_strings(data)

with open("parsed_strings.txt", "w", encoding="utf-8") as f:
    f.write("=== ASCII ===\n")
    for s in ascii_part:
        f.write(s + "\n")

    f.write("\n=== UTF-16LE ===\n")
    for s in utf16_part:
        f.write(s + "\n")