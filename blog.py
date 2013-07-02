# todo: rename?
import os
import css
import html
from miscutils import get_cachebusting_name
from funcutils import str_to_file


ROOT = os.path.dirname(os.path.realpath(__file__))
CSS_INPUT_DIR = ROOT + 'css/'
OUTPUT_DIR = '~/posts/output/'
POST_INPUT_DIR = '~/posts/'


def main():
    """ Build the site """

    css_filename = do_css(CSS_INPUT_DIR, OUTPUT_DIR)
    html.do_html(POST_INPUT_DIR, OUTPUT_DIR, css_filename)


def do_css(css_input_dir, css_output_dir):
    """ Take input css, combine, minify, cachebust, replace existing output """

    css_str = css.combine_minify(css_input_dir)
    css_name = get_cachebusting_name(css_str) + '.css'
    css.remove_css(css_output_dir)
    str_to_file(css_output_dir + css_name, css_str)
    return css_name


if __name__ == "__main__":
    main()
