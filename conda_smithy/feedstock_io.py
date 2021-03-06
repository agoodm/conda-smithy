from __future__ import unicode_literals

from contextlib import contextmanager
import io
import os
import shutil


def get_repo(path, search_parent_directories=True):
    repo = None
    try:
        import git
        repo = git.Repo(
            path,
            search_parent_directories=search_parent_directories
        )
    except ImportError:
        pass
    except git.InvalidGitRepositoryError:
        pass

    return repo


def get_file_blob(repo, filename):
    from git.index.typ import BlobFilter

    idx = repo.index

    repo_dir = os.path.abspath(repo.working_dir)

    filename = os.path.abspath(filename)
    filename = os.path.relpath(filename, repo_dir)
    filename = os.path.normpath(filename)

    blob = next(idx.iter_blobs(BlobFilter(filename)))[1]

    return blob


def get_mode_file(filename):
    repo = get_repo(filename)
    if repo:
        blob = get_file_blob(repo, filename)
        mode = blob.mode
    else:
        mode = os.stat(filename).st_mode

    return mode


def set_mode_file(filename, mode):
    repo = get_repo(filename)
    if repo:
        blob = get_file_blob(repo, filename)
        blob.mode |= mode
        repo.index.add([blob])

    os.chmod(filename, mode)


@contextmanager
def write_file(filename):
    dirname = os.path.dirname(filename)
    if dirname and not os.path.exists(dirname):
        os.makedirs(dirname)

    with io.open(filename, "w", encoding="utf-8") as fh:
        yield fh

    repo = get_repo(filename)
    if repo:
        repo.index.add([filename])


def touch_file(filename):
    with write_file(filename) as fh:
        fh.write("")


def remove_file(filename):
    touch_file(filename)

    repo = get_repo(filename)
    if repo:
        repo.index.remove([filename])

    os.remove(filename)

    dirname = os.path.dirname(filename)
    if dirname and not os.listdir(dirname):
        os.removedirs(dirname)


def copy_file(src, dst):
    shutil.copy2(src, dst)

    repo = get_repo(dst)
    if repo:
        repo.index.add([dst])
