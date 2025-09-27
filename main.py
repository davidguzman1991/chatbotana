import json
import os

import httpx
from fastapi import FastAPI, Header, Request, Query, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse

app = FastAPI()


@app.get("/health")
async def health():
    return {"ok": True}


@app.get("/", response_class=PlainTextResponse)
async def root():
    return "Servidor AnaBot activo"


@app.api_route("/webhook", methods=["GET", "POST"], include_in_schema=False)
async def noop_webhook():
    return PlainTextResponse("ok")


TG_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TG_SECRET = os.getenv("TELEGRAM_SECRET_TOKEN", "")


async def tg_send(chat_id: int, text: str):
    if not TG_TOKEN:
        print("WARN: TELEGRAM_BOT_TOKEN vacio")
        return
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(url, json={"chat_id": chat_id, "text": text})
            try:
                resp.raise_for_status()
            except httpx.HTTPError as exc:
                print("TG send error:", exc, "resp:", resp.text)
    except Exception as exc:
        print("TG send unexpected error:", exc)


@app.post("/webhook/telegram")
async def telegram_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: str | None = Header(None),
):
    if TG_SECRET and x_telegram_bot_api_secret_token != TG_SECRET:
        raise HTTPException(status_code=401, detail="Bad secret token")

    update = await request.json()
    print("TG update:", json.dumps(update, ensure_ascii=False))

    message = update.get("message") or update.get("edited_message")
    if message and "text" in message:
        chat_id = message["chat"]["id"]
        text = message["text"]
        await tg_send(chat_id, f"AnaBot recibio: {text}")
    return JSONResponse({"ok": True})


WA_TOKEN = os.getenv("WHATSAPP_TOKEN", "")
WA_PHONE_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
WA_VERIFY = os.getenv("WHATSAPP_VERIFY_TOKEN", "")

WA_MSG_URL = "https://graph.facebook.com/v19.0/{phone_id}/messages"


async def wa_send_text(to_number: str, text: str):
    if not (WA_TOKEN and WA_PHONE_ID):
        print("WARN WA: Falta WHATSAPP_TOKEN o WHATSAPP_PHONE_NUMBER_ID.")
        return
    url = WA_MSG_URL.format(phone_id=WA_PHONE_ID)
    headers = {
        "Authorization": f"Bearer {WA_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": text},
    }
    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.post(url, headers=headers, json=payload)
        if resp.status_code >= 400:
            print("WA send error:", resp.status_code, resp.text)


@app.get("/webhook/whatsapp")
async def wa_verify(
    mode: str | None = Query(None, alias="hub.mode"),
    challenge: str | None = Query(None, alias="hub.challenge"),
    token: str | None = Query(None, alias="hub.verify_token"),
    mode2: str | None = Query(None, alias="mode"),
    challenge2: str | None = Query(None, alias="challenge"),
    token2: str | None = Query(None, alias="token"),
):
    m = (mode or mode2 or "").strip()
    t = (token or token2 or "").strip()
    c = (challenge or challenge2 or "")
    if m == "subscribe" and t == (WA_VERIFY or "").strip():
        return int(c) if c.isdigit() else (c or "")
    raise HTTPException(status_code=403, detail="Verification failed")


@app.post("/webhook/whatsapp")
async def wa_webhook(request: Request):
    body = await request.json()
    try:
        entry = (body.get("entry") or [{}])[0]
        changes = (entry.get("changes") or [{}])[0]
        value = changes.get("value") or {}
        messages = value.get("messages") or []
        statuses = value.get("statuses") or []

        if messages:
            for m in messages:
                from_ = m.get("from")
                msg_type = m.get("type")
                text = ""
                if msg_type == "text":
                    text = m["text"].get("body", "")
                elif msg_type == "reaction":
                    text = f"Reaccion: {m['reaction'].get('emoji','')}"
                else:
                    text = f"Tipo {msg_type} recibido."
                if from_:
                    await wa_send_text(from_, f"Ana 🤖 te leyo: {text}")

        if statuses:
            print("WA statuses:", json.dumps(statuses))

    except Exception as e:
        print("WA parse/send error:", repr(e), "BODY:", json.dumps(body))
    return {"ok": True}


@app.get("/__debug/wa_token")
async def debug_wa():
    masked = "*" * max(0, len(WA_VERIFY or "") - 4) + (WA_VERIFY[-4:] if WA_VERIFY else "")
    return {"len": len(WA_VERIFY or ""), "repr": repr(WA_VERIFY or ""), "masked_end": masked}
# TODO: remove __debug/wa_token after verifying WhatsApp configuration.
