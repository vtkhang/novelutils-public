"""Define FileConverter class."""
import logging
from pathlib import Path
from shutil import rmtree, copy

import unicodedata as ud
from importlib_resources import files

from novelutils import data
from novelutils.utils.typehint import PathStr, DictPath

_logger = logging.getLogger(__name__)


class FileConverter:
    """This class define clean method and convert to xhtml method."""

    def __init__(self, raw_dir_path: PathStr, result_dir_path: PathStr = None) -> None:
        """Init path of raw directory and result directory.

        Args:
            raw_dir_path: path of raw directory
            result_dir_path: path of result directory

        Returns:
            None
        """
        self.x = Path(raw_dir_path)
        if not self.x.exists():
            raise FileConverterError(f"Raw directory not found: {self.x}")
        if result_dir_path is None:
            self.y = self.x.parent / "result_dir"
        else:
            self.y = Path(result_dir_path)
        if not self.y.exists():
            self.y.mkdir(parents=True)
            _logger.info(
                "Result directory not found, auto created at: %s", self.y.resolve()
            )
        self.txt: DictPath = {}  # use to track txt files in result directory
        self.xhtml: DictPath = {}  # use to track txt files in result directory

    def clean(self, duplicate_chapter: bool, rm_result: bool) -> int:
        """Clean all raw files in raw directory.

        Args:
            duplicate_chapter: if specified, remove duplicate chapter title
            rm_result: if specified, remove all old files in result directory

        Returns:
            int: -1 if raw directory empty
        """
        if not any(self.x.iterdir()):
            return -1
        if rm_result is True:
            _logger.info("Remove existing files in: %s", self.y.resolve())
            self._rm_result()
        # copy cover image to result directory
        cover_path = self.x / "cover.jpg"
        tmp = self.y / cover_path.name
        if tmp != cover_path:
            copy(cover_path, tmp)
        self.txt[-1] = tmp
        # clean foreword.txt
        fw_path = self.x / "foreword.txt"
        fw_lines = [
            line.strip() for line in fw_path.read_text(encoding="utf-8").splitlines()
        ]
        r = fw_lines[:4]
        r.extend(fix_bad_indent(tuple(fw_lines[4:])))
        tmp = self.y / fw_path.name
        tmp.write_text("\n".join(r), encoding="utf-8")
        self.txt[0] = tmp
        # clean chapter.txt
        r = fw_path.with_suffix(".temp")
        fw_path.rename(r)
        f_list = [item for item in self.x.glob("*.txt") if item.is_file()]
        r.rename(fw_path)
        for chapter in f_list:
            c_lines = [
                line.strip()
                for line in chapter.read_text(encoding="utf-8").splitlines()
            ]
            if duplicate_chapter is True:
                c_lines.pop(1)
            tmp = self.y / chapter.name
            tmp.write_text("\n".join(fix_bad_indent(tuple(c_lines))), encoding="utf-8")
            self.txt[int(chapter.stem)] = tmp
        _logger.info("Done cleaning. View result at: %s", self.y.resolve())

    def convert_to_xhtml(
            self, duplicate_chapter: bool, rm_result: bool, lang_code: str
    ) -> int:
        """Clean files and convert to XHTML.

        Args:
            duplicate_chapter: if specified, remove duplicate chapter title
            rm_result: if specified, remove all old files in result directory
            lang_code: language code of the novel

        Returns:
            int: -1 if raw directory empty
        """
        if not any(self.x.iterdir()):
            return -1
        # Check if default template is exist, if not throw exception
        # template of chapter
        txtp = files(data).joinpath(r"template/OEBPS/Text")
        ctp = txtp / "c1.xhtml"
        if ctp.exists() is False or ctp.is_dir():
            raise FileConverterError(f"Chapter template not found: {ctp}")
        # template of foreword
        fwtp = txtp / "foreword.xhtml"
        if fwtp.exists() is False or fwtp.is_dir():
            raise FileConverterError(f"Foreword template not found: {ctp}")
        # remove old files in result directory
        if rm_result is True:
            _logger.info("Remove existing files in: %s", self.y.resolve())
            self._rm_result()
        # copy cover image to result dir
        cover_path = self.x / "cover.jpg"
        tmp = self.y / cover_path.name
        if tmp != cover_path:
            copy(cover_path, tmp)
        self.xhtml[-1] = tmp
        # clean foreword.txt
        fwp = self.x / "foreword.txt"
        fw_lines = [
            escape_char(line.strip())
            for line in fwp.read_text(encoding="utf-8").splitlines()
        ]
        foreword_p_tag_list = [
            ("<p>" + line + "</p>") for line in fix_bad_indent(tuple(fw_lines[4:]))
        ]
        foreword_title = "Lời tựa"
        if lang_code == "zh":
            foreword_title = "内容简介"
        tmp = self.y / f"{fwp.stem}.xhtml"
        tmp.write_text(
            fwtp.read_text(encoding="utf-8").format(
                foreword_title=foreword_title,
                novel_title=fw_lines[0],
                author_name=fw_lines[1],
                url=fw_lines[2],
                types=fw_lines[3],
                foreword_p_tag_list="\n\n  ".join(foreword_p_tag_list),
            ),
            encoding="utf-8",
        )
        self.xhtml[0] = tmp
        # clean chapter.txt
        r = fwp.with_suffix(".temp")
        fwp.rename(r)
        f_list = [item for item in self.x.glob("*.txt") if item.is_file()]
        r.rename(fwp)
        for chapter in f_list:
            c_lines = [
                escape_char(line.strip())
                for line in chapter.read_text(encoding="utf-8").splitlines()
            ]
            if duplicate_chapter is True:
                c_lines.pop(1)
            tmp = self.y / f"c{chapter.stem}.xhtml"
            try:
                chapter_p_tag_list = [
                    "<p>" + line + "</p>" for line in fix_bad_indent(tuple(c_lines[1:]))
                ]
                tmp.write_text(
                    ctp.read_text(encoding="utf-8").format(
                        chapter_title=c_lines[0],
                        chapter_p_tag_list="\n\n  ".join(chapter_p_tag_list),
                    ),
                    encoding="utf-8",
                )
            except IndexError:
                _logger.warning("Empty chapter: %s", tmp)
            self.xhtml[int(chapter.stem)] = tmp
        _logger.info("Done converting. View result at: %s", self.y.resolve())

    def _rm_result(self) -> int:
        """Remove all files in result directory.

        Returns:
            int: -1 if result directory is raw directory
        """
        if self.x == self.y:
            return -1
        rmtree(self.y)
        self.y.mkdir()
        self.txt = {}
        self.xhtml = {}

    def _update_file_list(self, ext: str) -> None:
        """Remove all files not existing.

        Returns:
            None
        """
        # https://www.geeksforgeeks.org/python-delete-items-from-dictionary-while-iterating/
        t = {}
        if ext == "txt":
            t = self.txt
        elif ext == "xhtml":
            t = self.xhtml
        for key in list(t):
            if not t[key].exists():
                del t[key]

    def get_result_dir(self) -> Path:
        """Return path of result directory.

        Returns:
            Path: path of result directory
        """
        return self.y

    def get_file_list(self, ext: str) -> tuple:
        """Return result file paths list.

        Args:
            ext: extension of files [txt, xhtml]

        Returns:
            tuple: file paths list
        """
        t = {}
        if ext == "txt":
            self._update_file_list(ext="txt")
            t = self.txt
        elif ext == "xhtml":
            self._update_file_list(ext="xhtml")
            t = self.xhtml
        return tuple([value for key, value in sorted(t.items())])


class FileConverterError(Exception):
    """File converter exception."""

    pass


def fix_bad_indent(data_in: tuple) -> tuple:
    """Remove empty lines, bad indentation,...

    Args:
      data_in: list of lines

    Returns:
        tuple: cleaned text lines
    """
    temp = []
    # filter the '' out of data_in and store to temp
    for x in data_in:
        if x != "":
            temp.append(x.replace("\n", " "))
    # Fix the content when it was composed by Notepad
    temp2 = [temp[0]]
    pa = ",:"
    for x in range(1, len(temp)):
        t2 = ud.category(temp[x][0])[1]
        if (temp2[-1][-1] in pa) or (t2 == "l"):
            temp2[-1] += " " + temp[x]
        else:
            temp2.append(temp[x])
    return tuple(temp2)


def escape_char(text: str):
    """Escape special character for XHTML.

    Args:
      text: input string

    Returns:

    """
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
