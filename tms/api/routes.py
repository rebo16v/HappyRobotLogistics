import os

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

@tms_router.get("/carrier_get/{mc_number}")
async def carrier_get(mc_number: str):
    if (mc_number == "123456"):
        return {"carrier": {"mc_number": mc_number, "email": os.environ["DEMO_CARRIER_EMAIL"], "phone": os.environ["DEMO_CARRIER_PHONE"]}}
    else:
        return {"error": {"code": "unknown_carrier", "message": f"Carrier {mc_number} not found"}}
