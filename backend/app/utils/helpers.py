import re
import unicodedata

def clean_text(text: str) -> str:
    """
    Cleans raw scraped text content by removing duplicates, ads, navigation, 
    normalizing whitespace, encoding, and unicode characters.
    """
    if not text:
        return ""

    # Normalize unicode characters to NFKC (standard compatibility normalization)
    text = unicodedata.normalize("NFKC", text)

    # Normalize line breaks and remove consecutive duplicate empty lines
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Remove headers/footers/navigation patterns (common menu texts)
    nav_patterns = [
        r"(?i)\b(skip to content|sign in|join now|privacy policy|terms of service|cookie policy)\b",
        r"(?i)\b(all rights reserved|copyright ©|agree & join|agree and join)\b",
        r"(?i)\b(home|about|services|contact|blog|portfolio|careers|pricing|help|faq)\b\s*\|\s*",
        r"(?i)\b(facebook|twitter|instagram|linkedin|github|youtube|social media)\b"
    ]
    for pattern in nav_patterns:
        text = re.sub(pattern, "", text)

    # Split lines, strip each line, remove empty lines
    lines = [line.strip() for line in text.split("\n")]
    cleaned_lines = []
    seen_lines = set()

    for line in lines:
        if not line:
            continue
        
        # Deduplicate identical lines (e.g. repeated navigation menus or footers)
        # We only deduplicate short lines that are exact repeats (longer content might naturally repeat phrases, but exact identical lines are usually navigation elements)
        if len(line) < 100:
            normalized_line = line.lower()
            if normalized_line in seen_lines:
                continue
            seen_lines.add(normalized_line)

        cleaned_lines.append(line)

    # Join cleaned lines and normalize whitespaces in between words
    cleaned_text = "\n".join(cleaned_lines)
    cleaned_text = re.sub(r"[ \t]+", " ", cleaned_text) # collapse multiple spaces/tabs on the same line
    
    return cleaned_text.strip()
