""" Read and manipulate CSS files """

import cssmin

import os
from operator import add
from functools import partial

from funcutils import file_to_str, str_to_file, lcompose, fmap, ffilter, atr
from miscutils import logger

log = logger(0)


@log
def get_css_file_paths(css_path):
    """ Get full file path of all .css files in supplied dir """
    return [css_path + file_name
            for file_name in os.listdir(css_path)
            if file_name.endswith(".css")]


""" Combine CSS strings """
combine_css = '\n'.join


""" Minify a css string """
minify_css = cssmin.cssmin


""" Combine & minify CSS all .css files in supplied dir """
combine_minify = lcompose([
    get_css_file_paths,
    fmap(file_to_str),
    combine_css,
    minify_css,
    ])


""" Delete all CSS files """
remove_css = lcompose([
    get_css_file_paths,
    fmap(os.remove)
    ])
