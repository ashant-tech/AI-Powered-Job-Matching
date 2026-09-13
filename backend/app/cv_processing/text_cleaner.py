import re


def clean_text(text: str) -> str:
    """
    Clean and normalize text from CVs.
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep important ones
    text = re.sub(r'[^\w\s\-\.\,\@\/\#]', '', text)
    
    # Normalize quotes
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace(''', "'").replace(''', "'")
    
    # Remove page numbers and headers (simple patterns)
    text = re.sub(r'Page \d+ of \d+', '', text)
    text = re.sub(r'\d+/\d+/\d+', '', text)  # Remove dates
    
    # Remove empty lines
    text = re.sub(r'\n\s*\n', '\n', text)
    
    return text.strip()

def extract_email(text: str) -> str | None:
    """
    Extract email address from text.
    """
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    return emails[0] if emails else None

def extract_phone(text: str) -> str | None:
    """
    Extract phone number from text.
    """
    phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
    phones = re.findall(phone_pattern, text)
    return phones[0] if phones else None

def extract_links(text: str) -> list:
    """
    Extract URLs from text.
    """
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    urls = re.findall(url_pattern, text)
    return urls

def normalize_skill_name(skill: str) -> str:
    """
    Normalize skill names for better matching.
    """
    skill = skill.lower().strip()
    
    # Common variations
    skill_variations = {
        'javascript': 'javascript',
        'js': 'javascript',
        'python': 'python',
        'py': 'python',
        'java': 'java',
        'react.js': 'react',
        'reactjs': 'react',
        'node.js': 'nodejs',
        'nodejs': 'nodejs',
        'c++': 'c++',
        'cpp': 'c++',
        'c#': 'c#',
        'csharp': 'c#',
    }
    
    return skill_variations.get(skill, skill)
