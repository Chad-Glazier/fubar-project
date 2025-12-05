import re

def loose_compare(main_string: str, search_string: str) -> bool:
    """
    Check if search_string is loosely contained in main_string.
    
    Args:
        main_string: The string to search within
        search_string: The string to search for
        
    Returns:
        bool: True if search_string is loosely contained in main_string
    """
    if not search_string:
        return True
    
    main_lower = main_string.lower()
    search_lower = search_string.lower()
    
    # Direct substring match
    if search_lower in main_lower:
        return True
    
    # Extract words from both strings
    main_words = re.findall(r'\b\w+\b', main_lower)
    search_words = re.findall(r'\b\w+\b', search_lower)
    
    # All distinct words from `search_string` are in `main_string`
    if search_words:
        search_set = set(search_words)
        main_set = set(main_words)
        
        if search_set.issubset(main_set):
            return True
    
    # Try matching words in any order
    for word in search_words:
        if word not in main_lower:
            return False
        
    return bool(search_words)
