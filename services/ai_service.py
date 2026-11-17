import json
class AIService:
    def __init__(self, config):
        self.base_url=config.get("OLLAMA_BASE_URL","http://localhost:11434")
        self.model=config.get("OLLAMA_MODEL","llama3.2")
    def is_available(self):
        try:
            import requests
            return requests.get(self.base_url + "/api/tags", timeout=2).ok
        except Exception: return False
    def analyze(self, question, snapshot):
        if not question.strip(): return "Escribe una pregunta para analizar los datos."
        prompt = ("Eres PARKIA, asistente de análisis de un parqueadero. "
                  "Responde en español, con claridad. Usa exclusivamente los datos JSON. "
                  "Si faltan datos, dilo; no inventes estadísticas.\\nDATOS: "
                  + json.dumps(snapshot, ensure_ascii=False) + "\\nPREGUNTA: " + question)
        try:
            from langchain_ollama import ChatOllama
            from langchain_core.messages import HumanMessage
            llm=ChatOllama(model=self.model, base_url=self.base_url, temperature=0.2)
            return llm.invoke([HumanMessage(content=prompt)]).content
        except Exception as exc:
            return ("No fue posible consultar Ollama. Verifica que esté instalado, iniciado y que "
                    f"el modelo '{self.model}' esté descargado. Detalle: {exc}")
