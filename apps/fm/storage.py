import os
from django.conf import settings
# noinspection PyProtectedMember
from django.utils._os import safe_join
from django.core.files import locks
# noinspection PyUnresolvedReferences
from django.core.files.base import File, ContentFile
from django.core.files.move import file_move_safe
from django.core.files.storage import Storage


class CustomStorage(Storage):
    def __init__(self, location=None, file_permissions_mode=None, directory_permissions_mode=None):
        self.location = location
        self.file_permissions_mode = file_permissions_mode
        self.directory_permissions_mode = directory_permissions_mode

    def path(self, name):
        return safe_join(self.location, name)

    def exists(self, name):
        return os.path.exists(self.path(name))

    def _open(self, name, mode='rb'):
        return File(open(self.path(name), mode))

    def delete(self, name):
        assert name, "The name argument is not allowed to be empty."
        name = self.path(name)
        # If the file or directory exists, delete it from the filesystem.
        try:
            if os.path.isdir(name):
                os.rmdir(name)
            else:
                os.remove(name)
        except FileNotFoundError:
            # FileNotFoundError is raised if the file or directory was removed
            # concurrently.
            pass

    # noinspection SpellCheckingInspection
    def _save(self, name, content):
        full_path = self.path(name)

        # Create any intermediate directories that do not exist.
        directory = os.path.dirname(full_path)
        if not os.path.exists(directory):
            try:
                if self.directory_permissions_mode is not None:
                    # os.makedirs applies the global umask, so we reset it,
                    # for consistency with file_permissions_mode behavior.
                    old_umask = os.umask(0)
                    try:
                        os.makedirs(directory, self.directory_permissions_mode)
                    finally:
                        os.umask(old_umask)
                else:
                    os.makedirs(directory)
            except FileExistsError:
                # There's a race between os.path.exists() and os.makedirs().
                # If os.makedirs() fails with FileExistsError, the directory
                # was created concurrently.
                pass
        if not os.path.isdir(directory):
            raise IOError("%s exists and is not a directory." % directory)

        # There's a potential race condition between get_available_name and
        # saving the file; it's possible that two threads might return the
        # same name, at which point all sorts of fun happens. So we need to
        # try to create the file, but if it already exists we have to go back
        # to get_available_name() and try again.

        while True:
            try:
                # This file has a file path that we can move.
                if hasattr(content, 'temporary_file_path'):
                    file_move_safe(content.temporary_file_path(), full_path)

                # This is a normal uploadedfile that we can stream.
                else:
                    # This fun binary flag incantation makes os.open throw an
                    # OSError if the file already exists before we open it.
                    flags = (os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                             getattr(os, 'O_BINARY', 0))
                    # The current umask value is masked out by os.open!
                    fd = os.open(full_path, flags, 0o666)
                    _file = None
                    try:
                        locks.lock(fd, locks.LOCK_EX)
                        for chunk in content.chunks():
                            if _file is None:
                                mode = 'wb' if isinstance(chunk, bytes) else 'wt'
                                _file = os.fdopen(fd, mode)
                            _file.write(chunk)
                    finally:
                        locks.unlock(fd)
                        if _file is not None:
                            _file.close()
                        else:
                            os.close(fd)
            except FileExistsError:
                # A new name is needed if the file exists.
                name = self.get_available_name(name)
                full_path = self.path(name)
            else:
                # OK, the file save worked. Break out of the loop.
                break

        if self.file_permissions_mode is not None:
            os.chmod(full_path, self.file_permissions_mode)

        # Store filenames with forward slashes, even on Windows.
        return name.replace('\\', '/')


tmp_storage = CustomStorage(location='/tmp')

# this will prevent for APP scan all files of user home while developing
root_location = os.path.join(os.path.expanduser('~'), 'app_home') if settings.DEPLOYED else os.getcwd()
this_storage = CustomStorage(location=root_location)
