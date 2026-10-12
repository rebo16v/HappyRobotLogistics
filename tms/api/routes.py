from fastapi import APIRouter, Request
from tms.core.tcp_client import make_request

tms_router = APIRouter()

@tms_router.get("/")
async def root():
    return {"message": "TMS API"}


@tms_router.get("/load_query")
async def load_query(request: Request):
    params = dict(request.query_params)
    return make_request("LOAD_QUERY", params)


@tms_router.get("/load_get")
async def load_get(request: Request):
    params = dict(request.query_params)
    return make_request("LOAD_GET", params)


@tms_router.get("/load_book")
async def load_book(request: Request):
    params = dict(request.query_params)
    return make_request("LOAD_BOOK", params)
