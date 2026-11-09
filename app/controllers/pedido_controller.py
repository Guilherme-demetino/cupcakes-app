"""Controller de pedidos: checkout (US07), meus pedidos (US08) e cancelamento (US09).
Todas as rotas exigem login (RN10)."""
from flask import Blueprint, abort, flash, g, redirect, render_template, request, session, url_for

from ..auth import login_obrigatorio
from ..messages import msg
from ..models import cupcake_model, pedido_model
from ..models.carrinho import Carrinho

bp = Blueprint("pedido", __name__)


def _resumo_do_carrinho():
    """Recalcula o carrinho com os preços atuais e avisa sobre itens que saíram do cardápio."""
    carrinho = Carrinho(session.get("carrinho"))
    resumo = carrinho.resumo(cupcake_model.buscar_ativos_por_ids(carrinho.itens.keys()))
    for cupcake_id in resumo["removidos"]:
        flash(msg("MSG15", nome=cupcake_model.buscar_nome(cupcake_id)), "aviso")
    session["carrinho"] = carrinho.para_sessao()
    return resumo


def _tela_checkout(resumo, endereco, forma, observacao, erros, status=200):
    return render_template("checkout.html", resumo=resumo, endereco=endereco, forma=forma,
                           observacao=observacao, erros=erros, ufs=pedido_model.UFS,
                           formas=pedido_model.FORMAS_PAGAMENTO), status


@bp.get("/checkout")
@login_obrigatorio
def checkout():
    resumo = _resumo_do_carrinho()
    if not resumo["linhas"]:
        if not resumo["removidos"]:
            flash(msg("MSG14"), "aviso")
        return redirect(url_for("carrinho.ver"))
    endereco = pedido_model.ultimo_endereco(g.usuario["id"]) or {c: "" for c in pedido_model.CAMPOS_ENDERECO}
    return _tela_checkout(resumo, endereco, "PIX", "", {})


@bp.post("/checkout")
@login_obrigatorio
def confirmar():
    resumo = _resumo_do_carrinho()
    if resumo["removidos"] or not resumo["linhas"]:
        # O carrinho mudou (item desativado) ou ficou vazio: o cliente revisa antes de pagar.
        if not resumo["linhas"] and not resumo["removidos"]:
            flash(msg("MSG14"), "aviso")
        return redirect(url_for("carrinho.ver"))

    endereco = pedido_model.limpar_endereco(request.form)
    forma = request.form.get("forma_pagamento", "")
    observacao = request.form.get("observacao", "").strip()
    erros = pedido_model.validar_checkout(endereco, forma, observacao)
    if erros:
        return _tela_checkout(resumo, endereco, forma, observacao, erros, 422)

    pedido_id = pedido_model.criar(g.usuario["id"], endereco, forma, observacao, resumo)
    session.pop("carrinho", None)
    return redirect(url_for("pedido.confirmacao", pedido_id=pedido_id))


@bp.get("/pedidos/<int:pedido_id>/confirmacao")
@login_obrigatorio
def confirmacao(pedido_id):
    pedido = pedido_model.buscar_do_usuario(pedido_id, g.usuario["id"]) or abort(404)
    return render_template("confirmacao.html", pedido=pedido, mensagem=msg("MSG21", id=pedido["id"]))


@bp.get("/pedidos")
@login_obrigatorio
def lista():
    return render_template("pedidos.html", pedidos=pedido_model.listar_do_usuario(g.usuario["id"]),
                           nomes_status=pedido_model.STATUS)


@bp.get("/pedidos/<int:pedido_id>")
@login_obrigatorio
def detalhe(pedido_id):
    # Pedido de outro cliente responde 404 (e não 403) para não revelar que o número existe.
    pedido = pedido_model.buscar_do_usuario(pedido_id, g.usuario["id"]) or abort(404)
    return render_template("pedido.html", pedido=pedido, etapas=pedido_model.ETAPAS,
                           nomes_status=pedido_model.STATUS, formas=pedido_model.FORMAS_PAGAMENTO)


@bp.get("/pedidos/<int:pedido_id>/cancelar")
@login_obrigatorio
def confirmar_cancelamento(pedido_id):
    """Tela de confirmação (MSG18): cancelar não pode ser feito com um toque só."""
    pedido = pedido_model.buscar_do_usuario(pedido_id, g.usuario["id"]) or abort(404)
    if not pedido["pode_cancelar"]:
        flash("Este pedido já entrou em preparo e não pode mais ser cancelado pelo app.", "erro")
        return redirect(url_for("pedido.detalhe", pedido_id=pedido_id))
    return render_template("cancelar.html", pedido=pedido, pergunta=msg("MSG18", id=pedido_id))


@bp.post("/pedidos/<int:pedido_id>/cancelar")
@login_obrigatorio
def cancelar(pedido_id):
    try:
        pedido_model.cancelar_pelo_cliente(pedido_id, g.usuario["id"])
        flash(f"Pedido nº {pedido_id} cancelado.", "sucesso")
    except pedido_model.PedidoNaoPodeSerCancelado:
        if pedido_model.buscar_do_usuario(pedido_id, g.usuario["id"]) is None:
            abort(404)
        flash("Este pedido já entrou em preparo e não pode mais ser cancelado pelo app.", "erro")
    return redirect(url_for("pedido.detalhe", pedido_id=pedido_id))
