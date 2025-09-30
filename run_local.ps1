
# Cambia al directorio donde está este script
Set-Location -Path $PSScriptRoot

# Permite ejecución temporal de scripts en esta sesión (no permanente)
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force

# Si no existe .venv\Scripts\python.exe, crea el entorno virtual
$py = ".\.venv\Scripts\python.exe"
if (!(Test-Path $py)) {
    Write-Host "[AnaBot] .venv no existe. Creando entorno virtual..."
    try {
        py -3 -m venv .venv
        Write-Host "[AnaBot] Entorno virtual creado con py -3."
    } catch {
        Write-Host "[AnaBot] py -3 falló, intentando con python..."
        python -m venv .venv
        Write-Host "[AnaBot] Entorno virtual creado con python."
    }
} else {
    Write-Host "[AnaBot] Entorno virtual .venv ya existe."
}

# Actualiza pip e instala dependencias si existe requirements.txt
Write-Host "[AnaBot] Actualizando pip..."
& $py -m pip install --upgrade pip
if (Test-Path "requirements.txt") {
    Write-Host "[AnaBot] Instalando dependencias desde requirements.txt..."
    & $py -m pip install -r requirements.txt
} else {
    Write-Host "[AnaBot] No se encontró requirements.txt. Instalando fastapi y uvicorn[standard]..."
    & $py -m pip install fastapi uvicorn[standard]
}

# Verifica que main.py exista en la raíz
if (!(Test-Path "main.py")) {
    Write-Host "[AnaBot] ERROR: No se encontró main.py en la raíz. Abortando."
    exit 1
}

# Abre el endpoint /health en el navegador predeterminado
Write-Host "[AnaBot] Abriendo http://127.0.0.1:8080/health en el navegador..."
Start-Process "http://127.0.0.1:8080/health"

# Inicia el servidor Uvicorn
Write-Host "[AnaBot] Iniciando Uvicorn en http://127.0.0.1:8080 ..."
& $py -m uvicorn main:app --host 0.0.0.0 --port 8080
