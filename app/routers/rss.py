from fastapi import APIRouter, Depends, Request
from typing import Annotated

from app.common import get_current_token
from app.feed import RSSResponse, retrieve_feed

router = APIRouter(
    prefix='/rss',
    tags=['rss'],
    # responses={404: {'description': 'Not found'}},
)


@router.get('/unread', response_class=RSSResponse)
async def rss_unread(request: Request, token: Annotated[str, Depends(get_current_token)], reader: bool = False, full_content: bool = False):
    return RSSResponse((await retrieve_feed(
        request_url=request.url,
        request_token=token,
        use_reader_url=reader,
        get_full_content=full_content
    )))


@router.get('/unread/{tag}', response_class=RSSResponse)
async def rss_unread(tag: str, request: Request, token: Annotated[str, Depends(get_current_token)], reader: bool = False, full_content: bool = False):
    return RSSResponse((await retrieve_feed(
        request_url=request.url,
        request_token=token,
        tag=tag,
        use_reader_url=reader,
        get_full_content=full_content
    )))
