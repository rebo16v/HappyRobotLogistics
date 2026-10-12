from fastapi import FastAPI
from tms.api.routes import tms_router

app = FastAPI(title="HappyRobot Logistics API")

app.include_router(tms_router)

if __name__ == "__main__":
    import uvicorn
    from dotenv import load_dotenv
    load_dotenv("./tms.env")
    uvicorn.run("tms.main:app", host="0.0.0.0", port=8080, reload=True)