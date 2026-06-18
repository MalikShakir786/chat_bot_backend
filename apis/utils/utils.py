def format_file_size(size_bytes: int) -> str:
    size_kb = size_bytes / 1024
    size_mb = size_kb / 1024

    if size_mb >= 1:
        return f"{size_mb:.1f} MB"
    else:
        return f"{size_kb:.1f} KB"