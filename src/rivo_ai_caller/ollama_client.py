import requests

from .config import settings


class OllamaError(RuntimeError):
    pass


def check_connection(timeout: float = 2.5) -> tuple[bool, str]:
    try:
        response = requests.get(f"{settings.ollama_base_url}/api/tags", timeout=timeout)
        response.raise_for_status()
        payload = response.json()
        models = [item.get("name", "") for item in payload.get("models", [])]
        return True, ", ".join(models) if models else "Connected; no models downloaded yet."
    except requests.RequestException as exc:
        return False, str(exc)


def generate_reply(prompt: str, timeout: float = 90.0) -> str:
    body = {
        "model": settings.ollama_model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.4},
    }
    try:
        response = requests.post(
            f"{settings.ollama_base_url}/api/generate",
            json=body,
            timeout=timeout,
        )
        response.raise_for_status()
        return response.json().get("response", "").strip()
    except requests.RequestException as exc:
        raise OllamaError(str(exc)) from exc
