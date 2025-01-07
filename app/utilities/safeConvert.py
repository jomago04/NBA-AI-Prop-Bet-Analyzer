def safe_convert(cell_text, convert_type=float):
    """
    Safely converts a string to a number, returning 0 if conversion fails.
    
    Args:
        cell_text (str): The text to convert
        convert_type (type): The type to convert to (float or int)
    
    Returns:
        number: The converted number or 0 if conversion fails
    """
    try:
        # Remove any whitespace and handle empty strings
        cleaned_text = cell_text.strip()
        if not cleaned_text:
            return 0
        return convert_type(cleaned_text)
    except (ValueError, TypeError):
        return 0