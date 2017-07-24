import os

from boto import s3


def get_s3_bucket():
    conn = s3.connect_to_region(
        'eu-west-2',
        aws_access_key_id=os.environ['S3_ACCESS_KEY_ID'],
        aws_secret_access_key=os.environ['S3_SECRET_ACCESS_KEY'],
        is_secure=True,
    )
    return conn.get_bucket('adammalinowski')


def get_extension(filename):
    """ return the extension of the file """

    splitfilename = filename.split('.')
    return splitfilename[-1] if len(splitfilename) > 1 else 'html'


def extension_to_mimetype(extension):
    extension_to_mimetype = {
        'txt': 'text/plain',
        'html': 'text/html',
        'css': 'text/css',
        'js': 'text/javascript',
    }
    return extension_to_mimetype[extension]


def extension_to_headers(extension):
    no_cache = {'Cache-Control': 'private, max-age=0'}
    long_cache = {'Cache-Control': 'public, max-age=31449600'}
    extension_to_headers = {
        'txt': no_cache,
        'html': no_cache,
        'css': long_cache,
        'js': long_cache,
    }
    return extension_to_headers[extension]


def upload(out_dir):
    print('uploading...')
    bucket = get_s3_bucket()
    for file_name in os.listdir(out_dir):
        file_path = out_dir + file_name
        extension = get_extension(file_name)
        key = s3.key.Key(bucket)
        key.key = file_name
        key.content_type = extension_to_mimetype(extension)
        headers = extension_to_headers(extension)
        key.set_contents_from_filename(
            file_path,
            headers=headers,
        )
        key.make_public()
