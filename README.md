# PARKIA — Sistema inteligente de gestión de parqueaderos

Proyecto académico construido con Python, Flask, SQLite, POO, Git/GitHub y conexión opcional a Ollama mediante LangChain.

## Requisitos
- Python 3.10 o superior
- Git
- Navegador moderno
- Opcional para IA: Ollama instalado y un modelo descargado

## Instalación (Windows PowerShell)
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```
Abrir: http://127.0.0.1:5000

La base de datos `instance/parkia.db` y los espacios iniciales se crean automáticamente.

## Funciones
- Registro de vehículos (carro, moto y bicicleta).
- Ingreso y asignación automática de espacio compatible.
- Cálculo de estadía y salida.
- Pagos simulados en efectivo, tarjeta o QR.
- Cupones porcentuales.
- Historial de pagos y panel de ocupación.
- Asistente de análisis con Ollama + LangChain.

## Activar IA local
1. Instala Ollama desde https://ollama.com/
2. Descarga un modelo, por ejemplo: `ollama pull llama3.2`
3. Asegúrate de que Ollama esté ejecutándose.
4. Instala dependencias: `pip install -r requirements.txt`
5. Reinicia PARKIA y abre el módulo Asistente IA.

Variables opcionales:
- `OLLAMA_BASE_URL` (por defecto `http://localhost:11434`)
- `OLLAMA_MODEL` (por defecto `llama3.2`)

Si Ollama no está disponible, el resto de la aplicación sigue funcionando.

## Reglas académicas de demostración
- La tarifa inicial está configurada en COP $3.000 por hora en `config.py`.
- Se cobra por hora iniciada, con mínimo una hora.
- Los métodos QR y tarjeta son simulaciones; no se procesa dinero.
- Los cupones descuentan entre 1% y 80%.
- No incluye autenticación real ni despliegue de producción.

## Estructura
```text
PARKIA/
├── app.py
├── config.py
├── models/
│   ├── database.py
│   └── entities.py
├── services/
│   ├── parking_service.py
│   └── ai_service.py
├── templates/
├── static/
├── docs/
└── requirements.txt
```

## Convención de commits
Usar Conventional Commits:
- `feat:` nueva funcionalidad
- `fix:` corrección
- `docs:` documentación
- `style:` cambios visuales/formato sin cambiar lógica
- `refactor:` reorganización interna
- `test:` pruebas
- `chore:` mantenimiento

Ejemplos:
```bash
git add .
git commit -m "feat: agregar registro de vehiculos"
git commit -m "feat: implementar pagos simulados"
git commit -m "feat: integrar asistente local con ollama"
git commit -m "docs: agregar bitacora de uso de IA"
```

## Bitácora de IA
Completar `docs/bitacora_ia.xlsx` cada vez que se utilice IA durante el desarrollo. Registrar herramienta/modelo, propósito, prompt resumido, resultado, cambios realizados y validación humana. No registrar datos personales o secretos.

## Alcance y seguridad
Este es un prototipo académico. Antes de publicarlo se debe agregar autenticación, autorización, protección CSRF, validación reforzada, gestión segura de secretos, pruebas, HTTPS y servidor WSGI de producción. Los datos de ejemplo deben ser ficticios.
