import os
import re
from bs4 import BeautifulSoup

SRC_DIR = "/Users/amishchawla/Desktop/Projects/hiregen/hiregen_flask/academy"
DEST_DIR = "/Users/amishchawla/Desktop/Projects/hiregen/hiregen_flask/templates/academy"

def transform_url(url, current_rel_dir):
    """
    Transforms relative links into clean /academy/ clean URLs
    """
    if not url:
        return url
    if url.startswith("http://") or url.startswith("https://") or url.startswith("mailto:") or url.startswith("#"):
        return url

    # Remove query/hash temporarily
    hash_part = ""
    if "#" in url:
        url, hash_part = url.split("#", 1)
        hash_part = "#" + hash_part

    # Handle assets & datasets & resources files
    if "assets/" in url:
        clean_path = url[url.find("assets/"):]
        return f"/academy/{clean_path}{hash_part}"
    
    if "dataset/" in url:
        clean_path = url[url.find("dataset/"):]
        return f"/academy/{clean_path}{hash_part}"
        
    if "resources/" in url and (url.endswith(".md") or url.endswith(".csv") or url.endswith(".xlsx") or url.endswith(".zip")):
        clean_path = url[url.find("resources/"):]
        return f"/academy/{clean_path}{hash_part}"

    # Normalize relative paths to academy root
    if current_rel_dir:
        if url.startswith("../"):
            norm_url = url[3:]
        elif url.startswith("./"):
            norm_url = f"{current_rel_dir}/{url[2:]}"
        else:
            norm_url = f"{current_rel_dir}/{url}"
    else:
        if url.startswith("./"):
            norm_url = url[2:]
        else:
            norm_url = url

    # Remove .html extension
    if norm_url.endswith(".html"):
        norm_url = norm_url[:-5]

    # Handle index
    if norm_url == "index" or norm_url == "":
        return f"/academy/{hash_part}"
    
    return f"/academy/{norm_url}{hash_part}"

def process_file(src_path, dest_path, rel_dir):
    with open(src_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')

    # 1. Extract Title
    title_text = "AI Recruitment Masterclass | HireGen Academy"
    if soup.title and soup.title.string:
        title_text = soup.title.string.strip()

    # 2. Extract Meta tags & Scripts from Head (like schema.org json-ld)
    meta_tags = []
    if soup.head:
        for meta in soup.head.find_all(['meta', 'script', 'style']):
            if meta.name == 'meta':
                if meta.get('charset') or meta.get('name') == 'viewport':
                    continue
                meta_tags.append(str(meta))
            elif meta.name == 'script' and meta.get('type') == 'application/ld+json':
                meta_tags.append(str(meta))
            elif meta.name == 'style':
                meta_tags.append(str(meta))

    meta_block_str = "\n".join(meta_tags)

    # 3. Extract Shell or Main Content
    shell = soup.find('div', class_='shell')
    if not shell:
        shell = soup.find('body')
        if not shell:
            shell = soup

    # Transform all <a> links
    for a in shell.find_all('a'):
        href = a.get('href')
        if href:
            a['href'] = transform_url(href, rel_dir)

    # Transform all <img> src
    for img in shell.find_all('img'):
        src = img.get('src')
        if src:
            img['src'] = transform_url(src, rel_dir)

    # Remove inline body scripts since course.js handles it globally
    for s in shell.find_all('script'):
        s.decompose()

    # Inner shell HTML
    content_html = str(shell)

    # Template output
    jinja_template = """{% extends "academy_base.html" %}

{% block academy_title %}""" + title_text + """{% endblock %}

{% block academy_meta %}
""" + meta_block_str + """
{% endblock %}

{% block academy_content %}
""" + content_html + """
{% endblock %}
"""

    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    with open(dest_path, 'w', encoding='utf-8') as f:
        f.write(jinja_template)

def main():
    os.makedirs(DEST_DIR, exist_ok=True)
    count = 0
    for root, dirs, files in os.walk(SRC_DIR):
        if "_deploy" in root:
            continue
        for file in files:
            if file.endswith(".html"):
                src_path = os.path.join(root, file)
                rel_path = os.path.relpath(src_path, SRC_DIR)
                dest_path = os.path.join(DEST_DIR, rel_path)
                
                rel_dir = os.path.dirname(rel_path)
                process_file(src_path, dest_path, rel_dir)
                count += 1

    print(f"Successfully converted {count} files to Jinja templates in {DEST_DIR}")

if __name__ == '__main__':
    main()
