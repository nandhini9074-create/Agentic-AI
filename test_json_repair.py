import json

def repair_truncated_json(text: str) -> str:
    text = text.strip()
    if not text:
        return "{}"
    
    start_idx = text.find('{')
    if start_idx == -1:
        return "{}"
    
    text = text[start_idx:]
    
    state = "normal"  # normal, string, escape
    stack = []
    clean_up_to = 0
    
    i = 0
    while i < len(text):
        char = text[i]
        
        if state == "escape":
            state = "string"
            i += 1
            continue
            
        if state == "string":
            if char == "\\":
                state = "escape"
            elif char == '"':
                state = "normal"
                clean_up_to = i + 1
            i += 1
            continue
            
        # normal state
        if char == '"':
            state = "string"
        elif char in ('{', '['):
            stack.append(char)
            clean_up_to = i + 1
        elif char in ('}', ']'):
            if stack:
                stack.pop()
            clean_up_to = i + 1
        elif char in (',', ':', ' ', '\n', '\r', '\t'):
            pass
        elif char.isalnum() or char in ('-', '.', 't', 'f', 'n'):
            clean_up_to = i + 1
            
        i += 1
        
    truncated_text = text[:clean_up_to].strip()
    
    while truncated_text and truncated_text[-1] in (',', ':', ' '):
        truncated_text = truncated_text[:-1].strip()
        
    open_stack = []
    i = 0
    state = "normal"
    while i < len(truncated_text):
        char = truncated_text[i]
        if state == "escape":
            state = "string"
            i += 1
            continue
        if state == "string":
            if char == "\\":
                state = "escape"
            elif char == '"':
                state = "normal"
            i += 1
            continue
        if char == '"':
            state = "string"
        elif char == '{':
            open_stack.append('{')
        elif char == '[':
            open_stack.append('[')
        elif char == '}':
            if open_stack and open_stack[-1] == '{':
                open_stack.pop()
        elif char == ']':
            if open_stack and open_stack[-1] == '[':
                open_stack.pop()
        i += 1
        
    closing_chars = []
    for op in reversed(open_stack):
        if op == '{':
            closing_chars.append('}')
        elif op == '[':
            closing_chars.append(']')
            
    return truncated_text + "".join(closing_chars)

# Test with our real-world truncated file
with open("d:/Agentic-AI/temp_sports_result.json", "r", encoding="utf-8") as f:
    data = json.load(f)

raw_val = data["data"]["raw"]
# Strip code fences from raw
if raw_val.startswith("```json"):
    raw_val = raw_val[7:].strip()
elif raw_val.startswith("```"):
    raw_val = raw_val[3:].strip()
if raw_val.endswith("```"):
    raw_val = raw_val[:-3].strip()

repaired = repair_truncated_json(raw_val)
print("REPAIRED STRING LENGTH:", len(repaired))
print("LAST 100 CHARS OF REPAIRED:", repaired[-100:])

try:
    parsed = json.loads(repaired)
    print("SUCCESSFULLY PARSED REPAIRED JSON!")
    print("Parsed profile name:", parsed["profile"]["name"])
    print("Parsed articles count:", len(parsed["profile"]["articles"]))
except Exception as e:
    print("FAILED TO PARSE REPAIRED JSON:", e)
