# 1) Verificación manual del challenge (debe mostrar 12345)
https://<TU-DOMINIO>/webhook/whatsapp?hub.mode=subscribe&hub.verify_token=<EL_TOKEN>&hub.challenge=12345

# Fallback legacy (por si acaso):
https://<TU-DOMINIO>/webhook/whatsapp?mode=subscribe&token=<EL_TOKEN>&challenge=12345

# 2) Ver token cargado (debug temporal)
https://<TU-DOMINIO>/__debug/wa_token

# 3) Envío saliente por Graph (PowerShell/Windows con curl.exe)
$WA_TOKEN="REEMPLAZAR"
$PHONE_ID="REEMPLAZAR"
$TO="5939XXXXXXXX"
curl.exe -s -X POST "https://graph.facebook.com/v19.0/$PHONE_ID/messages" ^
  -H "Authorization: Bearer $WA_TOKEN" ^
  -H "Content-Type: application/json" ^
  -d "{`"messaging_product`":`"whatsapp`",`"to`":`"$TO`",`"type`":`"text`",`"text`":{`"body`":`"Hola desde Graph API`"}}"
