import os
import datetime

# helper to get file stats
def get_file_stats(full_path, project_root, relative_path_prefix="output"):
    stats = os.stat(full_path)
    size_bytes = stats.st_size
    created_ts = datetime.datetime.fromtimestamp(stats.st_ctime)

    def human_readable_size(size):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} PB"

    return {
        "path": os.path.abspath(full_path),
        "relative_path": os.path.relpath(full_path, project_root),
        "size_bytes": size_bytes,
        "size_human": human_readable_size(size_bytes),
        "created": created_ts.strftime("%Y-%m-%d %H:%M:%S"),
    }