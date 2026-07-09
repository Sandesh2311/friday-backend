import urllib.parse

def parse_and_search(query):
    """
    Parses a web search command and returns the URL for a Google search query.
    """
    c = query.lower()
    search_term = query
    
    # Strip common web search prefixes
    prefixes = [
        "web search",
        "search on google for",
        "search on google",
        "search google for",
        "search google",
        "search for",
        "google search",
        "google"
    ]
    
    for prefix in prefixes:
        if c.startswith(prefix):
            search_term = query[len(prefix):].strip()
            break
            
    encoded_query = urllib.parse.quote(search_term)
    return {
        "type": "action",
        "data": f"https://www.google.com/search?q={encoded_query}"
    }
