from fastapi import FastAPI, UploadFile

from cd.parser import parse_cd
from validator.validate import validate_cd as real_validate_cd

app = FastAPI()


@app.get("/status")
def get_status():
    return {"status": "ok"}


@app.post("/validate_cd")
async def validate_cd(file: UploadFile):
    try:
        cd = parse_cd(await file.read())
    except Exception as e:
        return {"error": str(e)}

    if not cd:
        return {"error": "Failed to parse CD file"}

    report_data = real_validate_cd(cd)
    return report_data


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
