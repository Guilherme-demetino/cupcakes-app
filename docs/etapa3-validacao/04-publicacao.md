# 4. Publicação do sistema (Render)

Para os avaliadores acessarem de casa, o CupcakeApp é publicado no **Render** (render.com), no plano gratuito. O arquivo [`render.yaml`](../../render.yaml), na raiz do repositório, descreve tudo o que o Render precisa criar:

| Recurso | Plano | O que faz |
|---|---|---|
| Serviço web `cupcakeapp` | free | Instala as dependências, cria as tabelas e os dados de exemplo **só na primeira vez** (`init-db --se-vazio`) e inicia o servidor (Gunicorn) |
| Banco `cupcakeapp-db` | free | PostgreSQL gerenciado pelo Render |

A chave secreta (`SECRET_KEY`) é **gerada pelo Render** e não fica no código. A senha do banco também é passada pelo Render (`DATABASE_URL`). Em HTTPS, o cookie da sessão só trafega criptografado (`SESSION_COOKIE_SECURE`).

## Passo a passo

1. Acesse **render.com** e clique em **Get Started**. Entre com a sua conta do **GitHub**. Não é preciso cartão de crédito para o plano gratuito.
2. No painel, clique em **New → Blueprint**.
3. Conecte o GitHub, se o Render pedir, e escolha o repositório **cupcakes-app**.
4. O Render lê o `render.yaml` e mostra o que vai criar: `cupcakeapp` (web) e `cupcakeapp-db` (banco). Dê um nome ao Blueprint, por exemplo `cupcakeapp`, e clique em **Apply** (ou **Deploy Blueprint**).
5. Espere de 5 a 10 minutos. Abra o serviço **cupcakeapp** e acompanhe a aba **Logs**. Deu certo quando aparecer `Banco criado e populado com os dados de exemplo.` e depois `Booting worker`.
6. O endereço aparece no topo da página do serviço, no formato **https://cupcakeapp-xxxx.onrender.com**. Abra e teste.

## Limitações do plano gratuito

| Limitação | Efeito | O que fazer |
|---|---|---|
| O servidor **"dorme"** depois de um tempo sem acessos | O primeiro acesso depois disso demora cerca de 1 minuto | Avise os avaliadores: "se demorar, espere 1 minuto e recarregue" |
| O banco gratuito tem **prazo de validade** (confira no painel do Render) | Depois do prazo, os dados são apagados | Faça a avaliação dentro do prazo. Para publicar de novo, basta repetir o Blueprint |
| O disco do servidor é **temporário** | As **fotos enviadas pelo admin** somem quando o servidor reinicia ou é atualizado. As fotos originais dos 6 cupcakes ficam, porque estão no repositório | Aceitável para a avaliação. Uma melhoria futura seria guardar as fotos num serviço de arquivos, como S3 ou Cloudinary |

## Atualizações

A cada `git push` na branch `main`, o Render publica a nova versão sozinho. Os dados do banco são **mantidos**, porque o `init-db --se-vazio` não apaga nada. É assim que as correções feitas depois da avaliação chegam ao site.
