import css
import html
from miscutils import get_cachebusting_name
from funcutils import str_to_file


def main():
    css_input_dir = '/projects/stat/input/css/'
    css_output_dir = '/projects/stat/output/'
    css_filename = do_css(css_input_dir, css_output_dir)

    html_input_dir = '/projects/stat/input/posts/'
    html_output_dir = '/projects/stat/output/'
    html.do_html(html_input_dir, html_output_dir, css_filename)


def do_css(css_input_dir, css_output_dir):
    css_str = css.combine_minify(css_input_dir)
    css_name = get_cachebusting_name(css_str) + '.css'
    css.remove_css(css_output_dir)
    str_to_file(css_output_dir + css_name, css_str)
    return css_name


if __name__ == "__main__":
    main()
