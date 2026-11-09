// CupcakeApp – interações do front-end.
// O site funciona sem JavaScript; o JS só deixa a experiência mais agradável.

document.addEventListener("DOMContentLoaded", () => {
  const MAX = 20, MIN = 1;
  const formatarReais = (v) => v.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });

  // Seletor de quantidade da tela de detalhes (− 1 +) e total no botão
  document.querySelectorAll("form.comprar").forEach((form) => {
    const input = form.querySelector("input[name=quantidade]");
    const total = form.querySelector("[data-total]");
    const preco = parseFloat(form.dataset.preco);

    const atualizar = () => {
      let q = parseInt(input.value, 10);
      if (isNaN(q) || q < MIN) q = MIN;
      if (q > MAX) { q = MAX; avisar("O máximo é 20 unidades por sabor. Para encomendas maiores, fale com a loja."); }
      input.value = q;
      total.textContent = formatarReais(preco * q);
    };

    form.querySelectorAll("[data-delta]").forEach((botao) =>
      botao.addEventListener("click", () => {
        input.value = (parseInt(input.value, 10) || MIN) + parseInt(botao.dataset.delta, 10);
        atualizar();
      })
    );
    input.addEventListener("change", atualizar);

    // Evita clique duplo enviando o pedido duas vezes
    form.addEventListener("submit", () => {
      const botao = form.querySelector("button[type=submit]");
      botao.disabled = true;
      botao.textContent = "Adicionando…";
    });
  });

  // Mostrar / ocultar senha (Sprint 2)
  document.querySelectorAll("[data-mostrar-senha]").forEach((botao) => {
    const campo = document.getElementById(botao.dataset.mostrarSenha);
    botao.addEventListener("click", () => {
      const mostrar = campo.type === "password";
      campo.type = mostrar ? "text" : "password";
      botao.setAttribute("aria-label", mostrar ? "Ocultar senha" : "Mostrar senha");
      botao.textContent = mostrar ? "🙈" : "👁";
    });
  });

  // Máscara de telefone: 11999998888 -> (11) 99999-8888
  document.querySelectorAll("[data-mascara-telefone]").forEach((campo) => {
    campo.addEventListener("input", () => {
      const d = campo.value.replace(/\D/g, "").slice(0, 11);
      let v = d;
      if (d.length > 2) v = `(${d.slice(0, 2)}) ${d.slice(2)}`;
      if (d.length > 6) v = `(${d.slice(0, 2)}) ${d.slice(2, d.length - 4)}-${d.slice(-4)}`;
      campo.value = v;
    });
  });

  // Checkout (Sprint 3): máscara do CEP e preenchimento automático do endereço pelo ViaCEP.
  // Se o serviço estiver fora do ar, nada quebra: o cliente digita o endereço normalmente.
  document.querySelectorAll("[data-cep]").forEach((campo) => {
    const preencher = (id, valor) => { const el = document.getElementById(id); if (el && valor) el.value = valor; };
    campo.addEventListener("input", async () => {
      const d = campo.value.replace(/\D/g, "").slice(0, 8);
      campo.value = d.length > 5 ? `${d.slice(0, 5)}-${d.slice(5)}` : d;
      if (d.length !== 8) return;
      try {
        const r = await fetch(`https://viacep.com.br/ws/${d}/json/`);
        const end = await r.json();
        if (end.erro) return;
        preencher("logradouro", end.logradouro);
        preencher("bairro", end.bairro);
        preencher("cidade", end.localidade);
        preencher("uf", end.uf);
        document.getElementById("numero")?.focus();
      } catch (e) { /* sem internet ou serviço fora: segue manual */ }
    });
  });

  // Evita enviar o pedido duas vezes com clique duplo
  document.querySelectorAll("form[data-checkout]").forEach((form) => {
    form.addEventListener("submit", () => {
      const botao = form.querySelector("button[type=submit]");
      botao.disabled = true;
      botao.textContent = "Enviando pedido…";
    });
  });

  // Toasts somem sozinhos depois de 4 segundos
  const esconder = (toast) => {
    toast.classList.add("sumindo");
    setTimeout(() => toast.remove(), 300);
  };
  document.querySelectorAll(".toast").forEach((t) => setTimeout(() => esconder(t), 4000));

  // Cria um toast pelo JavaScript (usado no limite de quantidade)
  function avisar(texto) {
    let area = document.querySelector(".toasts");
    if (!area) {
      area = document.createElement("div");
      area.className = "toasts";
      area.setAttribute("role", "status");
      document.body.appendChild(area);
    }
    const t = document.createElement("div");
    t.className = "toast toast-aviso";
    t.textContent = texto;
    area.appendChild(t);
    setTimeout(() => esconder(t), 4000);
  }
});
