"""CMBA Core: explicit bindings, optional applications, no inherited authority."""
from .errors import Refusal
from .codec import canonical, decode
from .bindings import dimension, bind, inspect, compare, reference, relation, profile_reference
__version__ = '0.1.0a1'
__all__ = ['Refusal','canonical','decode','dimension','bind','inspect','compare','reference','relation','profile_reference']
