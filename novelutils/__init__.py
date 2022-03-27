"""NOVELUTILS.

NOVELUTILS uses the Scrapy framework to download novel from a website
and convert all chapters to XHTML, TXT, or to make EPUB.
"""
import argparse
import sys

from novelutils.utils.crawler import NovelCrawler
from novelutils.utils.epub import EpubMaker
from novelutils.utils.file import FileConverter

if sys.version_info >= (3, 8):
    from importlib import metadata
else:
    import importlib_metadata as metadata
__version__ = metadata.version(__name__)


def main(argv) -> int:
    """Main program.

    Arguments:
        argv: command-line arguments, such as sys.argv (including the program name in argv[0])

    Returns:
        Zero on successful program termination, non-zero otherwise.
    """
    parser = _build_parser()
    if len(argv) == 1:
        parser.print_help()
        return 0
    args = parser.parse_args(argv[1:])
    if args.version is True:
        print(f"Novelutils {__version__}")
        return 0
    try:
        args.func(args)
    except AttributeError:
        if argv[1] == "epub":
            print("Missing sub command: from_url, from_raw")
            return 1
    return 0


def crawl_func(args):
    """Run crawling process."""
    p = NovelCrawler(url=args.url)
    p.crawl(
        rm_raw=not args.keep_raw,
        start_chap=args.start,
        stop_chap=args.stop,
        clean=args.clean,
        output=args.raw,
    )


def convert_func(args):
    """Convert process."""
    c = FileConverter(args.raw_dir, args.result_dir)
    c.convert_to_xhtml(
        lang_code=args.lang_code,
        duplicate_chapter=args.dup_chap,
        rm_result=not args.keep_result,
    )


def rm_dup_func(args):
    """Remove duplicates of chapters name.

    Examples:
     novelutils rm_dup .\raw
     novelutils rm_dup --result_dir=.\result .\raw

    """
    if args.result_dir is None:
        c = FileConverter(args.raw_dir, args.raw_dir)
    else:
        c = FileConverter(args.raw_dir, args.result_dir)
    c.clean(duplicate_chapter=True, rm_result=False)


def epub_from_url_func(args):
    """Make epub from url process."""
    e = EpubMaker()
    e.from_url(args.url, args.dup_chap, args.start, args.stop)


def epub_from_raw_func(args):
    """Make epub from raw process."""
    e = EpubMaker()
    e.from_raw(args.raw_dir, args.dup_chap, args.lang_code)


def _build_parser():
    """Constructs the parser for the command line arguments.

    Examples:
      $ novelutils crawl [start=1] [stop=-1] [rm_raw=True] [dup_chap=False] {url} [raw_dir=None]
      $ novelutils crawl https://bachngocsach.com/reader/livestream-sieu-kinh-di

      $ novelutils convert [lang_code=vi] [dup_chap=False] [rm_result=True] {raw_dir} [result_dir=None]
      $ novelutils convert /home/user/raw

      $ novelutils epub from_url [dup_chap=False] [start=1] [stop=-1] {url}
      $ novelutils epub from_url https://bachngocsach.com/reader/livestream-sieu-kinh-di

      $ novelutils epub from_raw [dup_chap=False] [lang_code=vi] {raw_dir}
      $ novelutils epub from_raw /home/user/raw
    Returns:
      An ArgumentParser instance for the CLI.
    """
    # parser
    parser = argparse.ArgumentParser(prog="novelutils", allow_abbrev=False)
    parser.add_argument(
        "-v", "--version", action="store_true", help="show version number and exit"
    )
    subparsers = parser.add_subparsers(title="modes", help="supported modes")
    # crawl parser
    crawl = subparsers.add_parser("crawl", help="get novel text")
    crawl.add_argument(
        "--start",
        type=int,
        default=1,
        help="start chapter index (default:  %(default)s)",
    )
    crawl.add_argument(
        "--stop",
        type=int,
        default=-1,
        help="stop chapter index, input -1 to get all chapters (default:  %(default)s)",
    )
    crawl.add_argument(
        "--keep_raw",
        action="store_true",
        help="if specified, keep all old files in raw directory (default:  %(default)s)",
    )
    crawl.add_argument(
        "--raw_dir",
        type=str,
        default=None,
        metavar="RAW_PATH",
        help="path to raw directory (default: working directory)",
    )
    crawl.add_argument(
        "--clean", action="store_false", help="clean all the text files after crawling."
    )
    crawl.add_argument("url", type=str, help="full web site to novel info page")
    crawl.set_defaults(func=crawl_func)
    # convert parser
    convert = subparsers.add_parser("convert", help="convert chapters to xhtml")
    convert.add_argument(
        "--lang_code",
        default="vi",
        help="language code of the novel (default: %(default)s)",
    )
    convert.add_argument(
        "--dup_chap",
        action="store_true",
        help="if specified, remove duplicate chapter title (default:  %(default)s)",
    )
    convert.add_argument(
        "--keep_result",
        action="store_true",
        help="if specified, keep all old files in result directory (default:  %(default)s)",
    )
    convert.add_argument(
        "--result_dir",
        type=str,
        default=None,
        metavar="RESULT_PATH",
        help="path to result directory (default: same parent as raw directory)",
    )
    convert.add_argument("raw_dir", type=str, help="path to raw directory")
    convert.set_defaults(func=convert_func)
    # remove duplicate
    rm_dup = subparsers.add_parser("rm_dup", help="remove duplicates of chapter name.")
    rm_dup.add_argument(
        "--result_dir",
        type=str,
        default=None,
        metavar="RESULT_PATH",
        help="path to result directory (default: replace files in raw directory)",
    )
    rm_dup.add_argument("raw_dir", type=str, help="path to raw directory")
    rm_dup.set_defaults(func=rm_dup_func)
    # epub parser
    epub = subparsers.add_parser("epub", help="make epub")
    subparsers_epub = epub.add_subparsers(title="modes", help="supported modes")
    # epub from_url parser
    from_url = subparsers_epub.add_parser("from_url", help="make epub from web site")
    from_url.add_argument(
        "--dup_chap",
        action="store_true",
        help="if specified, remove duplicate chapter title (default:  %(default)s)",
    )
    from_url.add_argument(
        "--start",
        type=int,
        default=1,
        help="start chapter index (default:  %(default)s)",
    )
    from_url.add_argument(
        "--stop",
        type=int,
        default=-1,
        help="stop chapter index, input -1 to get all chapters (default:  %(default)s)",
    )
    from_url.add_argument("url", type=str, help="full web site to novel info page")
    from_url.set_defaults(func=epub_from_url_func)
    # epub from_raw parser
    from_raw = subparsers_epub.add_parser(
        "from_raw", help="make epub from raw directory"
    )
    from_raw.add_argument(
        "--dup_chap",
        action="store_true",
        help="if specified, remove duplicate chapter title (default:  %(default)s)",
    )
    from_raw.add_argument(
        "--lang_code",
        default="vi",
        help="language code of the novel (default: %(default)s)",
    )
    from_raw.add_argument("raw_dir", type=str, help="path to raw directory")
    from_raw.set_defaults(func=epub_from_raw_func)
    return parser


class NovelutilsException(BaseException):
    """General exception for novelutils"""

    pass


def run_main():
    """Run main program."""
    try:
        sys.exit(main(sys.argv))
    except NovelutilsException as e:
        sys.stderr.write(f"novelutils:{str(e)}\n")
        sys.exit(1)


if __name__ == "__main__":
    run_main()
