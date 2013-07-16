""" Read and manipulate CSS files """

import os
from operator import add
from functools import partial

from funcutils import file_to_str, str_to_file, lcompose, fmap, ffilter, atr, pipe
from miscutils import logger, num_to_base36

log = logger()


def get_path_files_with_ext(extension, path):
    """ Get full file path of all extension files in supplied dir """
    return [path + file_name for file_name in os.listdir(path)
            if file_name.endswith(extension) and file_name != 'dark.css']


""" Combine CSS strings """
combine = '\n'.join


""" Combine & minify all .css files in supplied dir """
combine_css = lcompose([
    partial(get_path_files_with_ext, '.css'),
    fmap(file_to_str),
    combine,
    ])


""" Combine all .js files in supplied dir """
get_js = lcompose([
    partial(get_path_files_with_ext, '.js'),
    fmap(file_to_str),
    combine,
    ])


def remove_extention(extension, path):
    """ Delete all files with given extension """
    map(os.remove, get_path_files_with_ext(extension, path))


""" Make a nice short readable str (mostly) uniquely representing a str """
get_cachebusting_name = lcompose([hash, abs, num_to_base36])
