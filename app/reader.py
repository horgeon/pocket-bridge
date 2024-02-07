from hashlib import sha256
import urllib.parse

from fastapi_cache.decorator import cache
from starlette.datastructures import URL

import requests
from readability import Document

from app import common
from app.settings import settings


def get_read_signature(url: str):
    return sha256(settings.read_secret_key.encode('utf-8') + url.encode('utf-8')).hexdigest()


def validate_read_signature(url: str, signature: str):
    return signature == get_read_signature(url)


"""
def get_reader_url(base_url: str, article_url: str):
    return f'{base_url}read/{urllib.parse.quote(article_url)}?signature={get_read_signature(article_url)}'
"""


def get_html_url(base_url: URL, article_url: str, request_token: str):
    return base_url.replace(path=f'/read/html/{urllib.parse.quote(article_url, safe="")}', username='bridge', password=request_token)


@cache(expire=settings.cache.readability_expiration)
async def get_html_content(url: str) -> str:
    response = requests.get(url)
    response.raise_for_status()
    
    return Document(response.text).summary()


async def archive_from_url(request_token: str, article_url: str) -> dict:
    pocket = common.get_pocket_instance(request_token)
    if pocket is None:
        raise "Invalid request token."

    items = pocket.retrieve(state='all', search=article_url)['list']
    if len(items) == 0:
        raise 'Invalid Article URL.'

    pocket.archive(items.keys()[0])
    return pocket.commit()
