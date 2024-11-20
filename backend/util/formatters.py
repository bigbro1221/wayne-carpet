
class LogColors:
    RESET = "\033[0m"
    BLUE = "\033[34m"
    ORANGE = "\033[33m"  # Orange is represented as yellow in ANSI
    RED = "\033[31m"


def format_content(content):
    # Define special characters for MarkdownV2 that need to be escaped
    special_characters = r'([_*\[\]()~`>#+\-=|{}.!-])'
    
    # Escape special characters with a backslash
    formatted_content = re.sub(special_characters, r'\\\1', content)
    
    # Replace **bold** syntax with MarkdownV2-compatible bold (single *)
    formatted_content = formatted_content.replace("**", "*")
    
    return formatted_content

