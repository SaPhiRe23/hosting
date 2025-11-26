# backend/utils.py
import re

def generate_subdomain(project, user):
    def clean(s):
        s2 = re.sub(r'[^A-Za-z0-9_-]', '-', s)
        return s2.strip('-').lower()
    return f"{clean(project)}.{clean(user)}"

def container_name_from_subdomain(subdomain):
    return subdomain.replace(".", "-")
