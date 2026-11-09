# 🧁 CupcakeApp

Loja online responsiva (mobile-first) de cupcakes gourmet. Tem catálogo com detalhes completos e alergênicos, carrinho, pedidos com acompanhamento de status e área administrativa.

Projeto Integrador Transdisciplinar em Engenharia de Software II
**Aluno:** Guilherme França Demetino – RGM 33160236

## Documentação

| Etapa | Conteúdo | Status |
|---|---|---|
| [Etapa 1 – Planejamento](docs/etapa1-planejamento/) | Escopo, histórias de usuário, UML, IHC, protótipo, banco de dados e dicionário | ✅ Concluída |
| [Etapa 2 – Desenvolvimento](docs/etapa2-desenvolvimento/) | Front-end, back-end MVC, testes e manual de uso | 🚧 Sprint 1 concluída (catálogo, detalhes e carrinho) |
| Etapa 3 – Validação | Testes de verificação e validação, avaliação de 5 usuários, correções e vídeo | ⏳ A fazer |

## Tecnologias

- **Front-end:** HTML, CSS e JavaScript
- **Back-end:** Python + Flask, no padrão MVC
- **Banco de dados:** PostgreSQL 14+ (driver psycopg 3)
- **Testes:** Pytest

## Como rodar

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows  (Linux/macOS: source .venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env            # e ajuste a senha do PostgreSQL (Linux/macOS: cp)
flask --app run init-db           # cria as tabelas e os dados de exemplo
flask --app run run --debug       # http://127.0.0.1:5000
pytest                            # roda os testes
```

O passo a passo completo está em [docs/etapa2-desenvolvimento](docs/etapa2-desenvolvimento/README.md#como-rodar-no-seu-computador).

## Estrutura do repositório

```
cupcakes-app/
├── app/                 ← aplicação (MVC)
│   ├── models/          ← regras de negócio e acesso ao banco
│   ├── controllers/     ← rotas
│   ├── templates/       ← telas (HTML)
│   └── static/          ← CSS, JS e imagens
├── tests/               ← testes automatizados
├── database/            ← schema.sql e seed.sql
├── docs/
│   ├── etapa1-planejamento/
│   ├── etapa2-desenvolvimento/
│   └── etapa3-validacao/
├── requirements.txt
└── run.py
```
