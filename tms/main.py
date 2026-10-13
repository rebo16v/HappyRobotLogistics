from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from tms.api.routes import tms_router
import httpx


app = FastAPI(title="HappyRobot Logistics API")

app.include_router(tms_router)

fmcsa_app = FastAPI(title="FMCSA")

@fmcsa_app.get("/check_mc/{mc_number}")
async def check_mc(mc_number: str, webKey: str):
    headers={#"Accept": "*/*",
             #"Accept-Encoding": "deflate, gzip",
             #"User-Agent": "Mozilla/5.0(Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36(KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36",
             "Host": "mobile.fmcsa.dot.gov"
             }
    client = httpx.AsyncClient(follow_redirects=True)
    result = await(client.request("GET",
                                  f"https://mobile.fmcsa.dot.gov/qc/services/carriers/docket-number/{mc_number}?webKey={webKey}",
                                  headers=headers))
    print(f"RESPONSE: {result.content} \nHEADERS: {result.headers}")
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