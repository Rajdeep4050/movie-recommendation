#!/usr/bin/env python3
"""
Debug script to check Codespaces environment and Django settings
"""
import os
import sys

print("=" * 60)
print("CODESPACES ENVIRONMENT CHECK")
print("=" * 60)

# Check Codespaces environment variables
codespace_name = os.environ.get('CODESPACE_NAME')
github_codespace = os.environ.get('GITHUB_CODESPACES')

print(f"\nCodespaces Environment:")
print(f"  CODESPACE_NAME: {codespace_name}")
print(f"  GITHUB_CODESPACES: {github_codespace}")

# Load Django settings
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'movie_recommendation.settings')

try:
    import django
    django.setup()
    from django.conf import settings

    print(f"\nDjango Settings:")
    print(f"  DEBUG: {settings.DEBUG}")
    print(f"  ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
    print(f"  CSRF_TRUSTED_ORIGINS: {getattr(settings, 'CSRF_TRUSTED_ORIGINS', [])}")

except Exception as e:
    print(f"\nError loading Django: {e}")

print("\n" + "=" * 60)
