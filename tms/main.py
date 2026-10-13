from fastapi import FastAPI, Response
from tms.api.routes import tms_router
import httpx


app = FastAPI(title="HappyRobot Logistics API")

app.include_router(tms_router)

fmcsa_app = FastAPI(title="FMCSA")

@fmcsa_app.get("/check_mc/{mc_number}")
async def check_mc(mc_number: str, webKey: str):
    client = httpx.AsyncClient(follow_redirects=True)
    result = await(client.request("GET", "https://mobile.fmcsa.dot.gov/qc/services/carriers/docket-number/{mc_number}?webKey={webKey}"))
    print(f"RESPONSE: {result.content} \nHEADERS: {result.headers}")
    return Response(status_code=result.status_code, headers=result.headers, content=result.content)

app.mount("/fmcsa", fmcsa_app)

if __name__ == "__main__":
    import uvicorn
    from dotenv import load_dotenv
    load_dotenv("./tms.env")
    uvicorn.run("tms.main:app", host="0.0.0.0", port=8080, reload=True)