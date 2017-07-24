import argparse
import datetime
import logging

import assets
import conf
import markup
import pages
import s3
from miscutils import empty_dir


def configure_logging(level):
    """ Set up the logger with level from command line arg """

    logger = logging.getLogger("logger")
    if level == 0:
        logger.setLevel(logging.WARNING)
    elif level == 1:
        logger.setLevel(logging.INFO)
    elif level == 2:
        logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())


def get_args():
    """ Get publish True/False and verbosity from command line args """

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--verbosity",
        type=int,
        choices=[0, 1, 2],
        default=0,
        help="choose verbosity; 0 = None, 1 = Some, 2 = All",
    )
    subparsers = parser.add_subparsers(help='sub-command help')

    # make the output sub-command parser
    parser_output = subparsers.add_parser(
        'output',
        help="output either publish posts or draft posts",
    )
    parser_output.add_argument(
        'output',
        choices=['publish', 'draft', 'upload'],
        default='publish',
        help="choose 'publish' or 'draft' posts to output locally "
             "or upload to upload to live web site",
    )

    # make the test post sub-command parser
    parser_test = subparsers.add_parser(
        'test',
        help='tranform test input as raw body to html',
    )
    parser_test.add_argument(
        'input',
        help="input test input",
    )

    return vars(parser.parse_args())


def raw_body_to_html(raw_body):
    """ just for testing but need proper abstraction """

    raw_body, tags = markup.inline_tag_thing(raw_body)
    typed_chunks = markup.post_to_typed_chunks(raw_body)
    body_html = markup.typed_chunks_to_html_page(typed_chunks)
    return body_html


def get_options():
    args = get_args()
    # configure_logging(args['verbosity'])

    if args.get('test'):
        print(raw_body_to_html(args['test']))
        return

    publish = args['output'] in ['publish', 'upload']  # otherwise is draft
    out_dir = conf.PUBLISH_OUTPUT_DIR if publish else conf.DRAFT_OUTPUT_DIR
    post_source_dir = conf.POST_INPUT_DIR if publish else conf.DRAFT_INPUT_DIR
    options = {
        'publish': publish,
        'css_source_dir': conf.CSS_INPUT_DIR,
        'css_out': conf.CSS_INPUT_DIR,
        'js_source_dir': conf.JS_INPUT_DIR,
        'post_source_dir': post_source_dir,
        'out_dir': out_dir,
        'upload': args['output'] == 'upload',
    }
    return options


def main():
    """ Use command line args and config to do the business """

    # prepare
    options = get_options()
    output_dir = options['out_dir']
    empty_dir(output_dir)

    # create various files in output directory
    static_filenames = assets.make_static_assets(options)
    pages.make_404(output_dir, static_filenames)
    post_datas = pages.make_posts(
        options['publish'],
        options['post_source_dir'],
        output_dir,
        static_filenames,
    )
    pages.make_homepage(output_dir, static_filenames, post_datas)
    print('output done ' + datetime.datetime.now().strftime('%H:%M:%S'))

    # upload
    if options['upload']:
        s3.upload(options['out_dir'])
        print('upload done')


if __name__ == "__main__":
    main()
