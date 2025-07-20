
import itertools
from mnemonic import Mnemonic
from hdwallet import HDWallet
import binascii
import sys
import time # Import the time module for measuring performance
import os   # Import os module for file operations

# --- ANSI Escape Codes for Styling ---
# These codes might not work in all terminals (e.g., older Windows Command Prompt)
# but are widely supported in modern terminals (macOS Terminal, Linux terminals, VS Code terminal).
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_RED = "\033[91m"
COLOR_CYAN = "\033[96m" # New color for resume message
STYLE_BOLD = "\033[1m"
STYLE_RESET = "\033[0m"

# --- Configuration ---
# The scrambled words provided by the user
SCRAMBLED_WORDS = [
    "grab", "merit", "chuckle", "can", "island", "wash", "floor", "car",
    "exit", "mother", "box", "festival", "october", "odor", "camp",
    "country", "trial", "nephew", "coil", "fabric", "galaxy", "napkin",
    "appear", "apple"
]

# The target Bitcoin address (Native SegWit - bc1q)
TARGET_ADDRESS = "bc1qxsd68d42agvykdueutm228uzn4s2g9qp2kk7t8"

# BIP-39 language for the wordlist
BIP39_LANGUAGE = "english"

# Common derivation paths for Native SegWit (P2WPKH) addresses (BIP-84)
DERIVATION_PATHS = [
    "m/84'/0'/0'/0/0", # First Native SegWit receive address (account 0, index 0)
    "m/84'/0'/0'/0/1", # Second Native SegWit receive address (account 0, index 1)
    "m/84'/0'/0'/0/2", # Third Native Native SegWit receive address (account 0, index 2)
    "m/84'/0'/0'/1/0", # First Native SegWit change address (account 0, index 0)
]

# --- Checkpointing Configuration ---
CHECKPOINT_FILE = "progress_checkpoint.txt"
# Save progress every X permutations. A larger number means less frequent disk writes.
# For a 2012 MBP, 100,000,000 might still be a long time between saves.
# You can adjust this based on how often you want to save progress.
SAVE_PROGRESS_INTERVAL = 100_000 

# --- Script Logic ---
def save_progress(count):
    """Saves the current permutation count to a checkpoint file."""
    try:
        with open(CHECKPOINT_FILE, "w") as f:
            f.write(str(count))
        sys.stdout.write(f"\n{COLOR_CYAN}Progress saved: {count:,} permutations.{STYLE_RESET}\n")
        sys.stdout.flush()
    except Exception as e:
        sys.stdout.write(f"\n{COLOR_RED}Error saving progress: {e}{STYLE_RESET}\n")
        sys.stdout.flush()

def load_progress():
    """Loads the last saved permutation count from a checkpoint file."""
    if os.path.exists(CHECKPOINT_FILE):
        try:
            with open(CHECKPOINT_FILE, "r") as f:
                count = int(f.read().strip())
            # Removed print statement here, it will be handled in main()
            return count
        except (ValueError, IOError) as e:
            sys.stdout.write(f"{COLOR_RED}Error loading progress: {e}. Starting from beginning.{STYLE_RESET}\n")
            sys.stdout.flush()
            return 0
    return 0

def check_permutation(word_list_permutation, target_address, mnemonic_checker, derivation_paths):
    """
    Checks if a given permutation of words forms a valid BIP-39 mnemonic phrase
    and if it generates the target Bitcoin address.

    Args:
        word_list_permutation (list): A list of 24 words in a specific order.
        target_address (str): The Bitcoin address to match.
        mnemonic_checker (Mnemonic): An initialized Mnemonic object for checksum validation.
        derivation_paths (list): A list of BIP-39 derivation paths to check.

    Returns:
        tuple: (True, mnemonic_phrase) if a match is found, otherwise (False, None).
    """
    mnemonic_phrase = " ".join(word_list_permutation)

    try:
        if not mnemonic_checker.check(mnemonic_phrase):
            return False, None
    except Exception:
        return False, None

    try:
        seed_bytes = mnemonic_checker.to_seed(mnemonic_phrase)
        seed_hex = binascii.hexlify(seed_bytes).decode('utf-8')
    except Exception:
        return False, None

    # Corrected logic: Initialize HDWallet and set seed for EACH derivation path
    # to prevent stacking of paths.
    for path in derivation_paths:
        try:
            wallet = HDWallet(symbol="BTC")
            wallet.from_seed(seed_hex) # Set the seed for each path check
            wallet.from_path(path)
            derived_address = wallet.get_address()

            if derived_address == target_address:
                return True, mnemonic_phrase
            
        except Exception:
            # Continue to the next path if there's an error with this one
            pass

    return False, None

