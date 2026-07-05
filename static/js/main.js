/* Task & Calc — JS puro (sin frameworks) */

document.addEventListener("DOMContentLoaded", function () {
  // Renderiza los iconos de Lucide (<i data-lucide="...">)
  if (window.lucide) {
    lucide.createIcons();
  }

  // Oculta los mensajes flash automáticamente después de 4 segundos
  document.querySelectorAll(".message").forEach(function (msg) {
    setTimeout(function () {
      msg.style.transition = "opacity 0.4s";
      msg.style.opacity = "0";
      setTimeout(function () {
        msg.remove();
      }, 400);
    }, 4000);
  });

  initKanban();
  initCalculator();
});

/* ==========================================================
   Tablero Kanban: drag & drop con Pointer Events.
   Funciona con mouse y con pantalla táctil (teléfono).
   La posición dentro de la columna define la prioridad.
   ========================================================== */
function initKanban() {
  var board = document.querySelector(".kanban");
  if (!board) return;

  var reorderUrl = board.dataset.reorderUrl;
  var csrfToken = board.dataset.csrf;
  var drag = null; // { card, ghost, placeholder, dx, dy }

  board.addEventListener("pointerdown", function (e) {
    var handle = e.target.closest(".drag-handle");
    if (!handle) return;
    e.preventDefault();

    var card = handle.closest(".kanban-card");
    var rect = card.getBoundingClientRect();

    // Fantasma que sigue al puntero
    var ghost = card.cloneNode(true);
    ghost.classList.add("kanban-ghost");
    ghost.style.width = rect.width + "px";
    ghost.style.left = rect.left + "px";
    ghost.style.top = rect.top + "px";
    document.body.appendChild(ghost);

    // Hueco que marca dónde caerá la tarjeta
    var placeholder = document.createElement("li");
    placeholder.className = "kanban-placeholder";
    placeholder.style.height = rect.height + "px";
    card.after(placeholder);
    card.classList.add("is-dragging");

    drag = {
      card: card,
      ghost: ghost,
      placeholder: placeholder,
      dx: e.clientX - rect.left,
      dy: e.clientY - rect.top,
    };

    handle.setPointerCapture(e.pointerId);
    handle.addEventListener("pointermove", onMove);
    handle.addEventListener("pointerup", onDrop, { once: true });
    handle.addEventListener("pointercancel", onDrop, { once: true });
  });

  function onMove(e) {
    if (!drag) return;
    drag.ghost.style.left = e.clientX - drag.dx + "px";
    drag.ghost.style.top = e.clientY - drag.dy + "px";

    // Auto-scroll cuando el puntero se acerca al borde de la pantalla
    if (e.clientY < 90) window.scrollBy(0, -12);
    else if (e.clientY > window.innerHeight - 90) window.scrollBy(0, 12);

    // Columna bajo el puntero (el fantasma tiene pointer-events: none)
    var under = document.elementFromPoint(e.clientX, e.clientY);
    if (!under) return;
    var body = under.closest(".kanban-body");
    if (!body) {
      var column = under.closest(".kanban-column");
      if (column) body = column.querySelector(".kanban-body");
    }
    if (!body) return;

    // Insertar el hueco antes de la primera tarjeta cuyo centro
    // esté por debajo del puntero
    var cards = body.querySelectorAll(".kanban-card:not(.is-dragging)");
    var next = null;
    for (var i = 0; i < cards.length; i++) {
      var r = cards[i].getBoundingClientRect();
      if (e.clientY < r.top + r.height / 2) {
        next = cards[i];
        break;
      }
    }
    if (next) body.insertBefore(drag.placeholder, next);
    else body.appendChild(drag.placeholder);
  }

  function onDrop(e) {
    if (!drag) return;
    var handle = e.target;
    handle.removeEventListener("pointermove", onMove);

    drag.placeholder.before(drag.card);
    drag.placeholder.remove();
    drag.ghost.remove();
    drag.card.classList.remove("is-dragging");
    drag = null;

    updateCounts();
    saveOrder();
  }

  function updateCounts() {
    board.querySelectorAll(".kanban-column").forEach(function (col) {
      col.querySelector(".kanban-count").textContent =
        col.querySelectorAll(".kanban-card").length;
    });
  }

  function saveOrder() {
    var columns = {};
    board.querySelectorAll(".kanban-column").forEach(function (col) {
      columns[col.dataset.status] = Array.from(
        col.querySelectorAll(".kanban-card")
      ).map(function (card) {
        return parseInt(card.dataset.id, 10);
      });
    });

    fetch(reorderUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
      body: JSON.stringify({ columns: columns }),
    }).catch(function () {
      // Si falla el guardado, recargamos para volver al estado real
      window.location.reload();
    });
  }
}

/* ==========================================================
   Calculadora: tecla "C" limpia los campos y la pantalla
   ========================================================== */
function initCalculator() {
  var clearBtn = document.getElementById("calc-clear");
  if (!clearBtn) return;

  clearBtn.addEventListener("click", function () {
    document
      .querySelectorAll("#calc-form input[type='number']")
      .forEach(function (input) {
        input.value = "";
      });
    var screen = document.querySelector(".calc-screen-value");
    if (screen) screen.textContent = "0.00";
    document.querySelectorAll("#calc-form .field-error").forEach(function (el) {
      el.remove();
    });
  });
}
