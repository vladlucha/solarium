
def format_slug(slug):
    for char in slug:
        if char in "?.!/;:'":
            slug = slug.replace(char, '-')
        slug = slug.replace(' ', '').replace('"', '')
    return slug