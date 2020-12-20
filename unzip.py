import argparse
import os
import zipfile


def init_argparse():
    parser = argparse.ArgumentParser(description='question_b')
    parser.add_argument('--filename', metavar='filename', type=str, nargs='?',
                        help='unzip url')
    parser.add_argument('--dir', metavar='dir', type=str, nargs='?',
                        help='unzip dir')
    return parser.parse_args()


if __name__ == '__main__':
    args = init_argparse()
    arg_filename = args.filename
    arg_dir = args.dir
    print("Unzipping %s to %s" % (arg_filename, arg_dir))
    with zipfile.ZipFile(os.path.join(arg_dir, arg_filename), 'r') as zip_ref:
        zip_ref.extractall(arg_dir)
