"""Get novel from domain example.

.. _Web site:
   https://example.com

"""
from pathlib import Path

import scrapy


class DemoSpider(scrapy.Spider):
    """Define spider for domain: demo."""

    name = "example"

    def __init__(
        self,
        url: str,
        save_path: Path,
        start_chap: int,
        stop_chap: int,
        *args,
        **kwargs,
    ):
        """Initialize the attributes for this spider.

        Parameters
        ----------
        url : str
            The link of the novel information page.
        save_path : Path
            Path of raw directory.
        start_chap : int
            Start crawling from this chapter.
        stop_chap : int
            Stop crawling from this chapter, input -1 to get all chapters.
        """
        super().__init__(*args, **kwargs)
        self.start_urls = [url]
        self.save_path = save_path
        self.start_chap = start_chap
        self.stop_chap = stop_chap
        self.toc = []

    def parse(self, response: scrapy.http.Response, **kwargs):
        """Extract info of the novel and get the link of the
        table of content (toc).

        Parameters
        ----------
        response : Response
            The response to parse.

        Yields
        ------
        Request
            Request to the cover image page and toc page.
        """
        # download cover
        yield scrapy.Request(
            url=response.xpath('//*[@id="cover"]/img/@src').get(),
            callback=self.parse_cover,
        )
        get_info(response, self.save_path)
        toc_link = "https://example.com/toc"
        yield scrapy.Request(url=toc_link, callback=self.parse_link)

    def parse_cover(self, response: scrapy.http.Response):
        """Download the cover of novel.

        Parameters
        ----------
        response : Response
            The response to parse.
        """
        (self.save_path / "cover.jpg").write_bytes(response.body)

    def parse_link(self, response: scrapy.http.Response):
        """Extract link of the start chapter.

        Parameters
        ----------
        response : scrapy.http.Response
            The response to parse.

        Yields
        ------
        scrapy.Request
            Request to the start chapter.
        """
        self.toc.extend(
            [
                x.strip()
                for x in response.xpath(
                    '//a[contains(@class,"link-chap-")]/@href'
                ).getall()
            ]
        )
        yield scrapy.Request(
            url=self.toc[self.start_chap - 1],
            meta={"id": self.start_chap},
            callback=self.parse_content,
        )

    def parse_content(self, response: scrapy.http.Response):
        """Extract the content of chapter.

        Parameters
        ----------
        response : Response
            The response to parse.

        Yields
        ------
        Request
            Request to the next chapter.
        """
        get_content(response, self.save_path)
        if (response.meta["id"] == len(self.toc)) or response.meta[
            "id"
        ] == self.stop_chap:
            raise scrapy.exceptions.CloseSpider(reason="Done")
        response.request.headers[b"Referer"] = [str.encode(response.url)]
        yield scrapy.Request(
            url=self.toc[response.meta["id"]],
            headers=response.request.headers,
            meta={"id": response.meta["id"] + 1},
            callback=self.parse_content,
        )


def get_info(response: scrapy.http.Response, save_path: Path):
    """Get info of this novel.

    Parameters
    ----------
    response : Response
        The response to parse.
    save_path : Path
        Path of raw directory.
    """
    # get title
    title = response.xpath("//*[@id='title']/text()").get()
    author = response.xpath("//*[@id='author']/text()").get()
    types = response.xpath("//*[@id='types']/p/text()").getall()
    foreword = response.xpath("//*[@id='foreword']/p/text()").getall()
    info = []
    info.append(title)
    info.append(author)
    info.append(response.request.url)
    info.append(types)
    info.extend(foreword)
    (save_path / "foreword.txt").write_text("\n".join(info), encoding="utf-8")


def get_content(response: scrapy.http.Response, save_path: Path):
    """Get content of this novel.

    Parameters
    ----------
    response : Response
        The response to parse.
    save_path : Path
        Path of raw directory.
    """
    # get chapter
    chapter = response.xpath("//*[@id='chapter-title']/text()").get()
    # get content
    content = response.xpath("///*[@id='chapter']/p/text()").getall()
    content.insert(0, chapter)
    (save_path / f'{str(response.meta["id"])}.txt').write_text(
        "\n".join([x.strip() for x in content if x.strip() != ""]), encoding="utf-8"
    )
