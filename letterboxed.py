""" find solutions for nyt "letter boxed" """
import sys
import os
import ast
from tempfile import gettempdir

from tkinter import messagebox
from letterboxed_forms import InputForm, OutputForm
from encrypt import decrypt_file, encrypt_file

PATH = "\\\\texas\\Public\\LetterBoxed"
dictionary_file = os.path.join(PATH, "daily_dictionaries.txt")
solution_file = os.path.join(PATH, "letterboxed_solutions.txt")

SIDES = 4
LETTERS_ON_SIDE = 3

found_words = []
dictionary = {}
words_list = []

LOCK_FILE_DIR = os.path.join(gettempdir(), "LetterBoxed")
LOCK_FILE = os.path.join(LOCK_FILE_DIR, "#_lock_file_for_letterboxed_#.txt")

# Ensure the lock file directory exists
os.makedirs(LOCK_FILE_DIR, exist_ok=True)

# Check if the lock file exists
if os.path.exists(LOCK_FILE):
    messagebox.showerror("Error", "LetterBoxed is already running. Exiting.")
    sys.exit()

with open(LOCK_FILE, 'w', encoding='UTF-8'):
    pass

# Read the dictionary file and create a list of words without the dates.
with open(dictionary_file, 'r', encoding='UTF-8') as file:
    for line in file:
        words_list = [line.split('\t')[0].strip() for line in file]

def create_indexed_dictionary(words: list[str]) -> dict[str, list[str]]:
    """Create a dictionary with words grouped by their first two letters."""
    indexed_dictionary = {}
    for word in words:
        key = word[:2]
        indexed_dictionary.setdefault(key, []).append(word)
    return indexed_dictionary

dictionary: dict[str, list[str]] = create_indexed_dictionary(words_list)

def is_word(word: str) -> bool:
    """Checks if a word is present in the dictionary."""
    prefix = word[:2]
    return prefix in dictionary and word in dictionary[prefix]

def has_word_starting_with(prefix: str) -> bool:
    """Check if there are words starting with the given prefix."""
    if prefix[:2] in dictionary:
        words = dictionary[prefix[:2]]
        return any(word.startswith(prefix) for word in words)
    return False

def find_candidate_words(prefix: str, letters: str) -> list[str]:
    """Append each candidate to the prefix.
       Return words that start with the result."""
    return [prefix + letter for letter in letters if has_word_starting_with(
        prefix + letter)]

def find_next_letter_candidates(dname:  dict[str, int], exclude: int) -> str:
    """ Find the letters around the box excluding those on the current side """
    candidates = ''
    for x, y in dname.items():
        if x == exclude:
            for k, v in dname.items():
                if v != y:
                    candidates += k
    return candidates

def create_dictionary(named_as: list[str]) ->  dict[str, int]:
    """ For a key of each of the 12 letters say which side it is on """
    d = {}
    for i in range(SIDES):
        for j in range(LETTERS_ON_SIDE):
            d[named_as[i][j]] = i
    return d

def looking_for(word: str, dname: dict[str, int]) -> list[str]:
    """ For the last letter of a string add a candidate letter and return
        the results if there are words starting with the new string.
        If the string is a word add it to a list of words found. """
    start_with = word[-1]
    next_letter_candidates = find_next_letter_candidates(dname, start_with)
    clist = find_candidate_words(word, next_letter_candidates)
    for the_word in clist:
        if is_word(the_word):
            found_words.append(the_word)
    return clist

def find_words(letter_box) -> None:
    """ For each letter on the sides of the box
        find the words that start with it. """
    letter_side = create_dictionary(letter_box)
    matrix = []
    p_line = 0
    col = 0
    side = 0
    letter_on_side = 0
    for side in range(SIDES):
        for letter_on_side in range(LETTERS_ON_SIDE):
            word = letter_box[side][letter_on_side]
            matrix.append(looking_for(word, letter_side))
            while p_line != len(matrix):
                for col in range(len(matrix[p_line])):
                    word = matrix[p_line][col]
                    matrix.append(looking_for(word, letter_side))
                p_line += 1
            continue
    matrix.clear()

