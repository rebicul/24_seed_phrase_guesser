
# Understanding the Bitcoin Seed Phrase Guesser

## Overview

This document explains the purpose and functionality of the Python program `seed_guesser.py`, which was designed to systematically search for a Bitcoin seed phrase given a known set of 24 words in scrambled order.

## The Challenge: Guessing a 24-Word Seed Phrase

The inspiration for this program comes directly from the challenge posed in the article [“Guess My 12 And 24 Word Seed Phrases”](https://www.whatisbitcoin.com/security/guess-my-seed-phrase#Guess_My_12_And_24_Word_Seed_Phrases). The article highlights the immense security provided by BIP-39 mnemonic seed phrases, particularly those with 24 words.

The core challenge is this: if you have a set of 24 words that constitute a Bitcoin seed phrase, but you don't know their correct order, how would you find the specific arrangement that generates a target Bitcoin address?

The mathematical reality is that for 24 unique words, there are:

```
24! = 620,448,401,733,239,439,360,000
```

This is an astronomically large number, making a complete brute-force search practically impossible with current technology. This program demonstrates the structure and scale of such a challenge.


## Program Features

### Systematic Permutation Generation
Uses Python's `itertools.permutations` to systematically generate every unique permutation without duplicates or excess memory usage.

### BIP-39 Validation
Before wallet derivation, each permutation is validated using the BIP-39 checksum to ensure it's a legitimate mnemonic, saving unnecessary computation.

### HD Wallet Derivation
Uses the `hdwallet` library to convert the seed into addresses using common derivation paths (e.g., BIP-84 Native SegWit). If the derived address matches the target address, the correct permutation has been found.

### Checkpointing (Progress Saving)
Periodically saves the current permutation index to allow safe resumption after crashes or manual termination.


## Function Documentation

### `save_progress(count, job_id)`
- Saves how many permutations have been checked so far for a given `job_id`.
- Creates a file: `progress_checkpoint_{job_id}.txt`.

### `load_progress(job_id)`
- Loads the last saved checkpoint count from file.
- Returns 0 if no file exists (i.e., first run).

### `check_permutation(word_list_permutation, target_address, mnemonic_checker, derivation_paths)`
- Builds a 24-word phrase from the permutation.
- Validates it using BIP-39 rules.
- Derives Bitcoin addresses using HD wallet paths.
- Compares derived address to the target.
- Returns `(True, phrase)` if match is found; otherwise, `(False, None)`.

### `main()`
- Loads checkpoint.
- Generates permutations of the scrambled words.
- Checks each permutation against the target address.
- Saves progress periodically.


## Limitations and Feasibility

Even with optimizations and checkpointing, brute-forcing a 24-word phrase remains computationally infeasible. This project is a demonstration tool for:
- Understanding the scale of the BIP-39 seed space.
- Testing subset guesses when some word positions are known.
- Showcasing efficient brute-force design with resume capability.

**Not intended or suitable for recovering unknown seed phrases without significant prior knowledge.**


## License

MIT License
