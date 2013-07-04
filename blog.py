# todo: rename?
import os

import assets
import html

from miscutils import get_cachebusting_name
from funcutils import file_to_str, str_to_file


PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
HOME = os.path.expanduser("~")
POST_INPUT_DIR = HOME + '/posts/publish/'
OUTPUT_DIR = HOME + '/posts/output/'
CSS_INPUT_DIR = PROJECT_ROOT + '/css/'
JS_INPUT_DIR = PROJECT_ROOT + '/js/'


def main():
    """ Build the site """

    css_filename = do_css(CSS_INPUT_DIR, OUTPUT_DIR)
    js_filename = do_js(JS_INPUT_DIR, OUTPUT_DIR)
    html.do_html(POST_INPUT_DIR, OUTPUT_DIR, css_filename, js_filename)


def do_css(css_input_dir, css_output_dir):
    """ Take input css, combine, minify, cachebust, replace existing output """

    # first do primary css
    css_str = assets.combine_minify_css(css_input_dir)
    css_name = get_cachebusting_name(css_str) + '.css'
    assets.remove_extention('.css', css_output_dir)
    str_to_file(css_output_dir + css_name, css_str)

    # then do dark css
    dark_css = file_to_str(CSS_INPUT_DIR + 'dark.css')
    str_to_file(css_output_dir + 'dark.css', dark_css)

    return css_name


def do_js(js_input_dir, js_output_dir):
    """ Take input js, combine, cachebust, replace existing output """

    js_str = assets.get_js(js_input_dir)
    js_name = get_cachebusting_name(js_str) + '.js'
    assets.remove_extention('.js', js_output_dir)
    str_to_file(js_output_dir + js_name, js_str)
    return js_name


if __name__ == "__main__":
    main()
