"""Controller do carrinho (US06).

Padrão usado: POST -> altera o carrinho -> redireciona (PRG, Post/Redirect/Get).
Assim, atualizar a página não repete a ação.
"""
from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from ..messages import msg
from ..models import cupcake_model
from ..models.carrinho import QTD_MAX, Carrinho

bp = Blueprint("carrinho", __name__, url_prefix="/carrinho")


def _carregar():
    return Carrinho(session.get("carrinho"))


def _salvar(carrinho):
    session["carrinho"] = carrinho.para_sessao()


def _quantidade_do_form(padrao=1):
    """Lê a quantidade enviada; valores inválidos viram o padrão."""
    return request.form.get("quantidade", default=padrao, type=int)


@bp.get("")
def ver():
    carrinho = _carregar()
    cupcakes = cupcake_model.buscar_ativos_por_ids(carrinho.itens.keys())
    resumo = carrinho.resumo(cupcakes)

    for cupcake_id in resumo["removidos"]:  # RN04 / MSG15
        flash(msg("MSG15", nome=cupcake_model.buscar_nome(cupcake_id)), "aviso")
    _salvar(carrinho)

    return render_template("carrinho.html", resumo=resumo, qtd_max=QTD_MAX, msg_vazio=msg("MSG14"),
                           # pop: o botão "Desfazer" aparece só logo após a remoção
                           desfazer=session.pop("ultimo_removido", None))


@bp.post("/adicionar")
def adicionar():
    cupcake_id = request.form.get("cupcake_id", type=int)
    cupcake = cupcake_model.buscar_ativo_por_id(cupcake_id) if cupcake_id else None
    if cupcake is None:  # RN04: inativo ou inexistente não entra no carrinho
        flash(msg("MSG12"), "erro")
        return redirect(url_for("catalogo.index"))

    quantidade = max(1, _quantidade_do_form())
    carrinho = _carregar()
    limitado = carrinho.adicionar(cupcake_id, quantidade)
    _salvar(carrinho)

    if limitado:
        flash(msg("MSG13"), "aviso")
    else:
        flash(msg("MSG20", qtd=quantidade, nome=cupcake["nome"]), "sucesso")
    return redirect(url_for("catalogo.detalhe", cupcake_id=cupcake_id))


@bp.post("/alterar")
def alterar():
    carrinho = _carregar()
    cupcake_id = request.form.get("cupcake_id", type=int)
    if carrinho.alterar(cupcake_id, _quantidade_do_form()):
        flash(msg("MSG13"), "aviso")
    _salvar(carrinho)
    return redirect(url_for("carrinho.ver"))


@bp.post("/remover")
def remover():
    carrinho = _carregar()
    cupcake_id = request.form.get("cupcake_id", type=int)
    quantidade = carrinho.remover(cupcake_id)
    _salvar(carrinho)
    if quantidade:
        # Guarda o item removido para o botão "Desfazer" (princípio da reversibilidade).
        session["ultimo_removido"] = {"cupcake_id": cupcake_id, "quantidade": quantidade}
        flash(msg("MSG19", nome=cupcake_model.buscar_nome(cupcake_id)), "aviso")
    return redirect(url_for("carrinho.ver"))


@bp.post("/desfazer")
def desfazer():
    cupcake_id = request.form.get("cupcake_id", type=int)
    quantidade = _quantidade_do_form()
    if cupcake_id and quantidade > 0 and cupcake_model.buscar_ativos_por_ids([cupcake_id]):
        carrinho = _carregar()
        carrinho.adicionar(cupcake_id, quantidade)
        _salvar(carrinho)
        flash("Item devolvido ao carrinho.", "sucesso")
    return redirect(url_for("carrinho.ver"))
