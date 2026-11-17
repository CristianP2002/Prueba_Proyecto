# Comparación inicial y propuesta diferencial

Esta comparación es una hipótesis de diseño para orientar la investigación académica; no sustituye una evaluación documentada de productos reales.

| Función común en soluciones de parqueadero | PARKIA |
|---|---|
| Registro de placas | Incluido |
| Control de espacios | Incluido |
| Cálculo de tarifa | Incluido |
| Registro de pagos | Incluido como simulación |
| Cupones | Incluido |
| Reportes | Panel e historial |
| Analítica asistida por IA local | Diferenciador propuesto |
| Procesamiento local de consultas | Ollama + LangChain |

## Diferenciador
PARKIA prepara indicadores desde la base de datos y los entrega como contexto estructurado al modelo local. La IA interpreta esos indicadores y responde preguntas en lenguaje natural. Los cálculos numéricos se realizan en Python/SQL, no se delegan al modelo.

## Investigación pendiente
Para la entrega final, seleccionar al menos tres sistemas reales, consultar sus páginas oficiales, registrar fecha y funciones verificadas, y completar una matriz con fuentes. No afirmar que una función no existe si no se comprobó.
