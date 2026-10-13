from fastapi import FastAPI,Request, Response
from fastapi.responses import StreamingResponse
from tms.api.routes import tms_router
import httpx


app = FastAPI(title="HappyRobot Logistics API")

app.include_router(tms_router)

fmcsa_app = FastAPI(title="FMCSA")

@fmcsa_app.get("/check_mc/{mc_number}")
async def check_mc(mc_number: str):
    async with httpx.AsyncClient() as client:
        result = await(client.request("GET", "https://mobile.fmcsa.dot.gov/qc/services/carriers/docket-number/{mc_number}?webKey=cdc33e44d693a3a58451898d4ec9df862c65b954"))
        return StreamingResponse(
            result.aiter_bytes(),
            status_code=result.status_code,
            media_type=result.headers.get("content-type")
        )

app.mount("/fmcsa", fmcsa_app)

if __name__ == "__main__":
    import uvicorn
    from dotenv import load_dotenv
    load_dotenv("./tms.env")
    uvicorn.run("tms.main:app", host="0.0.0.0", port=8080, reload=True)