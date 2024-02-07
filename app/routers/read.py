from fastapi import APIRouter, Depends, Request
from typing import Annotated

from pydantic_core import Url
from requests import HTTPError
from starlette.responses import HTMLResponse, RedirectResponse

from app import reader
from app.common import get_current_token

router = APIRouter(
    prefix='/read',
    tags=['read'],
)


@router.get('/html/{article_url:path}', response_class=HTMLResponse)
async def read_html(request: Request, article_url: Url):
    try:
        return await reader.get_html_content(str(article_url))
    except HTTPError as e:
        return RedirectResponse(str(article_url))


@router.get('/archive/{article_url}')
async def archive_article(request: Request, article_url: str, token: Annotated[str, Depends(get_current_token)]):
    return (await reader.archive_from_url(
        article_url=article_url,
        request_token=token
    ))
