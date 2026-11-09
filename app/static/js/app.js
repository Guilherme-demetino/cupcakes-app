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