def main():
    print(f"{STYLE_BOLD}{COLOR_GREEN}Starting systematic permutation search for target address:{STYLE_RESET} {TARGET_ADDRESS}")
    print(f"{STYLE_BOLD}Total words in list:{STYLE_RESET} {len(SCRAMBLED_WORDS)}")
    print(f"{STYLE_BOLD}Checking derivation paths:{STYLE_RESET} {', '.join(DERIVATION_PATHS)}")
    print(f"{COLOR_YELLOW}{'-' * 60}{STYLE_RESET}") # Yellow separator line

    mnemonic_checker = Mnemonic(BIP39_LANGUAGE)
    
    # Load previous progress
    initial_loaded_progress = load_progress() # Load once at the beginning
    total_permutations_checked = initial_loaded_progress
    
    # Print resume message only if actually resuming
    if initial_loaded_progress > 0:
        sys.stdout.write(f"{COLOR_CYAN}Resuming from saved progress: {initial_loaded_progress:,} permutations.{STYLE_RESET}\n")
        sys.stdout.flush()

    # Record start time for performance calculation, adjusted for loaded progress
    start_time = time.time() 

    # Define how often to update the progress bar (e.g., every 100,000 permutations)
    PROGRESS_UPDATE_INTERVAL = 100_000 
    
    # Simple animation characters for visual feedback
    animation_frames = ['-', '\\', '|', '/']
    animation_index = 0

    # Generate all permutations of the scrambled words
    permutations_generator = itertools.permutations(SCRAMBLED_WORDS)

    # Skip permutations already checked if resuming
    if total_permutations_checked > 0:
        sys.stdout.write(f"{COLOR_CYAN}Skipping to {total_permutations_checked:,} permutations...{STYLE_RESET}\n")
        sys.stdout.flush()
        # Iterate through the generator without processing until the checkpoint is reached
        for _ in range(total_permutations_checked):
            try:
                next(permutations_generator)
            except StopIteration:
                # Handle case where saved count exceeds total permutations (e.g., file corrupted)
                sys.stdout.write(f"{COLOR_RED}Warning: Checkpoint count exceeds total permutations. Restarting from beginning.{STYLE_RESET}\n")
                sys.stdout.flush()
                total_permutations_checked = 0 # Reset count
                permutations_generator = itertools.permutations(SCRAMBLED_WORDS) # Re-initialize
                break # Exit skipping loop

    # Start processing from the current point
    for permutation in permutations_generator:
        total_permutations_checked += 1
        
        # Update progress more frequently
        if total_permutations_checked % PROGRESS_UPDATE_INTERVAL == 0:
            elapsed_time = time.time() - start_time
            # Calculate permutations per second using the initially loaded progress
            permutations_per_second = (total_permutations_checked - initial_loaded_progress) / elapsed_time if elapsed_time > 0 else 0 

            animation_index = (animation_index + 1) % len(animation_frames)
            current_frame = animation_frames[animation_index]

            sys.stdout.write(
                f"\r{COLOR_YELLOW}{current_frame}{STYLE_RESET} Checked {total_permutations_checked:,} permutations | "
                f"{permutations_per_second:,.2f} perms/sec "
            )
            sys.stdout.flush()
        
        # Save progress periodically
        if total_permutations_checked % SAVE_PROGRESS_INTERVAL == 0:
            save_progress(total_permutations_checked)

        found, correct_mnemonic = check_permutation(list(permutation), TARGET_ADDRESS, mnemonic_checker, DERIVATION_PATHS)

        if found:
            print(f"\n{STYLE_BOLD}{COLOR_GREEN}{'='*70}{STYLE_RESET}")
            print(f"{STYLE_BOLD}{COLOR_GREEN}🎉 MATCH FOUND! 🎉{STYLE_RESET}")
            print(f"{STYLE_BOLD}Correct Mnemonic Phrase:{STYLE_RESET} {correct_mnemonic}")
            print(f"{STYLE_BOLD}This phrase generates the target address:{STYLE_RESET} {TARGET_ADDRESS}")
            print(f"{STYLE_BOLD}{COLOR_GREEN}{'='*70}{STYLE_RESET}\n")
            # Save final progress on success
            save_progress(total_permutations_checked)
            return

    print(f"\n{COLOR_RED}Search completed. Target address not found with the given words and derivation paths.{STYLE_RESET}")
    # Remove checkpoint file if search completes without finding
    if os.path.exists(CHECKPOINT_FILE):
        os.remove(CHECKPOINT_FILE)
        sys.stdout.write(f"{COLOR_CYAN}Checkpoint file removed.{STYLE_RESET}\n")
        sys.stdout.flush()

if __name__ == "__main__":
    main()

