import re

def normalizeName(name):
    name = name.lower()
    name = name.replace("–", "-")
    name = re.sub(r"[^a-z0-9\s-]", "", name)
    return name.strip()
