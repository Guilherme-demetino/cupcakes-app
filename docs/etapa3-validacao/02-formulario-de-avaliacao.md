# 2. Formulário de Avaliação (teste de aceitação com 5 usuários)

O enunciado pede que a solução seja oferecida a **5 colegas de curso ou profissionais da área**. Eles testam e preenchem um formulário com os bugs encontrados, sugestões de melhoria e prints das telas com erro. O laudo precisa ter **no mínimo**:

- nome de quem testou;
- data do teste;
- o que testou e funcionou;
- o que testou e não funcionou, e o que deve ser corrigido;
- funcionalidade não testada, e por que faltou.

Este documento traz:
- (A) a mensagem-convite com o roteiro para o avaliador;
- (B) as perguntas prontas para montar no **Google Forms**;
- (C) o modelo do laudo que vai para o PDF final.

---

## A. Convite e roteiro para o avaliador

Envie esta mensagem junto com o link do sistema e o link do formulário:

> Oi! Estou fazendo o Projeto Integrador de Engenharia de Software e preciso que você teste meu sistema por uns **15 minutos** e me diga o que achou, **principalmente o que deu errado**. Pode ser bem sincero: apontar erros é justamente o que me ajuda.
>
> 🧁 **Sistema:** https://cupcakeapp-3x9a.onrender.com\
> *(se demorar para abrir, espere 1 minuto e recarregue: o servidor gratuito "acorda" no primeiro acesso)*
> 📝 **Formulário:** https://docs.google.com/forms/d/e/1FAIpQLScOTQfO6TlaKDLFHjVRCZ_HfHMhufYc7NYs9i8tSZ-nfGto5w/viewform
>
> **O que tentar fazer (como cliente):**
> 1. Navegue pelo cardápio, use a busca e os filtros de categoria.
> 2. Abra um cupcake e veja os ingredientes e alergênicos.
> 3. Coloque alguns cupcakes no carrinho, mude as quantidades e remova um.
> 4. Crie uma conta (pode usar um e-mail inventado, como seunome@teste.com).
> 5. Finalize um pedido. Não é cobrado nada, o pagamento seria "na entrega".
> 6. Acompanhe o pedido em "Pedidos" e, se quiser, cancele.
>
> **Se quiser testar a parte da loja (administrador):** entre com `admin@cupcakeapp.com.br` e a senha `Admin@2026`. Faça seu pedido andar até "Entregue" e cadastre um cupcake novo com uma foto.
>
> Tente também **"quebrar" o sistema**: deixar campos vazios, digitar coisas estranhas, apertar botões duas vezes… Se algo der errado, **tire um print**.
>
> Obrigado! 🙏

> ⚠️ Os dados do sistema publicado são **só de teste**. Peça aos avaliadores que **não usem a senha de verdade** de nenhuma conta deles.

---

## B. Perguntas para o Google Forms

> ✅ **Formulário criado em 09/11/2026** com o script `criar-formulario.gs`: https://docs.google.com/forms/d/e/1FAIpQLScOTQfO6TlaKDLFHjVRCZ_HfHMhufYc7NYs9i8tSZ-nfGto5w/viewform

> ⚡ **Jeito rápido:** o script [`criar-formulario.gs`](criar-formulario.gs) cria o formulário inteiro sozinho na sua conta Google. As instruções estão no começo do arquivo: cole em script.google.com e clique em Executar. A única diferença é a pergunta 11 (prints): o Google não permite criar campo de **upload** por script, então ela vira um campo de texto para colar um link. Quem quiser upload pode trocar o campo depois, no editor do formulário.

**Como criar à mão:** acesse **forms.google.com**, clique em **+ Formulário em branco** e monte as seções abaixo. A coluna "Tipo" diz qual opção escolher no menu de cada pergunta. Em **Configurações**, deixe ativado "Coletar endereços de e-mail" como *Não coletar*, para o avaliador não precisar se identificar por e-mail.

**Título:** CupcakeApp – Avaliação do sistema
**Descrição:** Obrigado por testar! Este formulário faz parte do Projeto Integrador de Engenharia de Software. Suas respostas e seu nome aparecerão no relatório entregue ao professor.

### Seção 1 – Sobre você e o teste

| # | Pergunta | Tipo | Obrigatória | Opções |
|---|---|---|---|---|
| 1 | Nome completo | Resposta curta | ✅ | – |
| 2 | Data do teste | Data | ✅ | – |
| 3 | Você é… | Múltipla escolha | ✅ | Colega de curso • Profissional da área de TI • Outro |
| 4 | Em qual aparelho você testou? | Caixas de seleção | ✅ | Celular • Computador • Tablet |
| 5 | Qual navegador? | Caixas de seleção | ✅ | Chrome • Edge • Firefox • Safari • Outro |

### Seção 2 – Funcionalidades testadas

