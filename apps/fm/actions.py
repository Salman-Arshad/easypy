import os
import sys
import subprocess
from django.http import JsonResponse


# noinspection PyBroadException,PyUnboundLocalVariable,PyUnusedLocal,SpellCheckingInspection
def run_code(file_name):
    fstdout = ''
    fstderr = ''
    ret_code = 0
    try:
        p = subprocess.Popen(
            [sys.executable, os.path.join('/tmp', file_name)], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, stderr = p.communicate()

        fstdout = stdout.decode('utf-8')
        fstderr = stderr.decode('utf-8')
        ret_code = p.returncode
    except Exception as e:
        fstderr = stderr.decode('utf-8')
    finally:
        return '%s\n%s\nExit Code: %s' % (fstdout, fstderr, ret_code)


def read_plain_file(storage, file):
    response = {'description': 'ok', 'content': ''}
    status = 200
    try:
        response['content'] = storage.open(file, 'r').read()
    except TypeError:
        status = 400
        response['description'] = 'file %s is not plain text readable' % file
    except IsADirectoryError:
        status = 400
        response['description'] = 'file %s is a directory' % file
    except FileNotFoundError:
        status = 404
        response['description'] = 'file %s not found' % file
    except Exception as e:
        print(f'{e.__class__.__name__} Exception when trying to read content of file {file}  \n{e}')
        status = 500
        response['description'] = 'can not read this file'
    finally:
        return JsonResponse(response, status=status)


def write_plain_file(storage, file, content):
    response = {'description': 'ok', 'content': ''}
    status = 200
    try:
        if os.path.isdir(os.path.join(storage.location, file)):
            raise IsADirectoryError
        if not os.path.isfile(os.path.join(storage.location, file)):
            raise FileNotFoundError
        storage.delete(file)
        storage.save(file, content)
    except IsADirectoryError:
        status = 400
        response['description'] = 'file %s is a directory' % file
    except FileNotFoundError:
        status = 404
        response['description'] = 'file %s not found' % file
    except Exception as e:
        print(f'{e.__class__.__name__} Exception when trying to write file {file}  \n{e}')
        status = 500
        response['description'] = 'can not write this file'
    finally:
        return JsonResponse(response, status=status)
