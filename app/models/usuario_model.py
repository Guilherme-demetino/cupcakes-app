"""Model de Usuário: cadastro (US01) e autenticação (US02).

Segurança das senhas (RN09): a senha NUNCA é gravada em texto puro.
O hash bcrypt é gerado pelo próprio PostgreSQL (extensão pgcrypto):
    crypt('senha', gen_salt('bf', 10))  -> '$2a$10$...'
e a conferência é feita comparando senha_hash = crypt('senha digitada', senha_hash).
"""
import re

import psycopg

from ..db import consultar_um, get_db
from ..messages import msg

SENHA_MIN = 8
_EMAIL_VALIDO = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class EmailJaCadastrado(Exception):
    """Tentativa de cadastrar um e-mail que já existe (RN08)."""


def normalizar_email(email):
    return (email or "").strip().lower()


def apenas_digitos(texto):
    return re.sub(r"\D", "", texto or "")


def formatar_telefone(telefone):
    """'11999998888' -> '(11) 99999-8888'"""
    d = apenas_digitos(telefone)
    if len(d) == 11:
        return f"({d[:2]}) {d[2:7]}-{d[7:]}"
    if len(d) == 10:
        return f"({d[:2]}) {d[2:6]}-{d[6:]}"
    return telefone


def validar_cadastro(nome, email, telefone, senha):
    """Valida os campos do formulário de cadastro.
    Devolve um dicionário {campo: mensagem}; vazio quando está tudo certo."""
    erros = {}
    nome = (nome or "").strip()
    if not nome:
        erros["nome"] = msg("MSG01")
    elif len(nome) < 2 or len(nome) > 100:
        erros["nome"] = "Digite seu nome completo (de 2 a 100 letras)."

    email = normalizar_email(email)
    if not email:
        erros["email"] = msg("MSG01")
    elif len(email) > 150 or not _EMAIL_VALIDO.match(email):
        erros["email"] = msg("MSG02")

    if not (telefone or "").strip():
        erros["telefone"] = msg("MSG01")
    elif len(apenas_digitos(telefone)) not in (10, 11):
        erros["telefone"] = msg("MSG23")

    if not senha:
        erros["senha"] = msg("MSG01")
    elif len(senha) < SENHA_MIN:
        erros["senha"] = msg("MSG04")
    elif len(senha) > 72:  # limite do algoritmo bcrypt
        erros["senha"] = "A senha pode ter no máximo 72 caracteres."
    return erros


def email_existe(email):
    return consultar_um("SELECT 1 AS existe FROM usuario WHERE email = %s", (normalizar_email(email),)) is not None


def criar(nome, email, telefone, senha):
    """Cria um CLIENTE e devolve o usuário criado (sem o hash da senha).
    Lança EmailJaCadastrado se o e-mail já existir."""
    try:
        return get_db().execute(
            """INSERT INTO usuario (nome, email, telefone, senha_hash, perfil)
               VALUES (%s, %s, %s, crypt(%s, gen_salt('bf', 10)), 'CLIENTE')
               RETURNING id, nome, email, telefone, perfil""",
            (nome.strip(), normalizar_email(email), formatar_telefone(telefone), senha),
        ).fetchone()
    except psycopg.IntegrityError as erro:
        get_db().rollback()
        raise EmailJaCadastrado(normalizar_email(email)) from erro


def autenticar(email, senha):
    """Devolve o usuário se e-mail e senha conferem; caso contrário, None."""
    if not email or not senha:
        return None
    return consultar_um(
        """SELECT id, nome, email, telefone, perfil
           FROM usuario
           WHERE email = %s AND senha_hash = crypt(%s, senha_hash)""",
        (normalizar_email(email), senha),
    )


def buscar_por_id(usuario_id):
    return consultar_um(
        "SELECT id, nome, email, telefone, perfil, criado_em FROM usuario WHERE id = %s", (usuario_id,))
