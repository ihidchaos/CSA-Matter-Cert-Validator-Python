from fastapi import FastAPI, UploadFile

from cd.parser import parse_cd

app = FastAPI()


@app.get("/status")
def get_status():
    return {"status": "ok"}


@app.post("/validate_cd")
async def validate_cd(file: UploadFile):
    try:
        file_bytes = await file.read()
        print(file_bytes)
        data = file_bytes
        cd = parse_cd(data)
        print(cd)
    except Exception as e:
        return {"error111": str(e)}

    if not cd:
        return {"error": "Failed to parse CD file"}

    report_data = validate_cd(cd)
    return report_data


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
