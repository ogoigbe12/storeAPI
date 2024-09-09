"""
blocklist.py

This file just contain the blocklist of the JWT tokens.
It will be imported by app and logout resource so that token
can be added to the blocklist when user logout. 
"""

BLOCKLIST = set()