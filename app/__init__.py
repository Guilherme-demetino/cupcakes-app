"""Fábrica da aplicação Flask (padrão "application factory").

Aqui juntamos as três camadas do MVC:
- Models       -> app/models/       (regras de negócio e acesso ao banco)
- Views        -> app/templates/    (HTML que o usuário vê)
- Controllers  -> app/controllers/  (recebem a requisição, chamam o model e escolhem a view)
"""
import logging
import os
from decimal import Decimal

from dotenv import load_dotenv
from flask import Flask, render_template, session

from . import db
from .auth import usuario_logado
from .messages import msg


def create_app(config=None):
    load_dotenv()
    app = Flask(__name__)
    app.config.update(
        DATABASE_URL=os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/cupcakeapp"),
        SECRET_KEY=os.getenv("SECRET_KEY", "dev-troque-esta-chave"),
        # "Lax" impede que outro site envie formulários (POST) usando a sessão do cliente.
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_HTTPONLY=True,
        # Fotos enviadas pelo administrador (Sprint 4)
        UPLOAD_FOLDER=os.path.join(os.path.dirname(__file__), "static", "img", "cupcakes"),
        UPLOAD_URL="/static/img/cupcakes",
        MAX_CONTENT_LENGTH=2 * 1024 * 1024,  # recusa envios acima de 2 MB antes de ler
    )
    if config:
        app.config.update(config)

    db.init_app(app)

    # ---- Controllers (rotas) ----
    from .controllers.catalogo_controller import bp as catalogo_bp
    from .controllers.carrinho_controller import bp as carrinho_bp
    from .controllers.auth_controller import bp as auth_bp
    from .controllers.pedido_controller import bp as pedido_bp
    from .controllers.admin_controller import bp as admin_bp
    app.register_blueprint(catalogo_bp)
    app.register_blueprint(carrinho_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(pedido_bp)
    app.register_blueprint(admin_bp)

    # ---- Filtros e variáveis disponíveis em todos os templates ----
    @app.template_filter("brl")
    def formatar_reais(valor):
        """12.9 -> 'R$ 12,90'"""
        valor = Decimal(str(valor or 0)).quantize(Decimal("0.01"))
        inteiro, centavos = f"{valor:.2f}".split(".")
        inteiro = f"{int(inteiro):,}".replace(",", ".")
        return f"R$ {inteiro},{centavos}"

    @app.template_filter("data_hora")
    def formatar_data_hora(valor):
        """datetime -> '09/11/2026 às 14:35'"""
        return valor.strftime("%d/%m/%Y às %H:%M") if valor else ""

    @app.context_processor
    def dados_globais():
        carrinho = session.get("carrinho", {})
        return {"qtd_carrinho": sum(carrinho.values()), "usuario": usuario_logado()}

    @app.get("/favicon.ico")
    def favicon():
        return app.send_static_file("img/favicon.svg")

    # ---- Tratamento de erros (RNF08) ----
    @app.errorhandler(404)
    def nao_encontrado(_erro):
        return render_template("erro.html", titulo="Página não encontrada",
                               mensagem="Não encontramos o que você procurou. Que tal voltar ao cardápio?"), 404

    @app.errorhandler(413)
    def arquivo_grande(_erro):
        return render_template("erro.html", titulo="Arquivo muito grande",
                               mensagem="A foto deve ter no máximo 200 KB. Dica: salve em formato WebP."), 413

    @app.errorhandler(500)
    def erro_interno(erro):
        logging.getLogger(__name__).exception("Erro inesperado: %s", erro)
        return render_template("erro.html", titulo="Ops!", mensagem=msg("MSG99")), 500

    return app
