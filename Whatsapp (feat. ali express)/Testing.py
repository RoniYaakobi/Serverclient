import os
import time

def print_centered(text):
    """Center text based on terminal width."""
    terminal_width = os.get_terminal_size().columns
    padding = (terminal_width - len(text)) // 2
    return " " * padding + text

def display_text(lines, blink_duration=5):
    """
    Display multiple lines of text.
    Some lines blink while others remain static.
    """
    # Clear the terminal and reset cursor to top
    print("\033[2J\033[H", end="")

    # Pre-compute centered lines
    centered_lines = [(print_centered(line), is_blinking) for line, is_blinking in lines]

    # Print all lines initially (static and blinking)
    for line, is_blinking in centered_lines:
        print(line)

    # Manage blinking lines
    blinking_indices = [i for i, (_, is_blinking) in enumerate(lines) if is_blinking]

    end_time = time.time() + blink_duration
    while time.time() < end_time:
        # Turn blinking lines visible
        for idx in blinking_indices:
            line = centered_lines[idx][0]
            print(f"\033[{idx + 1}H\033[5m{line}\033[0m")  # Move cursor and print blinking line
        time.sleep(0.5)

        # Clear blinking lines
        for idx in blinking_indices:
            line = centered_lines[idx][0]
            print(f"\033[{idx + 1}H{' ' * len(line)}")  # Move cursor and clear line
        time.sleep(0.5)

    # Restore cursor to the bottom after blinking ends
    print(f"\033[{len(lines) + 1}H")

# Example usage
lines = [
    ("Welcome to the program!", False),  # Static line
    ("This line blinks.", True),        # Blinking line
    ("Stay tuned!", False),             # Static line
    ("Another blinking line!", True)    # Blinking line
]

display_text(lines, blink_duration=5)
