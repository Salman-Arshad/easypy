import os
from django.conf import settings


def get_tree():
    dir_tree = os.path.join(os.path.expanduser('~'), 'app_home') if settings.DEPLOYED else os.getcwd()

    tree = {'name': '.', 'abs_path': '.', 'is_dir': True, 'children': []}

    def get_path(path):
        path_to_search = []
        try:
            path_tree = tree
            path_to_search = path.split('/')
            for path_name in path_to_search:
                if path_tree['name'] == path_name:
                    path_tree = path_tree
                else:
                    for path in path_tree['children']:
                        # noinspection PyTypeChecker
                        if path['name'] == path_name:
                            path_tree = path
                            break
            return path_tree
        except KeyError as e:
            e.args = (f"configuration does not exists {'/'.join(path_to_search)}",)
            raise

    cwd = os.getcwd()
    try:
        os.chdir(dir_tree)
        for root, dirs, files in os.walk("."):
            for name in files:
                get_path(root)['children'].append(
                    {'name': name, 'abs_path': os.path.join(root, name), 'is_dir': False, 'children': []}
                )
            for name in dirs:
                get_path(root)['children'].append(
                    {'name': name, 'abs_path': os.path.join(root, name), 'is_dir': True, 'children': []}
                )
        return tree
    finally:
        os.chdir(cwd)

import os
from django.conf import settings


def get_csv():
    dir_tree = os.path.join(os.path.expanduser('~'), 'app_home') if settings.DEPLOYED else os.getcwd()

    # tree = {'name': '.', 'abs_path': '.', 'is_dir': True, 'children': []}

    # def get_path(path):
    #     path_to_search = []
    #     try:
    #         path_tree = tree
    #         path_to_search = path.split('/')
    #         for path_name in path_to_search:
    #             if path_tree['name'] == path_name:
    #                 path_tree = path_tree
    #             else:
    #                 for path in path_tree['children']:
    #                     # noinspection PyTypeChecker
    #                     if path['name'] == path_name:
    #                         path_tree = path
    #                         break
    #         return path_tree
    #     except KeyError as e:
    #         e.args = (f"configuration does not exists {'/'.join(path_to_search)}",)
    #         raise

    csvs = []
    cwd = os.getcwd()
    try:
        os.chdir(dir_tree)
        for root, dirs, files in os.walk("."):
            for name in files:
                if 'csv' in name:
                    csvs.append(name)

                # get_path(root)['children'].append(
                #     {'name': name, 'abs_path': os.path.join(root, name), 'is_dir': False, 'children': []}
                # )
        return csvs
    finally:
        os.chdir(cwd)
