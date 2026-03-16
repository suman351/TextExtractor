import re


def is_hindi(text):
    # Check if more than 10% of characters are Devanagari
    hindi_chars = len(re.findall(r'[\u0900-\u097F]', text))
    return hindi_chars > (len(text) * 0.1)


def parse_questions(text):
    """
    Parse raw OCR text into Hindi / English question blocks.

    Special handling:
    Some questions have numbered statements 1, 2, 3, 4 and then
    options (a), (b), (c), (d) like "केवल 1 और 2". Because the OCR
    text contains "1.", "2.", "3." inside the same question, a simple
    split on (?=\\d+\\.) breaks the question into many small pieces.

    To handle this, we:
    1. Split on (?=\\d+\\.) as before.
    2. Detect any block that contains options (a)/(b)/(c)/(d).
    3. For each such options‑block, merge it together with a few
       preceding blocks (the intro + numbered statements) into a
       single question block.
    4. Any remaining blocks become standalone questions.
    """

    # 1) Split by any digit followed by a period (as before)
    blocks = re.split(r'(?=\d+\.)', text)

    # Pre‑clean all blocks once
    cleaned_blocks = [b.strip() for b in blocks]

    # Helper: detect if a block contains options like (a) .. (d)
    def has_mcq_options(block: str) -> bool:
        # Covers "(a)" or "(A)" etc., even if OCR drops spaces
        return bool(re.search(r'\([a-dA-D]\)', block))

    # Helper: trim a block so that it only contains the question stem
    # and options up to the line containing option (d). Anything after
    # (d) is typically page codes, English duplicates, etc., which we drop.
    def clean_mcq_block(block: str) -> str:
        lines = block.splitlines()
        cleaned_lines = []
        saw_option_a = False
        saw_option_d = False

        for line in lines:
            # Drop obvious footer / noise lines from the booklet
            stripped = line.strip()
            if not stripped:
                # Skip leading empty lines; keep internal blanks once started
                if not cleaned_lines:
                    continue
            if (
                "VGYH-U-FGT" in stripped  # booklet code
                or "ROUGH WORK" in stripped
                or "SPACE FOR" in stripped
            ):
                continue

            # Skip leading empty lines
            if not cleaned_lines and not stripped:
                continue

            cleaned_lines.append(line)

            if re.search(r'\([aA]\)', line):
                saw_option_a = True
            if re.search(r'\([dD]\)', line):
                saw_option_d = True
                break

        # If we never even saw option (a), return original block
        if not saw_option_a:
            return block.strip()

        result = "\n".join(cleaned_lines).strip()
        return result

    n = len(cleaned_blocks)

    # 2) Build groups where an options‑block pulls a few previous blocks
    assigned = [False] * n
    groups = {}  # start_index -> list of indices belonging to that question

    option_indices = [i for i, blk in enumerate(cleaned_blocks) if has_mcq_options(blk)]

    for opt_idx in option_indices:
        if assigned[opt_idx]:
            continue

        group = [opt_idx]

        # Look backwards and pull in up to 4 preceding non‑trivial blocks.
        # This typically captures: intro + 3 numbered statements.
        j = opt_idx - 1
        while j >= 0 and len(group) < 5:
            if assigned[j]:
                break

            prev = cleaned_blocks[j]
            if len(prev) < 30:  # skip tiny / noisy chunks
                j -= 1
                continue

            # We expect these to be statement‑like blocks such as "1.", "2.", "3."
            # or an intro paragraph. We include them unconditionally until the limit.
            group.insert(0, j)
            j -= 1

        start = group[0]
        for idx in group:
            assigned[idx] = True
        groups[start] = group

    hindi_qs = []
    english_qs = []

    # 3) Walk through blocks in order and emit merged / standalone questions.
    #    Only keep blocks that actually look like MCQs (have (a)/(b)/(c)/(d)).
    i = 0
    while i < n:
        if i in groups:
            # Merge all blocks in this group into one question
            indices = groups[i]
            merged = "\n".join(cleaned_blocks[idx] for idx in indices)
            if len(merged) >= 30 and has_mcq_options(merged):
                merged = clean_mcq_block(merged)
                if is_hindi(merged):
                    hindi_qs.append(merged)
                else:
                    english_qs.append(merged)
            i = indices[-1] + 1
            continue

        if assigned[i]:
            # This index was merged into a group whose start < i
            i += 1
            continue

        block = cleaned_blocks[i]
        if len(block) >= 30 and has_mcq_options(block):
            block = clean_mcq_block(block)
            if is_hindi(block):
                hindi_qs.append(block)
            else:
                english_qs.append(block)

        i += 1

    return hindi_qs, english_qs