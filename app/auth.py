"""Controle de acesso: quem está logado e quais páginas exigem login (RNF05, RNF06)."""
from functools import wraps
from urllib.parse import urlparse

from flask import flash, g, redirect, render_template, request, session, url_for

from .messages import msg


def entrar(usuario):
    """Registra o login na sessão. O carrinho é mantido (critério da US07)."""
    carrinho = session.get("carrinho")
    session.clear()  # descarta qualquer dado antigo da sessão
    if carrinho:
        session["carrinho"] = carrinho
    session["usuario_id"] = usuario["id"]
    session["usuario_nome"] = usuario["nome"]
    session["usuario_perfil"] = usuario["perfil"]
    session.permanent = True


def sair():
    session.clear()


def usuario_logado():
    """Dados básicos do usuário logado, ou None."""
    if "usuario_id" not in session:
        return None
    return {"id": session["usuario_id"], "nome": session["usuario_nome"], "perfil": session["usuario_perfil"]}


def destino_seguro(destino, padrao="/"):
    """Só aceita endereços internos do próprio site (evita 'open redirect' para sites falsos)."""
    if not destino:
        return padrao
    partes = urlparse(destino)
    if partes.scheme or partes.netloc or not destino.startswith("/") or destino.startswith("//") \
            or "\\" in destino:
        return padrao
    return destino


def login_obrigatorio(view):
    """Decorator: a página só abre para usuários logados."""
    @wraps(view)
    def protegida(*args, **kwargs):
        if usuario_logado() is None:
            flash("Entre na sua conta para continuar.", "aviso")
            proxima = request.full_path.rstrip("?")
            return redirect(url_for("auth.login", next=proxima))
        g.usuario = usuario_logado()
        return view(*args, **kwargs)
    return protegida


def admin_obrigatorio(view):
    """Decorator: a página só abre para o perfil ADMIN (RNF06 / MSG17)."""
    @wraps(view)
    @login_obrigatorio
    def protegida(*args, **kwargs):
        if g.usuario["perfil"] != "ADMIN":
            return render_template("erro.html", titulo="Acesso restrito", mensagem=msg("MSG17")), 403
        return view(*args, **kwargs)
    return protegida
