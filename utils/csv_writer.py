import os


def save_extracted_questions(hindi_data, english_data):
    """
    Save extracted Hindi and English questions into plain-text files
    in the `output` folder.
    """
    os.makedirs("output", exist_ok=True)

    with open("output/hindi_questions.txt", "w", encoding="utf-8") as f:
        for i, q in enumerate(hindi_data, 1):
            f.write(f"--- Hindi Question {i} ---\n{q}\n\n")

    with open("output/english_questions.txt", "w", encoding="utf-8") as f:
        for i, q in enumerate(english_data, 1):
            f.write(f"--- English Question {i} ---\n{q}\n\n")

    print(
        f"✅ Extraction complete: {len(hindi_data)} Hindi and {len(english_data)} English questions saved to 'output/'."
    )