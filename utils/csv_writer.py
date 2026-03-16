import os


def save_extracted_questions(hindi_data, english_data):
    """
    Save only extracted Hindi questions into a plain-text file
    in the `output` folder.

    `english_data` is accepted but intentionally ignored, because
    the current workflow only needs Hindi questions.
    """
    os.makedirs("output", exist_ok=True)

    # Save Hindi questions
    with open("output/hindi_questions.txt", "w", encoding="utf-8") as f:
        for i, q in enumerate(hindi_data, 1):
            f.write(f"--- Hindi Question {i} ---\n{q}\n\n")

    print(
        f"✅ Extraction complete: {len(hindi_data)} Hindi questions saved to 'output/hindi_questions.txt'."
    )