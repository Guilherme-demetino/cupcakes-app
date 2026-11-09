"""Ponto de entrada da aplicação.

Para rodar em desenvolvimento:
    flask --app run init-db      (cria as tabelas e os dados de exemplo – só na 1ª vez)
    flask --app run run --debug  (abre em http://127.0.0.1:5000)
"""
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
