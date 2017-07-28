""" Read and manipulate CSS files """

import os
from functools import partial

import funcutils as fu
from miscutils import logger, num_to_base36

log = logger()


def get_path_files_with_ext(extension, directory):
    """ Get full file directory of all extension files in supplied dir """

    return [
        directory + file_name for file_name in os.listdir(directory)
        if file_name.endswith(extension)
    ]


def combine_css(directory):
    """ Combine & minify all .css files in supplied dir """

    composed = fu.lcompose([
        partial(get_path_files_with_ext, '.css'),
        fu.fmap(fu.file_to_str),
        '\n'.join,
    ])
    return composed(directory)


def get_js(directory):
    """ Combine all .js files in supplied dir """

    composed = fu.lcompose([
        partial(get_path_files_with_ext, '.js'),
        fu.fmap(fu.file_to_str),
        '\n'.join,
    ])
    return composed(directory)


def remove_extention(extension, directory):
    """ Delete all files with given extension from directory """

    map(os.remove, get_path_files_with_ext(extension, directory))


def get_cachebusting_name(file_str):
    """ Make nice short readable str (mostly) uniquely representing a str """

    return fu.lcompose([hash, abs, num_to_base36])(file_str)


def make_static_assets(opts):
    """ Make cachebusted css & js files, return dict of filenames """

    css_filename = do_css(opts['css_source_dir'], opts['out_dir'])
    js_filename = do_js(opts['js_source_dir'], opts['out_dir'])
    return {
        'primary_css': css_filename,
        'js': js_filename
    }


def do_css(css_input_dir, css_output_dir):
    """ Take input css, combine, cachebust, replace """

    # primary css
    css_str = combine_css(css_input_dir)
    css_name = get_cachebusting_name(css_str) + '.css'

    # remove and write
    remove_extention('.css', css_output_dir)
    fu.str_to_file(css_output_dir + css_name, css_str)

    return css_name


def do_js(js_input_dir, js_output_dir):
    """ Take input js, combine, cachebust, replace existing output """

    remove_extention('.js', js_output_dir)
    js_str = get_js(js_input_dir)
    js_name = get_cachebusting_name(js_str) + '.js'
    fu.str_to_file(js_output_dir + js_name, js_str)
    return js_name
