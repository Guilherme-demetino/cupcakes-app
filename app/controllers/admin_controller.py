"""Controller da área administrativa: manter cupcakes (US10) e gerenciar pedidos (US11).
Todas as rotas exigem o perfil ADMIN (RNF06): clientes recebem MSG17."""
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from ..auth import admin_obrigatorio
from ..messages import msg
from ..models import cupcake_model, pedido_model
from ..uploads import FotoInvalida, salvar_foto

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.get("")
@admin_obrigatorio
def inicio():
    return redirect(url_for("admin.pedidos"))


# ---------------------------------------------------------------- US10 – Cupcakes

@bp.get("/cupcakes")
@admin_obrigatorio
def cupcakes():
    return render_template("admin/cupcakes.html", cupcakes=cupcake_model.listar_todos())


def _dados_do_formulario():
    return {
        "nome": request.form.get("nome", "").strip(),
        "descricao": request.form.get("descricao", "").strip(),
        "preco": request.form.get("preco", "").strip(),
        "tamanho": request.form.get("tamanho", ""),
        "peso_gramas": request.form.get("peso_gramas", "").strip(),
        "categoria_id": request.form.get("categoria_id", type=int),
        "ingrediente_ids": request.form.getlist("ingredientes", type=int),
    }


def _formulario(cupcake_id=None):
    """Mesma lógica para criar e editar."""
    existente = None
    if cupcake_id is not None:
        existente = cupcake_model.buscar_para_edicao(cupcake_id) or abort(404)

    categorias = cupcake_model.listar_categorias()
    ingredientes = cupcake_model.listar_ingredientes()
    dados, erros, status = existente or {"tamanho": "TRADICIONAL", "ingrediente_ids": []}, {}, 200

    if request.method == "POST":
        dados = _dados_do_formulario()
        arquivo = request.files.get("foto")
        enviou_foto = bool(arquivo and arquivo.filename)
        tem_foto = enviou_foto or bool(existente and existente["foto_url"])
        erros = cupcake_model.validar_cupcake(dados, tem_foto, [c["id"] for c in categorias],
                                              [i["id"] for i in ingredientes])
        foto_url = None
        if not erros and enviou_foto:
            try:
                foto_url = salvar_foto(arquivo)
            except FotoInvalida as erro:
                erros["foto"] = str(erro)
        if not erros:
            try:
                novo_id = cupcake_model.salvar(dados, foto_url, cupcake_id)
            except cupcake_model.NomeRepetido:
                erros["nome"] = "Já existe um cupcake com esse nome."
            else:
                flash(msg("MSG22"), "sucesso")
                return redirect(url_for("admin.cupcakes", _anchor=f"cupcake-{novo_id}"))
        status = 422
        if existente:
            dados["foto_url"] = existente["foto_url"]

    return render_template("admin/cupcake_form.html", dados=dados, erros=erros, existente=existente,
                           categorias=categorias, ingredientes=ingredientes,
                           tamanhos=cupcake_model.TAMANHOS), status


@bp.route("/cupcakes/novo", methods=["GET", "POST"])
@admin_obrigatorio
def novo_cupcake():
    return _formulario()


@bp.route("/cupcakes/<int:cupcake_id>/editar", methods=["GET", "POST"])
@admin_obrigatorio
def editar_cupcake(cupcake_id):
    return _formulario(cupcake_id)


@bp.post("/cupcakes/<int:cupcake_id>/ativo")
@admin_obrigatorio
def alternar_ativo(cupcake_id):
    resultado = cupcake_model.alternar_ativo(cupcake_id) or abort(404)
    estado = "voltou ao cardápio" if resultado["ativo"] else "saiu do cardápio"
    flash(f"{resultado['nome']} {estado}.", "sucesso")
    return redirect(url_for("admin.cupcakes", _anchor=f"cupcake-{cupcake_id}"))


# ---------------------------------------------------------------- US11 – Pedidos

@bp.get("/pedidos")
@admin_obrigatorio
def pedidos():
    status = request.args.get("status")
    if status not in pedido_model.STATUS:
        status = None
    return render_template("admin/pedidos.html", pedidos=pedido_model.listar_todos(status),
                           filtro=status, contagem=pedido_model.contar_por_status(),
                           nomes_status=pedido_model.STATUS, avanco=pedido_model.AVANCO,
                           acoes=pedido_model.ACOES)


@bp.get("/pedidos/<int:pedido_id>")
@admin_obrigatorio
def pedido(pedido_id):
    return render_template("admin/pedido.html", pedido=pedido_model.buscar_admin(pedido_id) or abort(404),
                           nomes_status=pedido_model.STATUS, acoes=pedido_model.ACOES,
                           formas=pedido_model.FORMAS_PAGAMENTO, etapas=pedido_model.ETAPAS)


@bp.post("/pedidos/<int:pedido_id>/status")
@admin_obrigatorio
def mudar_status(pedido_id):
    atual, novo = request.form.get("atual", ""), request.form.get("novo", "")
    if pedido_model.buscar_admin(pedido_id) is None:
        abort(404)
    try:
        pedido_model.mudar_status_admin(pedido_id, atual, novo)
        flash(f"Pedido nº {pedido_id}: {pedido_model.STATUS[novo]}.", "sucesso")
    except pedido_model.TransicaoInvalida as erro:
        real = pedido_model.STATUS.get(erro.atual, erro.atual)
        if erro.atual != atual:  # outra pessoa mudou o pedido enquanto esta tela estava aberta
            flash(f"Este pedido foi atualizado por outra pessoa e agora está \"{real}\". Confira antes de continuar.",
                  "aviso")
        else:  # MSG16
            flash(msg("MSG16", atual=real, novo=pedido_model.STATUS.get(erro.novo, erro.novo)), "erro")
    destino = request.form.get("voltar")
    if destino == "lista":
        return redirect(url_for("admin.pedidos", status=request.form.get("filtro") or None))
    return redirect(url_for("admin.pedido", pedido_id=pedido_id))
