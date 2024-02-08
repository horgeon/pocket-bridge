import hashlib
from typing import Mapping, Optional

from fastapi_cache.decorator import cache
from requests import HTTPError
from starlette.datastructures import URL
from starlette.responses import Response

from feedgen.feed import FeedGenerator
from datetime import datetime, timezone

from app import reader, common
from app.common import get_base_url
from app.settings import settings


class RSSResponse(Response):
    '''
    A subclass of starlette.responses.Response which will set the content to an RSS XML document. It takes one argument,
    a FeedGenerator object which will be converted to an XML document.
    '''
    media_type = 'application/xml'
    charset = 'utf-8'

    @property
    def etag(self) -> str:
        '''
        Generates a SHA1 sum of the body of the response so that the server can
        support the ETag protocol.

        :return: The SHA1 hex digest of the body of the response
        :rtype: str
        '''
        return hashlib.sha1(self.body).hexdigest()

    def init_headers(self, headers: Mapping[str, str] = None) -> None:
        newheaders = {
            'Accept-Range': 'bytes',
            'Connection': 'Keep-Alive',
            'ETag': self.etag,
            'Keep-Alive': 'timeout=5, max=100',
        }

        headers = headers or {}
        for headername in newheaders:
            if headername not in headers:
                headers[headername] = newheaders[headername]
        super().init_headers(headers)

    def render(self, feed: FeedGenerator) -> bytes:
        return feed.rss_str(pretty=True)


class AtomResponse(RSSResponse):
    '''
    A subclass of RSSResponse which will set the content to an Atom XML document. It takes one argument, a FeedGenerator
    object which will be converted to an XML document.
    '''
    media_type = 'application/xml'
    charset = 'utf-8'

    def render(self, feed: FeedGenerator) -> bytes:
        return feed.atom_str(pretty=True)


async def _pocket_api_to_feed(articles: dict[str, object], request_url: URL, title_part: str, request_token: str,
                              get_full_content: bool = False) -> FeedGenerator:
    feed = FeedGenerator()

    feed.id(str(request_url))
    feed.title(f'Pocket - {title_part}')
    feed.description(f'{title_part} items from Pocket')
    feed.link(href=str(request_url), rel='self')

    base_url = get_base_url(request_url)

    for article_id, article in articles['list'].items():
        title = article['resolved_title'] if len(article['resolved_title']) else article['given_title']
        url = article['resolved_url'] if len(article['resolved_url']) > 0 else article['given_url']
        reader_url = str(reader.get_html_url(base_url=base_url, article_url=article['resolved_url'],
                                             request_token=request_token))

        entry = feed.add_entry()
        entry.guid(article_id)
        entry.id(url)
        entry.title(title)
        entry.link(href=reader_url)
        entry.updated(datetime.fromtimestamp(int(article['time_updated']), timezone.utc))
        entry.published(datetime.fromtimestamp(int(article['time_added']), timezone.utc))

        summary = article['excerpt'] if 'excerpt' in article else title
        entry.summary(summary)
        if get_full_content:
            try:
                entry.description((await reader.get_html_content(url=url)), isSummary=False)
            except HTTPError as e:
                entry.description(f'<p>{e.strerror}</p>', isSummary=False)
        else:
            entry.description(summary, isSummary=True)

        # if 'time_to_read' in article:
        #    entry.summary(f'Estimated reading time: {article["time_to_read"]}m')

    return feed


@cache(expire=settings.cache.pocket_list_expiration)
async def _get_pocket_list(request_token: str, tag: Optional[str] = None) -> dict:
    pocket = common.get_pocket_instance(request_token)
    if pocket is None:
        raise "Invalid request token."

    if tag is not None:
        return pocket.retrieve(state='unread', sort='newest', tag=tag)

    return pocket.retrieve(state='unread', sort='newest')


async def retrieve_feed(request_url: URL, request_token: str, tag: Optional[str] = None,
                        get_full_content: bool = False) -> FeedGenerator:

    if tag is not None:
        title_part = f'Unread items tagged {tag}' if tag != '_untagged_' else 'Unread and untagged items'
    else:
        title_part = 'Unread items'

    return await _pocket_api_to_feed(
        request_url=request_url,
        title_part=title_part,
        articles=(await _get_pocket_list(request_token=request_token, tag=tag)),
        request_token=request_token,
        get_full_content=get_full_content
    )
