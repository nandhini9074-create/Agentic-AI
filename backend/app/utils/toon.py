import re
from typing import Dict, Any, List

def escape_val(val: Any) -> str:
    """
    Safely escape values by collapsing newlines/excess spaces and escaping 
    pipe (|) and equal (=) signs to prevent structured format corruption.
    """
    if val is None:
        return ""
    s = str(val)
    # Collapse all newlines, tabs, and repeating spaces into a single space
    s = re.sub(r'\s+', ' ', s).strip()
    # Escape special format tokens
    s = s.replace("|", "\\|").replace("=", "\\=")
    return s

def unescape_val(s: str) -> str:
    """Restore escaped pipes and equals signs back to their original representation."""
    return s.replace("\\|", "|").replace("\\=", "=")

def dict_to_toon_line(entity: str, data: Dict[str, Any]) -> str:
    """
    Converts a flat dictionary of key-value properties into a single 
    structured TOON format line for the specified entity name.
    
    Output Format: entity|key1=value1|key2=value2
    """
    parts = [escape_val(entity)]
    for k, v in data.items():
        escaped_k = escape_val(k)
        escaped_v = escape_val(v)
        parts.append(f"{escaped_k}={escaped_v}")
    return "|".join(parts)

def parse_toon_line(line: str) -> Dict[str, Any]:
    """
    Parses a single flat-pipe TOON line back into its entity name 
    and a flat dictionary of unescaped key-value properties.
    """
    line = line.strip()
    if not line:
        return {"entity": None, "properties": {}}
    
    # Split on pipe character (|) ONLY if not preceded by an escape backslash (\)
    parts = re.split(r'(?<!\\)\|', line)
    
    entity = unescape_val(parts[0])
    properties = {}
    for p in parts[1:]:
        if "=" in p:
            # Split on the first equals sign (=) ONLY if not preceded by an escape backslash (\)
            kv_parts = re.split(r'(?<!\\)=', p, maxsplit=1)
            if len(kv_parts) == 2:
                k = unescape_val(kv_parts[0])
                v = unescape_val(kv_parts[1])
                properties[k] = v
    return {"entity": entity, "properties": properties}

def parse_toon_string(toon_str: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    Parses an entire multi-line flat-pipe TOON string into groups categorized by entity type.
    """
    grouped_entities = {}
    for line in toon_str.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parsed = parse_toon_line(line)
        entity = parsed["entity"]
        if entity:
            if entity not in grouped_entities:
                grouped_entities[entity] = []
            grouped_entities[entity].append(parsed["properties"])
    return grouped_entities

def serialize_rag_context_to_toon(name: str, query: str, chunks: List[Dict[str, Any]], pages: List[Dict[str, Any]] = None) -> str:
    """
    Serializes a profile target name, user query, RAG candidate chunks, 
    and full crawled pages into a token-optimized multi-line TOON block.
    
    Saves significant token space compared to raw text block headers or JSON serialization.
    """
    lines = []
    
    # 1. System metadata
    lines.append(dict_to_toon_line("meta", {
        "format": "Flat-Pipe TOON",
        "version": "1.0",
        "optimization": "token-efficient"
    }))
    
    # 2. User Query context
    lines.append(dict_to_toon_line("user", {
        "target_name": name,
        "query": query
    }))
    
    # 3. Similarity Context Chunks (RAG)
    if chunks:
        for idx, chunk in enumerate(chunks, 1):
            lines.append(dict_to_toon_line("ctx", {
                "id": idx,
                "chunk_id": chunk.get("chunk_id", f"chunk_{idx}"),
                "score": chunk.get("rerank_score") or chunk.get("distance") or 0.0,
                "source": chunk.get("source_url", "Unknown"),
                "content": chunk.get("content", "")
            }))
            
    # 4. Scraped Full Page Context (Docs)
    if pages:
        for idx, page in enumerate(pages, 1):
            lines.append(dict_to_toon_line("doc", {
                "id": idx,
                "title": page.get("title", "Web Page"),
                "source": page.get("source_url", "Unknown"),
                "content": page.get("visible_text", "")[:4000] # Limit size to maintain token budget
            }))
            
    # 5. Task description instruction
    lines.append(dict_to_toon_line("task", {
        "type": "synthesis",
        "action": "Generate structured professional profile"
    }))
    
    return "\n".join(lines)
