"use strict";

document.addEventListener("DOMContentLoaded", () => {
  const menuButton = document.querySelector("[data-menu-toggle]");
  const menu = document.querySelector("[data-menu]");
  if (menuButton && menu) {
    menuButton.addEventListener("click", () => {
      const isOpen = menu.classList.toggle("is-open");
      menuButton.setAttribute("aria-expanded", String(isOpen));
      const label = isOpen ? "Fechar menu" : "Abrir menu";
      menuButton.setAttribute("aria-label", label);
      menuButton.querySelector("[data-menu-label]").textContent = label;
      menuButton.querySelector(".menu-toggle-icon").textContent = isOpen ? "×" : "☰";
    });
  }

  document.querySelectorAll("form[data-confirm]").forEach((form) => {
    form.addEventListener("submit", (event) => {
      if (!window.confirm(form.dataset.confirm)) event.preventDefault();
    });
  });
});
