""" Read and manipulate CSS files """

import os
from functools import partial

import funcutils as fu
from miscutils import logger, num_to_base36

log = logger()


def get_path_files_with_ext(extension, path):
    """ Get full file path of all extension files in supplied dir """
    return [path + file_name for file_name in os.listdir(path)
            if file_name.endswith(extension) and file_name != 'dark.css']


""" Combine CSS strings """
combine = '\n'.join


""" Combine & minify all .css files in supplied dir """
combine_css = fu.lcompose([
    partial(get_path_files_with_ext, '.css'),
    fu.fmap(fu.file_to_str),
    combine,
])


""" Combine all .js files in supplied dir """
get_js = fu.lcompose([
    partial(get_path_files_with_ext, '.js'),
    fu.fmap(fu.file_to_str),
    combine,
])


def remove_extention(extension, path):
    """ Delete all files with given extension """
    map(os.remove, get_path_files_with_ext(extension, path))


""" Make a nice short readable str (mostly) uniquely representing a str """
get_cachebusting_name = fu.lcompose([hash, abs, num_to_base36])
