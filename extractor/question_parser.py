import re


def is_hindi(text):
    # Check if more than 10% of characters are Devanagari
    hindi_chars = len(re.findall(r'[\u0900-\u097F]', text))
    return hindi_chars > (len(text) * 0.1)


def parse_questions(text):
    """
    Parse raw OCR text into Hindi / English question blocks.

    New line-based strategy (more robust for UPSC-style MCQs):
    - Walk line by line instead of splitting big blocks.
    - Keep appending lines to the current question.
    - Once we have seen options (a)–(d), the *next* line that
      looks like a new question number (e.g. "4.") starts a
      new question.
    - This way, internal statement numbers "1.", "2.", "3."
      inside a question do NOT split it.
    """

    lines = text.splitlines()

    def is_noise(line: str) -> bool:
        s = line.strip()
        if not s:
            return False
        return (
            "VGYH-U-FGT" in s
            or "ROUGH WORK" in s.upper()
            or "SPACE FOR" in s.upper()
        )

    def line_has_option(line: str):
        m = re.search(r'\(([a-dA-D])\)', line)
        if m:
            return m.group(1).lower()
        return None

    def looks_like_question_start(line: str) -> bool:
        # line starting with digits + dot, e.g. "3." or "10."
        return bool(re.match(r'^\s*\d+\.', line))

    current_lines: list[str] = []
    options_seen: set[str] = set()
    questions: list[str] = []

    for raw_line in lines:
        if is_noise(raw_line):
            continue

        # Start a new question if:
        # - we already have a question with options,
        # - and this line looks like a new question number.
        if (
            current_lines
            and options_seen
            and looks_like_question_start(raw_line)
        ):
            block = "\n".join(current_lines).strip()
            if len(block) > 30:
                questions.append(block)
            current_lines = []
            options_seen = set()

        current_lines.append(raw_line)
        opt = line_has_option(raw_line)
        if opt:
            options_seen.add(opt)

    # Flush last question
    if current_lines and options_seen:
        block = "\n".join(current_lines).strip()
        if len(block) > 30:
            questions.append(block)

    # Helper: trim a block so that it only contains the question stem
    # and options up to the line containing option (d). Anything after
    # (d) is typically page codes, English duplicates, etc., which we drop.
    def clean_mcq_block(block: str) -> str:
        lines_local = block.splitlines()
        cleaned_lines = []
        saw_option_a = False
        saw_option_d = False

        for line in lines_local:
            stripped = line.strip()
            if not stripped and not cleaned_lines:
                continue
            if is_noise(line):
                continue

            cleaned_lines.append(line)

            if re.search(r'\([aA]\)', line):
                saw_option_a = True
            if re.search(r'\([dD]\)', line):
                saw_option_d = True
                break

        if not saw_option_a:
            return block.strip()

        return "\n".join(cleaned_lines).strip()

    hindi_qs: list[str] = []
    english_qs: list[str] = []

    for q in questions:
        cleaned = clean_mcq_block(q)
        if len(cleaned) < 30:
            continue
        if is_hindi(cleaned):
            hindi_qs.append(cleaned)
        else:
            english_qs.append(cleaned)

    return hindi_qs, english_qs