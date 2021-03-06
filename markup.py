import re
import cgi
from functools import partial
from itertools import takewhile

from html import urlize
import funcutils as fu
from miscutils import logger

log = logger()


def xotd(xotd_post):
    """ Takes a thing-of-the-day

    Takes thing-of-the-day file and converts it to html files

    Format is:

        [Title]

        ---

        [Entry]

        [Date]

        ---

    """


def inline_tag_thing(raw_body):
    """ find inline tags, replace with internal links, return tags """

    tags = []

    def replace(matched):
        """ Take matched, mutate closed-over tag list, return link markup """

        matched_str = matched.groups()[0]
        tags.append(matched_str)
        return '"{0}"->{1}'.format(matched_str, urlize(matched_str))

    raw_body = wrap_match('\|').sub(replace, raw_body)
    return raw_body, tags


def post_to_chunks(post):
    """ Split a post into lists of lines, broken by empty lines

    e.g. "1\n2\n\n3\n4\n\n\n5" -> [[1, 2], [3, 4], [5]]

    """
    chunks = []
    buff = []
    for line in re.split('\n', post):
        if not line:
            if buff:
                chunks.append(buff)
            buff = []
        else:
            buff.append(line)
    if buff:
        chunks.append(buff)
    return chunks


def chunk_to_typed_chunk(chunk):
    """ Take chunk, return tuple of (elem type, chunk with chunk markup removed)

    examples:
    - ["Hi.", "What is up?"] -> ('p', ["Hi.", "What is up?"])
    - ["---"] -> ('hr', [])
    - ["`10 PRINT 'bumface'", "20 GOTO 10`"]
      -> ('pre', ["10 PRINT 'bumface'", "20 GOTO 10"])

    """
    schunk = list(map(fu.atr('strip'), chunk))
    if len(chunk) == 1:
        if schunk[0].startswith('---'):  # todo also check no non-dash chars?
            return ('hr', [])

    if schunk[-1].startswith('-----'):
        if schunk[-2].startswith('-----'):
            return ('h2', chunk[:-2])
        else:
            return ('h3', chunk[:-1])

    if schunk[0].startswith('`') and schunk[-1].endswith('`'):
        chunk[0] = chunk[0][2:]  # remove markup
        chunk[-1] = chunk[-1][:-2]  # remove markup
        return ('pre', chunk)

    if schunk[0].startswith('- ') or schunk[0].startswith('1. '):
        return ('l', chunk)

    return ('p', chunk)  # everything else is a paragraph


def parse_list_chunk(chunk):
    """ Convert a chunk into a list of (list_type, indent, line) tuples """

    indent_amount = 4  # number of spaces to indicate a level of indentation
    outlines = []
    last_indent = 0
    for line in chunk:
        sline = line.strip()
        if sline.startswith('- '):
            list_type = 'ul'
        elif re.match(r'^[\d]\. ', sline):  # match digit, dot, space
            list_type = 'ol'
        else:
            list_type = None
        if list_type:
            indent_spaces = len(line) - len(line.lstrip())
            indent = indent_spaces / indent_amount
            assert not indent_spaces % indent_amount, "Bad indent amount"
            assert indent <= last_indent + 1, "Indented by more than one level"
            last_indent = indent
            if list_type == 'ul':
                line_without_markup = sline[2:]
            else:
                line_without_markup = sline[3:]
            outlines.append((list_type, indent, line_without_markup))
        else:
            # if not an li, is just part of existing li on new line
            last_tuple = outlines[-1]
            outlines[-1] = (last_tuple[0], last_tuple[1], last_tuple[2] + line)
    return outlines


def parsed_list_to_html(parsed_list, last_indent=0):
    """ Recursively convert a list to HTML """

    if parsed_list[0][0] == 'ul':
        open_elem, close_elem = '<ul>', '</ul>'
    else:
        open_elem, close_elem = '<ol>', '</ol>'
    html_lines = [open_elem]
    i = 0
    while i < len(parsed_list):
        list_type, indent, line = parsed_list[i]
        if indent > last_indent:
            # get the sublist
            sublist = list(takewhile(lambda li: li[1] > last_indent,
                                     parsed_list[i:]))
            result = parsed_list_to_html(sublist, last_indent=indent)
            html_lines.extend(result)
            i += len(sublist)
        else:
            html_lines.append('<li>' + inline_markup_to_html(line))
            i += 1
    html_lines.append(close_elem)
    return html_lines


def convert_markup_links(astr):
    """ Convert markup links of form "link text"->linkurl to html links

    Note, link url must have space after, no commas or nuthin.

    """
    return re.sub(
        r"""
            "([^"]*)"     # match link text
            ->([^| ]*)    # match link url, any chars other than  space or |
            \|?           # optional | at the end ignored
        """,
        r'<a href="\2">\1</a>',
        astr,
        flags=re.VERBOSE,
    )


