# todo: rename?
import os

import assets, html, markup

from miscutils import get_cachebusting_name
from funcutils import file_to_str, str_to_file, lcompose, ffilter, atr


PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
HOME = os.path.expanduser("~")
POST_INPUT_DIR = HOME + '/posts/publish/'
OUTPUT_DIR = HOME + '/posts/output/'
CSS_INPUT_DIR = PROJECT_ROOT + '/css/'
JS_INPUT_DIR = PROJECT_ROOT + '/js/'


""" Get filename of posts for conversion """
post_filenames = lcompose([
    os.listdir,
    ffilter(atr('endswith', '.txt')),
    ])


def main():
    """ Build the site """

    css_filename, dark_css_filename = do_css(CSS_INPUT_DIR, OUTPUT_DIR)
    js_filename = do_js(JS_INPUT_DIR, OUTPUT_DIR)
    static_filenames = {
        'primary_css': css_filename,
        'dark_css': dark_css_filename,
        'js': js_filename
    }


    files_with_titles = []
    for filename in post_filenames(POST_INPUT_DIR):
        html_file_name, post_html, title = html.postfile_to_html(POST_INPUT_DIR + filename, static_filenames)
        files_with_titles.append((html_file_name, title))
        str_to_file(OUTPUT_DIR + html_file_name, post_html)

    # make homepage
    # need to order by date and refactor
    homepage_post_str = '\n'.join('<a href="{0}">{1}</a>'.format(*file_title)
                                  for file_title in files_with_titles)
    body_html = markup.to_html(homepage_post_str)
    template = '/projects/site/templates/base.html'
    post_html = html.make_html_page(template, body_html, "", static_filenames, 'Home')
    str_to_file(OUTPUT_DIR + 'home', post_html)


def do_css(css_input_dir, css_output_dir):
    """ Take input css & dark css, combine, cachebust, replace """

    # primary css
    css_str = assets.combine_css(css_input_dir)
    css_name = get_cachebusting_name(css_str) + '.css'

    # dark css
    dark_css_str = file_to_str(CSS_INPUT_DIR + 'dark.css')
    dark_css_name = get_cachebusting_name(dark_css_str) + '.css'

    # remove and write
    assets.remove_extention('.css', css_output_dir)
    str_to_file(css_output_dir + css_name, css_str)
    str_to_file(css_output_dir + dark_css_name, dark_css_str)

    return css_name, dark_css_name


def do_js(js_input_dir, js_output_dir):
    """ Take input js, combine, cachebust, replace existing output """

    js_str = assets.get_js(js_input_dir)
    js_name = get_cachebusting_name(js_str) + '.js'
    assets.remove_extention('.js', js_output_dir)
    str_to_file(js_output_dir + js_name, js_str)
    return js_name


if __name__ == "__main__":
    main()
