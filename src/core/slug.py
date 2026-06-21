"""Shared slug generation with Cyrillic transliteration."""

import re

_TRANSLIT = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd',
    'е': 'e', 'ё': 'yo', 'ж': 'zh', 'з': 'z', 'и': 'i',
    'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n',
    'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't',
    'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch',
    'ш': 'sh', 'щ': 'shch', 'ъ': '', 'ы': 'y', 'ь': '',
    'э': 'e', 'ю': 'yu', 'я': 'ya',
}


def generate_slug(name: str) -> str:
    """Generate a URL-friendly slug from a name.

    Supports both Latin and Cyrillic input.
    Example: 'Нефтяная Вышка' -> 'neftyanaya-vyshka'
    """
    slug = name.lower()
    # Transliterate Cyrillic
    slug = ''.join(_TRANSLIT.get(ch, ch) for ch in slug)
    # Keep only latin letters, digits, spaces and hyphens
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    # Collapse whitespace to hyphens
    slug = re.sub(r'[\s]+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    slug = slug.strip('-')
    return slug or 'item'
