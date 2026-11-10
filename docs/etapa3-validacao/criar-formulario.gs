/**
 * CupcakeApp – cria automaticamente o formulário de avaliação no Google Forms.
 *
 * COMO USAR:
 *  1. Acesse https://script.google.com e clique em "Novo projeto".
 *  2. Apague o conteúdo do editor e cole TODO este arquivo.
 *  3. Troque o LINK_DO_SISTEMA abaixo pelo endereço do site publicado.
 *  4. Clique em "Executar" (▶). Na primeira vez, o Google pede autorização:
 *     "Revisar permissões" → escolha sua conta → "Avançado" → "Acessar projeto (não seguro)" → "Permitir".
 *     (O aviso aparece porque o script é seu e não foi publicado; ele só cria o formulário na sua conta.)
 *  5. Ao terminar, abra "Registro de execução": aparecem o link para RESPONDER (mande aos colegas)
 *     e o link para EDITAR (só para você).
 */

const LINK_DO_SISTEMA = 'https://cupcakeapp-3x9a.onrender.com'; // link do site publicado

function criarFormulario() {
  const form = FormApp.create('CupcakeApp – Avaliação do sistema');
  form
    .setDescription(
      'Obrigado por testar! Este formulário faz parte do Projeto Integrador de Engenharia de Software II ' +
      '(Guilherme França Demetino). Suas respostas e seu nome aparecerão no relatório entregue ao professor.\n\n' +
      '🧁 Sistema: ' + LINK_DO_SISTEMA + '\n' +
      'Conta de administrador para testar a parte da loja: admin@cupcakeapp.com.br / Admin@2026\n' +
      '⚠️ Use dados inventados. Não use a senha de verdade de nenhuma conta sua.'
    )
    .setCollectEmail(false)
    .setProgressBar(true)
    .setConfirmationMessage('Muito obrigado pela avaliação! 🧁 Suas observações vão ajudar a melhorar o sistema.');

  // ---------------- Seção 1 – Sobre você e o teste ----------------
  form.addSectionHeaderItem().setTitle('1. Sobre você e o teste');
  form.addTextItem().setTitle('Nome completo').setRequired(true);
  form.addDateItem().setTitle('Data do teste').setRequired(true);
  form.addMultipleChoiceItem()
    .setTitle('Você é…')
    .setChoiceValues(['Colega de curso', 'Profissional da área de TI', 'Outro'])
    .setRequired(true);
  form.addCheckboxItem()
    .setTitle('Em qual aparelho você testou?')
    .setChoiceValues(['Celular', 'Computador', 'Tablet'])
    .setRequired(true);
  form.addCheckboxItem()
    .setTitle('Qual navegador?')
    .setChoiceValues(['Chrome', 'Edge', 'Firefox', 'Safari', 'Outro'])
    .setRequired(true);

  // ---------------- Seção 2 – Funcionalidades ----------------
  form.addPageBreakItem().setTitle('2. Funcionalidades testadas');
  form.addGridItem()
    .setTitle('Para cada funcionalidade, marque o resultado')
    .setHelpText('Marque uma opção em cada linha.')
    .setRows([
      'Ver cardápio, buscar e filtrar',
      'Ver detalhes e alergênicos',
      'Carrinho (adicionar, alterar, remover)',
      'Criar conta',
      'Entrar e sair da conta',
      'Finalizar pedido',
      'Acompanhar pedido',
      'Cancelar pedido',
      '(Admin) Gerenciar pedidos',
      '(Admin) Cadastrar e editar cupcakes',
    ])
    .setColumns(['✅ Testei e funcionou', '❌ Testei e NÃO funcionou', '➖ Não testei'])
    .setRequired(true);

  // ---------------- Seção 3 – Detalhes (itens obrigatórios do laudo) ----------------
  form.addPageBreakItem().setTitle('3. Detalhes');
  form.addParagraphTextItem()
    .setTitle('O que você testou e funcionou?')
    .setHelpText('Descreva com suas palavras.')
    .setRequired(true);
  form.addParagraphTextItem()
    .setTitle('O que você testou e NÃO funcionou?')
    .setHelpText('Descreva o que fez, o que aconteceu e o que deveria ter acontecido. Se tudo funcionou, escreva "nada".')
    .setRequired(true);
  form.addParagraphTextItem()
    .setTitle('Na sua opinião, o que deve ser corrigido no que não funcionou?');
  form.addParagraphTextItem()
    .setTitle('Alguma funcionalidade ficou sem testar? Qual, e por quê?')
    .setHelpText('Ex.: "não testei a área do admin porque não tive tempo". Se testou tudo, escreva "testei tudo".')
    .setRequired(true);
  form.addParagraphTextItem()
    .setTitle('Prints das telas com erro (opcional)')
    .setHelpText('Cole aqui um link (Google Drive, Imgur…) ou envie os prints diretamente para o Guilherme pelo WhatsApp.');

  // ---------------- Seção 4 – Opinião geral ----------------
  form.addPageBreakItem().setTitle('4. Opinião geral');
  form.addScaleItem().setTitle('Facilidade de uso').setBounds(1, 5)
    .setLabels('Muito difícil', 'Muito fácil').setRequired(true);
  form.addScaleItem().setTitle('Aparência (visual)').setBounds(1, 5)
    .setLabels('Muito ruim', 'Muito boa').setRequired(true);
  form.addMultipleChoiceItem()
    .setTitle('Você compraria cupcakes por um app assim?')
    .setChoiceValues(['Sim', 'Talvez', 'Não'])
    .setRequired(true);
  form.addParagraphTextItem().setTitle('Sugestões de melhoria');
  form.addCheckboxItem()
    .setTitle('Autorização')
    .setChoiceValues(['Autorizo que meu nome e minhas respostas apareçam no relatório do projeto'])
    .setRequired(true);

  Logger.log('✅ Formulário criado!');
  Logger.log('🔗 Link para os COLEGAS responderem: ' + form.getPublishedUrl());
  Logger.log('✏️ Link para VOCÊ editar: ' + form.getEditUrl());
}