| # | Pergunta | Tipo | Obrigatória |
|---|---|---|---|
| 6 | Para cada funcionalidade, marque o resultado | **Grade de múltipla escolha** | ✅ (exigir resposta em cada linha) |

- **Linhas da grade:**
  1. Ver cardápio, buscar e filtrar;
  2. Ver detalhes e alergênicos;
  3. Carrinho (adicionar, alterar, remover);
  4. Criar conta;
  5. Entrar e sair da conta;
  6. Finalizar pedido;
  7. Acompanhar pedido;
  8. Cancelar pedido;
  9. *(Admin)* Gerenciar pedidos;
  10. *(Admin)* Cadastrar e editar cupcakes.
- **Colunas:** ✅ Testei e funcionou • ❌ Testei e NÃO funcionou • ➖ Não testei

### Seção 3 – Detalhes (os itens obrigatórios do laudo)

| # | Pergunta | Tipo | Obrigatória |
|---|---|---|---|
| 7 | **O que você testou e funcionou?** Descreva com suas palavras. | Parágrafo | ✅ |
| 8 | **O que você testou e NÃO funcionou?** Descreva o que fez, o que aconteceu e o que deveria ter acontecido. Se tudo funcionou, escreva "nada". | Parágrafo | ✅ |
| 9 | Na sua opinião, **o que deve ser corrigido** no que não funcionou? | Parágrafo | – |
| 10 | **Alguma funcionalidade ficou sem testar?** Qual, e por quê? (ex.: "não testei a área do admin porque não tive tempo") | Parágrafo | ✅ |
| 11 | Prints das telas com erro | Upload de arquivo (até 5 imagens) | – |

> 💡 O **upload de arquivo** do Google Forms exige que o avaliador entre com uma conta Google. Se algum colega não tiver ou não quiser, peça para mandar os prints pelo WhatsApp e anexe você mesmo no laudo.

### Seção 4 – Opinião geral

| # | Pergunta | Tipo | Obrigatória | Opções |
|---|---|---|---|---|
| 12 | Facilidade de uso | Escala linear 1–5 | ✅ | 1 = muito difícil • 5 = muito fácil |
| 13 | Aparência (visual) | Escala linear 1–5 | ✅ | 1 = muito ruim • 5 = muito boa |
| 14 | Você compraria cupcakes por um app assim? | Múltipla escolha | ✅ | Sim • Talvez • Não |
| 15 | Sugestões de melhoria | Parágrafo | – | – |
| 16 | Autorizo que meu nome e minhas respostas apareçam no relatório do projeto | Caixa de seleção | ✅ | Autorizo |

As perguntas 7, 8, 10 e 1–2 cobrem os cinco itens mínimos do enunciado. A grade (6) e as notas (12–14) permitem fazer um resumo em números.

---

## C. Modelo do laudo (uma página por avaliador no PDF final)

Depois de receber as 5 respostas, cada uma vira uma página do PDF entregue ao professor. Em **Respostas → ⋮ → Fazer o download das respostas (.csv)** dá para exportar todas. Com esse arquivo, eu monto o PDF.

```
LAUDO DE TESTE Nº __ – CupcakeApp

Avaliador(a): ______________________   Perfil: ( ) Colega de curso ( ) Profissional de TI ( ) Outro
Data do teste: ___/___/______          Aparelho/navegador: ______________________

FUNCIONALIDADES
                                   Funcionou  Não funcionou  Não testou
Cardápio, busca e filtros            ( )         ( )           ( )
Detalhes e alergênicos               ( )         ( )           ( )
Carrinho                             ( )         ( )           ( )
Criar conta                          ( )         ( )           ( )
Entrar / sair                        ( )         ( )           ( )
Finalizar pedido                     ( )         ( )           ( )
Acompanhar pedido                    ( )         ( )           ( )
Cancelar pedido                      ( )         ( )           ( )
(Admin) Gerenciar pedidos            ( )         ( )           ( )
(Admin) Cadastrar/editar cupcakes    ( )         ( )           ( )

1. O QUE TESTOU E FUNCIONOU:
2. O QUE TESTOU E NÃO FUNCIONOU (e o que deve ser corrigido):
3. FUNCIONALIDADE NÃO TESTADA (e por quê):
4. SUGESTÕES DE MELHORIA:
5. NOTAS: Facilidade __/5   Aparência __/5   Compraria? ______
6. PRINTS: (anexos)

RESPOSTA DO DESENVOLVEDOR
Ação tomada: ( ) Corrigido – ver C__ em 03-correcoes  ( ) Não corrigido – justificativa: ______
```

A última parte, **"Resposta do desenvolvedor"**, mostra ao professor que cada apontamento foi analisado. Isso atende ao item "coletar as sugestões, realizar correções e melhorias (quando pertinente) e incorporá-las na documentação".
