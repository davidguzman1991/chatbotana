
from fastapi import FastAPI, Response

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

# Endpoint opcional para evitar 404 ruidoso de favicon
@app.get("/favicon.ico")
def favicon():
    return Response(status_code=204)
