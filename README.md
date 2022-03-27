# NOVELUTILS

![python version](https://img.shields.io/badge/python-3.7+-blue) ![scrapy version](https://img.shields.io/badge/scrapy-2.5.1-blue) ![code style](https://img.shields.io/badge/code%20style-black-000000.svg)

## Developer

- Email: vuthuakhangit@gmail.com

## Description

- This tool can get text from websites and create epub.
- This project is for research purposes only.

## Installation

1. Download or clone this project.
2. Make sure Python 3.7 or above is installed.
3. Go to root folder of this project, using pip to install:

  ```bash
  pip install -e .
  ```

## Development

1. Download or clone this project.
2. Go to to root folder of this project.
3. Using pip to install this project in development mode (better with virtual env like conda):

```bash
pip install -e .[dev]
```

## Build

1. Download or clone this project.
2. Go to to root folder of this project.
3. Install and build this project with package "build":

```bash
pip install build
python -m build
```

## Ussage

- Create your own spider, using the template spider in `novelutils\app\spiders`.

- Commands:

  ```bash
  novelutils crawl https://example.com

  novelutils convert /path/to/raw/directory

  novelutils epub from_url https://example.com

  novelutils epub from_raw /path/to/raw/directory
  ```

- Examples:

    - Create epub fron the input link:

    ```shell
    novelutils epub from_url https://example.com
    ```

    - Download from chapter 1 to chapter 5:

    ```shell
    novelutils crawl --start 1 --stop 5 https://example.com
    ```

    - Download all chapters:

    ```shell
    novelutils crawl https://example.com
    ```

    - Download from chapter 3 to the end of the novel:

    ```shell
    novelutils --start 3 https://example.com
    ```

- Use novelutils package as script

    - Download novel via NovelCrawler

    ```python
    from novelutils.utils.crawler import NovelCrawler
    p = NovelCrawler(url="https://example.com")
    p.crawl(rm_raw=True, start_chap=3, stop_chap=8) 
    ```

    - Convert txt to xhtml by FileConverter:

    ```python
    from novelutils.utils.file import FileConverter
    c = FileConverter(raw_dir_path="/path/to/raw/dir")
    c.convert_to_xhtml(duplicate_chapter=False, rm_result=True, lang_code="vi")
    ```

    - Create epub from the input link:

    ```python
    from novelutils.utils.epub import EpubMaker
    e = EpubMaker()
    e.from_url("https://example.com", duplicate_chapter=False, start=1, stop=-1)
    ```

## Frameworks and packages, and IDEs are used in this project:

1. Package, framework:

- [Scrapy](https://scrapy.org/)

- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/)

2. IDEs:

- [Pycharm Community](https://www.jetbrains.com/pycharm/download)