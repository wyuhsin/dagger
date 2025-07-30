import shutil

def get_visual_width(s):
    """Calculates the visual width of a string, accounting for wide characters."""
    width = 0
    for char in s:
        if 0x1100 <= ord(char) <= 0x115F or \
           0x2E80 <= ord(char) <= 0xA4CF or \
           0xAC00 <= ord(char) <= 0xD7A3 or \
           0xF900 <= ord(char) <= 0xFAFF or \
           0xFE10 <= ord(char) <= 0xFE19 or \
           0xFE30 <= ord(char) <= 0xFE4F or \
           0xFF00 <= ord(char) <= 0xFF60 or \
           0xFFE0 <= ord(char) <= 0xFFE6:
            width += 2
        else:
            width += 1
    return width

def print_in_columns(items):
    """Prints a list of items in multiple columns, respecting character width."""
    if not items:
        return

    try:
        terminal_width = shutil.get_terminal_size().columns
    except OSError:
        terminal_width = 80

    numbered_items = [f"{i+1}. {name}" for i, name in enumerate(items)]
    max_visual_width = max(get_visual_width(item) for item in numbered_items) if numbered_items else 0
    col_width = max_visual_width + 4
    num_cols = max(1, terminal_width // col_width)
    num_rows = (len(numbered_items) + num_cols - 1) // num_cols

    for r in range(num_rows):
        line_parts = []
        for c in range(num_cols):
            index = r + c * num_rows
            if index < len(numbered_items):
                item = numbered_items[index]
                padding = ' ' * (col_width - get_visual_width(item))
                line_parts.append(item + padding)
        print("".join(line_parts))
