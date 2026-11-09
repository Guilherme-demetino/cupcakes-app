"""Controller de autenticação: cadastro (US01), login e logout (US02) e "Minha conta"."""
from flask import Blueprint, flash, redirect, render_template, request, url_for

from .. import auth
from ..messages import msg
from ..models import usuario_model

bp = Blueprint("auth", __name__)


def _proxima_pagina():
    """Para onde voltar depois do login/cadastro (ex.: o carrinho)."""
    return auth.destino_seguro(request.values.get("next"), url_for("catalogo.index"))


@bp.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if auth.usuario_logado():
        return redirect(url_for("auth.conta"))

    dados, erros = {}, {}
    if request.method == "POST":
        dados = {campo: request.form.get(campo, "") for campo in ("nome", "email", "telefone", "senha")}
        erros = usuario_model.validar_cadastro(**dados)

        # Verifica o e-mail repetido junto com os outros erros, para o cliente corrigir tudo de uma vez.
        if "email" not in erros and usuario_model.email_existe(dados["email"]):
            erros["email"] = msg("MSG03")

        if not erros:
            try:
                usuario = usuario_model.criar(**dados)
            except usuario_model.EmailJaCadastrado:  # dois cadastros ao mesmo tempo
                erros["email"] = msg("MSG03")
            else:
                auth.entrar(usuario)
                flash(f"Conta criada! Boas-vindas, {usuario['nome'].split()[0]}.", "sucesso")
                return redirect(_proxima_pagina())

    dados.pop("senha", None)  # a senha nunca volta para a tela
    status = 422 if erros else 200
    return render_template("cadastro.html", dados=dados, erros=erros,
                           proxima=request.values.get("next", "")), status


@bp.route("/login", methods=["GET", "POST"])
def login():
    if auth.usuario_logado():
        return redirect(_proxima_pagina())

    email, erro = "", None
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        usuario = usuario_model.autenticar(email, request.form.get("senha", ""))
        if usuario:
            auth.entrar(usuario)
            flash(f"Olá, {usuario['nome'].split()[0]}!", "sucesso")
            return redirect(_proxima_pagina())
        # Mesma mensagem para e-mail inexistente ou senha errada:
        # não revelamos quais e-mails têm cadastro (critério da US02).
        erro = msg("MSG05")

    return render_template("login.html", email=email, erro=erro,
                           proxima=request.values.get("next", "")), (401 if erro else 200)


@bp.post("/logout")
def logout():
    auth.sair()
    flash("Você saiu da sua conta.", "sucesso")
    return redirect(url_for("catalogo.index"))


@bp.get("/conta")
@auth.login_obrigatorio
def conta():
    usuario = usuario_model.buscar_por_id(auth.usuario_logado()["id"])
    if usuario is None:  # conta removida enquanto a sessão estava aberta
        auth.sair()
        return redirect(url_for("auth.login"))
    return render_template("conta.html", usuario=usuario)