def find_pairs(word_counts: dict[str, int]) -> list[tuple[str, str]]:
    """ Find pairs of words with at least 12 unique letters """
    sorted_by_count = sorted(word_counts.items(), key=lambda x: x[1])
    reversed_sorted = sorted(sorted_by_count, key=lambda x: x[1], reverse=True)
    pairs = []
    for right_word, _ in reversed_sorted:
        if len(set(right_word)) >= 12:
            pairs.append((right_word, 'SINGLETON'))
            break
        for left_word, _ in sorted_by_count:
            if right_word[0] == left_word[-1] and \
                right_word != left_word and \
                    len(set(left_word + right_word)) >= 12:
                pairs.append((left_word, right_word))
    return sorted(pairs, key=lambda x: len(set(x[0] + x[1])))

def find_longest_words(pairs: list[tuple[str, str]]) -> tuple[int, int]:
    """ Find the longest words in the pairs and return the lengths. """
    longest_left = 0
    longest_right = 0
    for left_word, right_word in pairs:
        longest_left = max(longest_left, len(left_word))
        longest_right = max(longest_right, len(right_word))
    return (longest_left + 1, longest_right + 1)

def format_pairs(word_pairs: dict[str, list[str]]) -> tuple[int, tuple[str], list[str]]:
    """Return the number of pairs found a list of the pairs."""
    print_lines = []
    pairs = sorted(find_pairs(word_pairs), key=lambda x: len(x[0] + x[1]))
    num_rows = max(1, round((len(pairs)) // 2))
    num_cols = max(1, round((len(pairs)) // num_rows)) + 1
    fill  = find_longest_words(pairs)
    for row in range(num_rows):
        row_line = []
        for p in pairs[row * num_cols:(row + 1) * num_cols]:
            f = f"{len(p[0] + p[1])}: {p[0].ljust(fill[0])}{p[1].ljust(fill[1])}"
            row_line.append(f)
        display_line = ''.join(row_line).strip()
        if len(display_line) > 0:
            print_lines.append(display_line)
    match(len(pairs)):
        case 0: return (0, print_lines, ["", ""])
        case 1: return (1, print_lines, pairs[0])
        case _: return (len(pairs), print_lines, pairs[0])

def find_all_words(letter_box: list[str]) -> tuple[int, list[str], tuple[str, str]]:
    """ Does the work of finding words in the dictionary """
    find_words(letter_box)
    found_words.sort()
    uniqueness: dict[str, int] = {word: len(set(word)) for word in found_words}
    # sort the words by the number of unique letters in the word.
    ordered_dict: dict[str, int] = dict(
        sorted(uniqueness.items(), key=lambda x: (x[1], x[0])))
    # Format the pairs for display.
    return format_pairs(ordered_dict)

def get_solution(signature, first_pair) -> list[str]:
    """ Get the solution from the file. """
    decrypt_file(solution_file)
    with open(solution_file, 'r', encoding='UTF-8') as solutions:
        for solution in solutions:
            fields = solution.split('*')
            if fields[3].strip() == signature:
                encrypt_file(solution_file)
                return ast.literal_eval(fields[1])
    encrypt_file(solution_file)
    return first_pair

def process_data(data, input_form) -> None:
    """ Process the data from and to the form. """
    try:
        returned: tuple[int, list[str], tuple[str, str]] = find_all_words(data)
        pair_count: int = returned[0]
        print_lines: list[str] = returned[1]
        signature: str = ''.join(sorted(set(''.join(returned[2]))))
        answers: list[str] = get_solution(signature, returned[2])
        OutputForm(print_lines, answers, pair_count, input_form, LOCK_FILE)
    except Exception as e:
        if os.path.exists(LOCK_FILE):
            os.remove(LOCK_FILE)
        raise e

if __name__ == "__main__":
    form = InputForm(process_data)
    form.run()
if os.path.exists(LOCK_FILE):
    os.remove(LOCK_FILE)
