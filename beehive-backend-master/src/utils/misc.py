import os
import random
import re
import string


NEWLINE_RE = re.compile(r'\r\n|[\r\n]')


def generate_random_string(chars, length):
    random.seed()
    return ''.join(random.choice(chars) for i in range(length))


def splitlines_keep_final(s):
    """
    This logic is implemented since the builtin splitlines function ignores
    final newline symbols, so 'hello\n' will result in ['hello'] instead of
    ['hello', ''], and this is necessary for our code file handling. builtin
    implementation seeks only \n or \r or "\r\n" like we do and is defined here:
    https://github.com/python/cpython/blob/5368c2b6e23660cbce7e38dc68f859c66ac349ee/Objects/stringlib/split.h#L335
    """
    return NEWLINE_RE.split(s)


def camel_case_to_snake_case(text):
    text = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', text).lower()


def generate_random_tmp_dir_path():
    chars = string.ascii_lowercase + string.ascii_uppercase + string.digits
    return os.path.join('/', 'tmp', generate_random_string(chars, 32))


def unzip_tmp_random_dir(zip_file):
    # find a non-existing temp directory
    temp_path = generate_random_tmp_dir_path()
    while os.path.exists(temp_path):
        temp_path = generate_random_tmp_dir_path()

    # create the directory
    os.mkdir(temp_path)

    # extract zip file
    zip_file.extractall(path=temp_path)

    # return the extracted path
    return temp_path


# copied from https://www.oreilly.com/library/view/python-cookbook/0596001673/ch04s16.html
def path_split_all(path):
    all_parts = []

    while True:
        parts = os.path.split(path)
        if parts[0] == path:  # sentinel for absolute paths
            all_parts.insert(0, parts[0])
            break
        elif parts[1] == path:  # sentinel for relative paths
            all_parts.insert(0, parts[1])
            break
        else:
            path = parts[0]
            all_parts.insert(0, parts[1])

    return all_parts


def delete_files_by_pattern(root_path, re_pattern):
    for dir_name, _, dir_files in os.walk(root_path):
        for matching_file_name in filter(lambda f: re.match(re_pattern, f), dir_files):
            os.remove(os.path.join(dir_name, matching_file_name))


def read_file_content(file_path):
    content = None

    with open(file_path, 'r') as f:
        content = f.read()

    return content
