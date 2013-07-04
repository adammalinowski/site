""" Read and manipulate CSS files """

import cssmin

import os
from operator import add
from functools import partial

from funcutils import file_to_str, str_to_file, lcompose, fmap, ffilter, atr
from miscutils import logger

log = logger(0)


@log
def get_path_files_with_ext(extension, path):
    """ Get full file path of all extension files in supplied dir """
    return [path + file_name for file_name in os.listdir(path)
            if file_name.endswith(extension) and file_name != 'dark.css']


""" Combine CSS strings """
combine = '\n'.join


""" Minify a css string """
minify_css = cssmin.cssmin


""" Combine & minify all .css files in supplied dir """
combine_minify_css = lcompose([
    partial(get_path_files_with_ext, '.css'),
    fmap(file_to_str),
    combine,
    minify_css,
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
