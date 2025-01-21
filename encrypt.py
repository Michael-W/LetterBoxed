'''This module provides functions to encrypt and decrypt a file using a Caesar cipher.'''
import random

def encrypt_file(file_path):
    '''Encrypts a file using a random shift for a Caesar cipher.
       The shift is stored as the first line of the file.'''
    key = random.randint(1, 25)  # Generate a random shift key between 1 and 25
    encrypted_lines = [f"{key}\n"]  # Store the key as the first line

    with open(file_path, 'r', encoding='utf-8') as ifile:
        for line in ifile:
            if line.strip().isdigit():
                return  # Exit if the first line is the key, its already encrypted.
            encrypted_line = ''
            for char in line:
                if char.isalpha():
                    # This works only for a text file with English letters.
                    encrypted_char = chr((ord(char.lower()) - ord('a') + key) % 26 + ord('a'))
                    encrypted_line += encrypted_char
                else:
                    encrypted_line += char
            encrypted_lines.append(encrypted_line)

    with open(file_path, 'w', encoding='utf-8') as ofile:
        ofile.writelines(encrypted_lines)

def decrypt_file(file_path):
    '''Decrypts a file that was encrypted using the encrypt_file function.'''
    with open(file_path, 'r', encoding='utf-8') as ifile:
        lines = ifile.readlines()

    try:
        key = int(lines[0])  # The first line is the key
    except ValueError:       # If the first line is not a number, the file
        return               # is not encrypted, so don't do anything

    decrypted_lines = []

    for line in lines[1:]:  # Skip the first line which is the key
        decrypted_line = ''
        for char in line:
            if char.isalpha():
                decrypted_char = chr((ord(char.lower()) - ord('a') - key + 26) % 26 + ord('a'))
                decrypted_line += decrypted_char
            else:
                decrypted_line += char
        decrypted_lines.append(decrypted_line)

    with open(file_path, 'w', encoding='utf-8') as ofile:
        ofile.writelines(decrypted_lines)
