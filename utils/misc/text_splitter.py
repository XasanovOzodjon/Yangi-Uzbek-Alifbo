import html

TELEGRAM_MAX_LEN = 4096


def split_text_chunks(text, max_len=TELEGRAM_MAX_LEN):
    if not text:
        return []
    if len(text) <= max_len:
        return [text]

    chunks = []
    remaining = text
    while len(remaining) > max_len:
        part = remaining[:max_len]
        split_idx = part.rfind("\n")
        if split_idx == -1 or split_idx < max_len // 2:
            split_idx = part.rfind(" ")
        if split_idx == -1:
            split_idx = max_len

        chunk = remaining[:split_idx].rstrip()
        if chunk:
            chunks.append(chunk)
        remaining = remaining[split_idx:].lstrip()

    if remaining:
        chunks.append(remaining)

    return chunks


def split_into_copyable_chunks(text: str, max_payload_len: int = TELEGRAM_MAX_LEN):
    """
    Matnni Telegram HTML 'code' (ustiga bosganda kopy qiladigan monospace) formatiga o'rab,
    Telegram maksimal uzunligi (4096 belgi) dan oshmagan bo'laklarga ajratadi.
    """
    if not text:
        return []

    # <code> va </code> teglari 13 ta belgi
    max_inner_len = max_payload_len - 13

    # Dastlab matnni taxminan 3800 belgidan bo'laklaymiz
    raw_chunks = split_text_chunks(text, max_len=3800)
    final_chunks = []

    for raw_chunk in raw_chunks:
        escaped = html.escape(raw_chunk, quote=False)
        if len(escaped) <= max_inner_len:
            final_chunks.append(f"<code>{escaped}</code>")
        else:
            # Agar & < > ko'p bo'lib oshib ketsa, kichikroq bo'laklarga ajratamiz
            smaller_parts = split_text_chunks(raw_chunk, max_len=1800)
            for part in smaller_parts:
                part_escaped = html.escape(part, quote=False)
                while len(part_escaped) > max_inner_len:
                    cutoff = max_inner_len // 6
                    head = part[:cutoff]
                    part = part[cutoff:]
                    final_chunks.append(f"<code>{html.escape(head, quote=False)}</code>")
                    part_escaped = html.escape(part, quote=False)
                if part_escaped:
                    final_chunks.append(f"<code>{part_escaped}</code>")

    return final_chunks

