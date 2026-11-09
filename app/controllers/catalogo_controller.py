"""Controller do catálogo: lista (US03), filtro/busca (US04) e detalhes (US05)."""
from flask import Blueprint, render_template, request

from ..messages import msg
from ..models import cupcake_model

bp = Blueprint("catalogo", __name__)


@bp.get("/")
def index():
    categoria_id = request.args.get("categoria", type=int)
    termo = request.args.get("q", "").strip()[:80]

    cupcakes = cupcake_model.listar_ativos(categoria_id, termo)

    aviso = None
    if not cupcakes:
        aviso = msg("MSG11", termo=termo) if (termo or categoria_id) else msg("MSG10")

    return render_template("catalogo.html", cupcakes=cupcakes,
                           categorias=cupcake_model.listar_categorias(),
                           categoria_id=categoria_id, termo=termo, aviso=aviso)


@bp.get("/cupcakes/<int:cupcake_id>")
def detalhe(cupcake_id):
    cupcake = cupcake_model.buscar_ativo_por_id(cupcake_id)
    if cupcake is None:
        return render_template("erro.html", titulo="Cupcake indisponível", mensagem=msg("MSG12")), 404
    return render_template("detalhe.html", cupcake=cupcake)
