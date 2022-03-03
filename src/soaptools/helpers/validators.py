from urllib.parse import urlparse


def is_url(path: str) -> bool:
    try:
        result = urlparse(path)
        return all([result.scheme, result.netloc])
    except:
        return False


def is_directory_path(path: str) -> bool:
    return "." not in path
