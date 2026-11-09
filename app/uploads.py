"""Upload das fotos dos cupcakes (US10, RN01, RNF01).

Por segurança, o arquivo NÃO é aceito pela extensão do nome (que o usuário pode
trocar): os primeiros bytes são conferidos para saber se é mesmo uma imagem.
O nome é gerado pelo sistema, então ninguém consegue sobrescrever arquivos.
"""
import uuid
from pathlib import Path

from flask import current_app

TAMANHO_MAX = 200 * 1024  # RNF01: até 200 KB


class FotoInvalida(Exception):
    pass


def _tipo_da_imagem(cabecalho):
    if cabecalho[:4] == b"RIFF" and cabecalho[8:12] == b"WEBP":
        return "webp"
    if cabecalho[:3] == b"\xff\xd8\xff":
        return "jpg"
    if cabecalho[:8] == b"\x89PNG\r\n\x1a\n":
        return "png"
    return None


def salvar_foto(arquivo):
    """Valida e grava a foto enviada. Devolve a URL pública (/static/...)."""
    conteudo = arquivo.read(TAMANHO_MAX + 1)
    if len(conteudo) > TAMANHO_MAX:
        raise FotoInvalida("A foto deve ter no máximo 200 KB. Dica: salve em formato WebP.")
    tipo = _tipo_da_imagem(conteudo[:12])
    if tipo is None:
        raise FotoInvalida("Envie uma imagem WebP, JPG ou PNG.")

    pasta = Path(current_app.config["UPLOAD_FOLDER"])
    pasta.mkdir(parents=True, exist_ok=True)
    nome = f"{uuid.uuid4().hex}.{tipo}"
    (pasta / nome).write_bytes(conteudo)
    return f"{current_app.config['UPLOAD_URL'].rstrip('/')}/{nome}"
