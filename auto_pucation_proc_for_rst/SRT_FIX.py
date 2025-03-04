import difflib
import re
import argparse

def load_file(filepath):
    """Load a file and return its content."""
    with open(filepath, "r", encoding="utf-8") as file:
        return file.read()

def load_srt_text(filepath):
    """Extract text content from an SRT file, ignoring timestamps and numbering."""
    with open(filepath, "r", encoding="utf-8") as file:
        lines = file.readlines()
    
    srt_texts = []
    for line in lines:
        line = line.strip()
        if "-->" not in line and not line.isdigit():
            srt_texts.append(line)
    return srt_texts

def extract_srt_segments(srt_filepath):
    """Extracts subtitle segments from an SRT file, including sequence number, timestamps, and text."""
    with open(srt_filepath, "r", encoding="utf-8") as file:
        lines = file.readlines()

    segments = []
    index = None
    timestamp = None
    text = []

    for line in lines:
        line = line.strip()

        if line.isdigit():
            if index is not None and timestamp and text:
                segments.append((index, timestamp, " ".join(text)))
            index = int(line)
            text = []
        elif "-->" in line:
            timestamp = line
        elif line:
            text.append(line)

    if index is not None and timestamp and text:
        segments.append((index, timestamp, " ".join(text)))

    return segments

def format_text_with_srt(original_text, srt_segments):
    """Formats the original text according to the SRT segments, keeping the correct timestamps and numbering."""
    original_text_cleaned = re.sub(r'\s+', ' ', original_text)  # Normalize spaces
    formatted_srt_text = []
    start_idx = 0

    for index, timestamp, srt_text in srt_segments:
        match = difflib.SequenceMatcher(None, original_text_cleaned[start_idx:], srt_text).find_longest_match(
            0, len(original_text_cleaned[start_idx:]), 0, len(srt_text))

        if match.size > 0:
            segment = original_text_cleaned[start_idx + match.a: start_idx + match.a + match.size]

            if match.a + match.size < len(original_text_cleaned) and original_text_cleaned[start_idx + match.a + match.size] in ",.!?":
                segment += original_text_cleaned[start_idx + match.a + match.size]

            formatted_srt_text.append(f"{index}\n{timestamp}\n{segment}\n")
            start_idx += match.a + match.size + 1

    return "\n".join(formatted_srt_text)

def save_file(filepath, content):
    """Save content to a file."""
    with open(filepath, "w", encoding="utf-8") as file:
        file.write(content)

def convert_txt_to_srt(txt_filepath, srt_filepath):
    """Convert a .txt file to .srt format."""
    with open(txt_filepath, "r", encoding="utf-8") as txt_file:
        content = txt_file.read()
    
    srt_content = content  # Basic RST formatting
    
    with open(srt_filepath, "w", encoding="utf-8") as rst_file:
        rst_file.write(srt_content)

def main():
    parser = argparse.ArgumentParser(description="Process any original text and SRT file.")
    parser.add_argument("original_text ", help="Path to the original text file")
    parser.add_argument("srt_file ", help="Path to the SRT file")
    parser.add_argument("output_txt ", help="Path to save the output TXT file")
    parser.add_argument("output_srt ", help="Path to save the output RST file")
    
    args = parser.parse_args()
    
    original_text = load_file(args.original_text)
    srt_segments = extract_srt_segments(args.srt_file)
    formatted_text = format_text_with_srt(original_text, srt_segments)
    save_file(args.output_txt, formatted_text)
    
    # Convert to RST format
    convert_txt_to_srt(args.output_txt, args.output_srt)
    
    print(f"Formatted text saved to: {args.output_txt}")
    print(f"RST file saved to: {args.output_srt}")

if __name__ == "__main__":
    main()
