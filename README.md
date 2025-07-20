
# Seed Phrase Guesser

## Overview

This program was created as an educational demonstration of the immense difficulty in guessing a valid 12 or 24-word Bitcoin seed phrase, as discussed in the article ["Guess My Seed Phrase"](https://www.whatisbitcoin.com/security/guess-my-seed-phrase#Guess_My_12_And_24_Word_Seed_Phrases).

The article outlines a challenge where the author dares anyone to guess a seed phrase that holds Bitcoin funds, showcasing how impractical and computationally infeasible it is to brute-force such phrases. This program simulates such a brute-force attempt using a known wordlist and a target Bitcoin address, helping illustrate the scale of the problem.

**Disclaimer:** This project is for educational purposes only. Attempting to hack or guess someone's private keys without permission is illegal and unethical.

---

## Function Descriptions

### `save_progress(permutation_index)`
Saves the current index of the permutation being tested into a file (`progress.txt`). This allows the script to resume from the last saved state in case of interruption.

### `load_progress()`
Reads the `progress.txt` file to determine where the previous run left off, enabling the resume functionality to work efficiently.

### `check_permutation(words)`
Accepts a permutation of words, generates a seed phrase using the BIP39 standard, and derives the associated Bitcoin address using HDWallet. It then checks if the address matches the target Bitcoin address.

### `main()`
Coordinates the loading of progress, permutation generation, and checking each permutation for a match. It also measures elapsed time and prints progress statistics.

---

## Configuration

- `SCRAMBLED_WORDS`: A list of 24 BIP39-compatible words used to generate permutations.
- `TARGET_ADDRESS`: The known Bitcoin address that the program is attempting to match through permutations.

---

## Limitations

This approach is not optimized for speed and is purely demonstrative. Brute-forcing 24-word permutations (24!) is computationally infeasible without astronomical resources.

---

## License

MIT License
