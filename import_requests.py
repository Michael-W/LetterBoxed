"""Fetch words and the solution for the current NYT Letter Boxed puzzle.
    Append the words and the solutions to seperate files."""
import sys
import os
import json
import requests
from encrypt import decrypt_file, encrypt_file

def resource_path(relative_path):
    """ Get absolute path to resource """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

# Where the files are stored
PATH = resource_path("Data")

def sort_inplace(the_file: str) -> None:
    """Sorts the lines in a file in place."""
    with open(the_file, 'r', encoding='UTF-8') as ifile:
        lines = ifile.readlines()
    lines.sort()
    with open(the_file, 'w', encoding='UTF-8') as ofile:
        ofile.writelines(lines)

def fetch_todays_metadata(url: str) -> tuple[list[str], int, str, list[str]]:
    """Fetches today's words for the NYT Letter Boxed puzzle."""
    response = requests.get(url, timeout=10)
    data_start = response.text.index("window.gameData")
    metadata_start = data_start + response.text[data_start:].index("{")
    metadata_end = metadata_start + response.text[metadata_start:].index("}")
    metadata = json.loads(response.text[metadata_start:metadata_end + 1])
    return ([word.lower() for word in metadata['dictionary']],
            len(metadata['dictionary']),
            metadata['printDate'],
            metadata['ourSolution'],
            metadata['sides'])

def load_the_dictionary(dictionary) -> tuple[int, set]:
    """Read the file and store the words in a set
        after removing the timestamps. Return the set."""
    existing_words = set()
    with open(dictionary, 'r', encoding='UTF-8') as file:
        for line in file:
            word, _ = line.strip().split('\t')
            existing_words.add(word)
        return existing_words

def append_new_words(url: str, dictionary: str) -> tuple[
        int, int, int, str, list[str, str], list[str, str, str, str], str]:
    """Append new words to the file, with a time stamp.
        Return numbers for logging."""
    metadata = fetch_todays_metadata(url)
    new_words: int = sorted(metadata[0])
    metadata_word_count: int = metadata[1]
    letterbox_date: str = metadata[2]
    solution: list[str, str] = metadata[3]
    sides: list[str, str, str, str] = metadata[4]
    signature: str = ''.join(sorted(set(''.join(sides))))
    new_word_count = 0
    existing_words = sorted(load_the_dictionary(dictionary))
    with open(dictionary, 'a', encoding='UTF-8') as file:
        new_word_count = 0
        for word in new_words:
            # If the word is not in the dictionary,
            # append it with the current date and time
            if word not in existing_words:
                file.write(f"{word}\t{letterbox_date}\n")
                new_word_count += 1
    sort_inplace(dictionary)
    return (new_word_count,
            len(existing_words) + new_word_count,
            metadata_word_count - new_word_count,
            letterbox_date,
            solution,
            sides,
            signature)

def main():
    """Fetches words for the current NYT Letter Boxed puzzle,
        appends them to a file, and logs the results."""
    # Facts
    dictionary_file = os.path.join(PATH, "daily_dictionaries.txt")
    log_file = os.path.join(PATH, "import_requests.log")
    solution_file = os.path.join(PATH, "letterboxed_solutions.txt")
    letter_box_url = "https://www.nytimes.com/puzzles/letter-boxed"
    # Action
    word_counts = append_new_words(letter_box_url, dictionary_file)
    # Save the solution to the top of the solutions file.
    decrypt_file(solution_file)
    with open(solution_file, 'r+', encoding='UTF-8') as file:
        content = file.readlines()
        letterbox_date = word_counts[3]
        solution = word_counts[4]
        sides = word_counts[5]
        signature = word_counts[6]
        file_line = f"{letterbox_date}*{solution}*{sides}*{signature}\n".lower()
        content.insert(0, file_line.rstrip('\r\n') + '\n')
        file.seek(0, 0)
        file.writelines(content)
    encrypt_file(solution_file)
    # Save the log message to the top of the log file.
    log_message = " ".join(f"{word_counts[3]} {word_counts[0]:4,d} words added. "
                   f"{word_counts[2]:4,d} words were already there. "
                   f"Now {word_counts[1]:7,d} words in the dictionary.\n".split())
    with open(log_file, 'r+', encoding='UTF-8') as log:
        content = log.readlines()
        content.insert(0, log_message.rstrip('\r\n') + '\n')
        # Trim the log file after 100 entries
        content = content[:100]
        log.seek(0, 0)
        log.writelines(content)
        log.truncate()

if __name__ == "__main__":
    main()