def convert_raw_links(astr):
    """ Convert raw urls to html links """
    return re.sub(
        r"""
            (?=(?<![^ ])http)  # starting http, not preceeded by non-space
            ([^| ]*)           # match all non-space chars other than |
            \|?                # optional | at the end ignored
        """,
        r'<a href="\1">\1</a>',
        astr,
        flags=re.VERBOSE,
    )


def wrap_match(match):
    """ Return re matching something surrounding text e.g. *some bold text*

    But not 1 * 2 * 3

    """
    return re.compile(
        r"""
            (?<![^\ ])%s(?!\ )  # char not preceeded by non-space,
                                # not followed by space
            (.+?)               # the surrounded text as a group
            (?<!\ )%s           # the match char not preceeded by space,
            (?![\w])            # not followed by alphanumeric
        """ % (match, match),
        flags=re.VERBOSE,
    )


def inline_markup_to_html(astr):
    """ Convert inline markup to html e.g. *bold text* -> <b>bold text</b> """

    markup_to_elem = [(r'\*', '<b>', '</b>'),
                      (r'\/', '<i>', '</i>'),
                      (r'`', '<code>', '</code>')]

    def replace(matched):
        """ Take matched, add opening & closing tags, cgi escape if code """

        matched_str = matched.groups()[0]
        if match == '`':
            matched_str = cgi.escape(matched_str)
        return opener + matched_str + closer

    for match, opener, closer in markup_to_elem:
        astr = wrap_match(match).sub(replace, astr)

    return fu.pipe(astr, [convert_markup_links, convert_raw_links])


def chunk_type_wrap(chunk_type, chunk):
    """ Wrap a chunk in HTML tags of it's chunk type """
    return '<%s>%s</%s>' % (chunk_type, '<br>'.join(chunk), chunk_type)


def typed_chunk_to_html(typed_chunk):
    """ Convert a typed chunk to html """

    chunk_type, chunk = typed_chunk
    wrap = partial(chunk_type_wrap, chunk_type)  # little helper

    if chunk_type == 'hr':
        return '<hr>'

    if chunk_type == 'l':
        return fu.pipe(
            chunk,
            [parse_list_chunk, parsed_list_to_html, '\n'.join],
        )

    if chunk_type in ['h2', 'h3']:
        assert len(chunk) == 1, "Header has multiple lines"
        header = chunk[0]
        name = urlize(header)
        header_link = link('#' + name, header)
        return '<a name="{0}"></a>{1}'.format(name, wrap([header_link]))

    if chunk_type == 'pre':
        # no inline markup, but do html escape
        chunk = map(cgi.escape, chunk)

    if chunk_type == 'p':
        chunk = map(inline_markup_to_html, chunk)

    return wrap(chunk)


def typed_chunks_to_toc_list(typed_chunks):
    return [(t, c[0]) for t, c in typed_chunks if t in ['h2', 'h3']]


def tagify(tag, value, **kwargs):
    attrs = ''
    if kwargs:
        if 'clss' in kwargs:
            kwargs['class'] = kwargs.pop('clss')
        attr_kvs = ['{}="{}"'.format(k, v) for k, v in kwargs.items()]
        attrs = ' ' + ' '.join(attr_kvs)
    return '<{tag}{attrs}>{val}</{tag}>'.format(
        tag=tag,
        val=value,
        attrs=attrs,
    )


def link(href, text):
    return '<a href="{0}">{1}</a>'.format(href, text)


def anchor_link(chunk):
    return link('#' + urlize(chunk), chunk)


def list_to_ul(alist):
    if not alist:
        return ''
    return '<ul>{0}</ul>'.format('\n'.join('<li>{0}</li>'.format(li)
                                 for li in alist))


def toc_list_to_toc(toc_chunks):

    # find if is only h3's
    if all(t == 'h3' for t, c in toc_chunks):
        return list_to_ul(anchor_link(chunk) for t, chunk in toc_chunks)
    else:
        # first make list of h2 with optional child list
        # wait should html be nested list also?!
        nested_lis = []
        for chunk_type, chunk in toc_chunks:
            if chunk_type == 'h2':
                nested_lis.append((chunk, []))
            elif chunk_type == 'h3':
                nested_lis[-1][1].append(chunk)
        # then make html
        inner_lists = [(outer, list_to_ul(map(anchor_link, lis)))
                       for outer, lis in nested_lis]
        return list_to_ul([anchor_link(outer) + '\n' + html_inner
                           for outer, html_inner in inner_lists])


""" Convert post in custom markup to typed chunks """
post_to_typed_chunks = fu.lcompose([
    post_to_chunks,
    fu.fmap(chunk_to_typed_chunk)
])


""" Convert typed chunks to html page """
typed_chunks_to_html_page = fu.lcompose([
    fu.fmap(typed_chunk_to_html),
    partial('\n'.join),
])
