from .registry import EntityRegistry
from .synonyms import SynonymManager
from .canonicalizer import Canonicalizer
from .resolver import EntityResolver

__all__ = [
    "EntityRegistry",
    "SynonymManager",
    "Canonicalizer",
    "EntityResolver"
]
