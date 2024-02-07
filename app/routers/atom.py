from fastapi import APIRouter, Depends, Request
from typing import Annotated

from app.common import get_current_token
from app.feed import AtomResponse, retrieve_feed

router = APIRouter(
    prefix='/atom',
    tags=['atom'],
    # responses={404: {'description': 'Not found'}},
)


@router.get('/unread', response_class=AtomResponse)
async def atom_unread(request: Request, token: Annotated[str, Depends(get_current_token)]):
    return AtomResponse((await retrieve_feed(
        request_url=request.url,
        request_token=token
    )))


@router.get('/unread/{tag}', response_class=AtomResponse)
async def atom_unread(tag: str, request: Request, token: Annotated[str, Depends(get_current_token)]):
    return AtomResponse((await retrieve_feed(
        request_url=request.url,
        request_token=token,
        tag=tag
    )))


@router.get('/full/unread', response_class=AtomResponse)
async def atom_unread(request: Request, token: Annotated[str, Depends(get_current_token)]):
    return AtomResponse((await retrieve_feed(
        request_url=request.url,
        request_token=token,
        get_full_content=True
    )))


@router.get('/full/unread/{tag}', response_class=AtomResponse)
async def atom_unread(tag: str, request: Request, token: Annotated[str, Depends(get_current_token)]):
    return AtomResponse((await retrieve_feed(
        request_url=request.url,
        request_token=token,
        tag=tag,
        get_full_content=True
    )))
