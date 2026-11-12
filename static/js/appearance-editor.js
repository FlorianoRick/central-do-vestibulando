"use strict";

document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("[data-appearance-form]");
  const preview = document.querySelector("[data-appearance-preview]");
  if (!form || !preview) return;

  const dirtyNotice = document.querySelector("[data-unsaved-indicator]");
  const previewState = document.querySelector("[data-preview-state]");
  const orderField = form.querySelector("#id_home_section_order");
  let dirty = form.dataset.dirty === "true";

  const markDirty = () => {
    dirty = true;
    if (dirtyNotice) dirtyNotice.hidden = false;
    if (previewState) previewState.textContent = "Alterações não salvas";
  };
  if (dirty) markDirty();

  const cssValueFor = (control) => {
    let value = control.type === "checkbox" ? String(control.checked) : control.value;
    if (control.dataset.cssMap) {
      try {
        value = JSON.parse(control.dataset.cssMap)[value] ?? value;
      } catch (_error) {
        return null;
      }
    }
    if (control.dataset.cssUnit) value = `${value}${control.dataset.cssUnit}`;
    return value;
  };

  const updatePreviewVariable = (control) => {
    const variable = control.dataset.cssVar;
    if (!variable) return;
    const value = cssValueFor(control);
    if (value !== null && value !== "") preview.style.setProperty(`--${variable}`, value);
  };

  form.querySelectorAll("[data-css-var]").forEach((control) => {
    updatePreviewVariable(control);
    control.addEventListener("input", () => updatePreviewVariable(control));
    control.addEventListener("change", () => updatePreviewVariable(control));
  });

  form.querySelectorAll("[data-color-picker]").forEach((picker) => {
    const textInput = document.getElementById(picker.dataset.colorPicker);
    if (!textInput) return;
    picker.addEventListener("input", () => {
      textInput.value = picker.value.toUpperCase();
      updatePreviewVariable(textInput);
      markDirty();
    });
    textInput.addEventListener("input", () => {
      if (/^#[0-9a-f]{6}$/i.test(textInput.value)) picker.value = textInput.value;
    });
  });

  form.querySelectorAll("[data-reset-field]").forEach((button) => {
    button.addEventListener("click", () => {
      const field = form.elements.namedItem(button.dataset.resetField);
      if (!field) return;
      field.value = field.dataset.default;
      field.dispatchEvent(new Event("input", { bubbles: true }));
      field.dispatchEvent(new Event("change", { bubbles: true }));
    });
  });

  form.addEventListener("input", (event) => {
    if (event.target.matches("input, select, textarea")) markDirty();
  });
  form.addEventListener("change", (event) => {
    if (event.target.matches("input, select, textarea")) markDirty();
  });

  const orderList = document.querySelector("[data-section-order-list]");
  const syncOrder = () => {
    if (!orderList || !orderField) return;
    const keys = Array.from(orderList.querySelectorAll("[data-section-key]"), (item) => item.dataset.sectionKey);
    orderField.value = JSON.stringify(keys);
  };
  if (orderList && orderField) {
    try {
      const savedOrder = JSON.parse(orderField.value);
      const items = new Map(Array.from(orderList.children, (item) => [item.dataset.sectionKey, item]));
      if (Array.isArray(savedOrder) && savedOrder.length === items.size && savedOrder.every((key) => items.has(key))) {
        savedOrder.forEach((key) => orderList.append(items.get(key)));
      }
    } catch (_error) {
      // Keep the predefined order if a draft value is malformed.
    }
    orderList.addEventListener("click", (event) => {
      const button = event.target.closest("button[data-order-up], button[data-order-down]");
      if (!button) return;
      const item = button.closest("[data-section-key]");
      if (button.hasAttribute("data-order-up") && item.previousElementSibling) {
        orderList.insertBefore(item, item.previousElementSibling);
      } else if (button.hasAttribute("data-order-down") && item.nextElementSibling) {
        orderList.insertBefore(item.nextElementSibling, item);
      }
      syncOrder();
      markDirty();
    });
  }

  const applySectionDefaults = (section) => {
    section.querySelectorAll("input, select, textarea").forEach((control) => {
      if (control.type === "file") {
        control.value = "";
        return;
      }
      if (control.name.endsWith("-clear")) {
        control.checked = true;
        return;
      }
      if (control.type === "checkbox") {
        control.checked = control.dataset.default === "true";
      } else if (control.dataset.default !== undefined) {
        control.value = control.dataset.default;
      }
      control.dispatchEvent(new Event("input", { bubbles: true }));
      control.dispatchEvent(new Event("change", { bubbles: true }));
    });
    if (section.dataset.section === "layout") {
      try {
        const keys = JSON.parse(orderField.value);
        const items = new Map(Array.from(orderList.children, (item) => [item.dataset.sectionKey, item]));
        keys.forEach((key) => orderList.append(items.get(key)));
      } catch (_error) {
        // The server validates this value before it is saved.
      }
    }
    if (section.dataset.section === "branding") {
      updateLogoPreview(true);
      if (faviconClearInput) faviconClearInput.dispatchEvent(new Event("change", { bubbles: true }));
      else if (faviconPreview) faviconPreview.hidden = true;
    }
    markDirty();
  };

  document.querySelectorAll("[data-reset-section]").forEach((button) => {
    button.addEventListener("click", () => {
      const section = button.closest("[data-section]");
      if (section) applySectionDefaults(section);
    });
  });

  const updateLogoPreview = (cleared = false) => {
    const logoInput = form.querySelector("input[name='logo']");
    const clearInput = form.querySelector("input[name='logo-clear']");
    const logo = document.querySelector("[data-preview-logo]");
    const mark = document.querySelector("[data-preview-mark]");
    const fallback = document.querySelector("[data-preview-brand-fallback]");
    const selectedFile = logoInput?.files?.[0];
    const showFallback = cleared || Boolean(clearInput?.checked);
    if (selectedFile) {
      logo.src = URL.createObjectURL(selectedFile);
      logo.hidden = false;
      mark.hidden = true;
      fallback.hidden = true;
    } else if (!showFallback && logo.dataset.savedSrc) {
      logo.src = logo.dataset.savedSrc;
      logo.hidden = false;
      mark.hidden = true;
      fallback.hidden = true;
    } else {
      logo.hidden = true;
      mark.hidden = false;
      fallback.hidden = false;
    }
  };

  const logoInput = form.querySelector("input[name='logo']");
  const logoClearInput = form.querySelector("input[name='logo-clear']");
  logoInput?.addEventListener("change", () => updateLogoPreview());
  logoClearInput?.addEventListener("change", () => updateLogoPreview());

  const faviconInput = form.querySelector("input[name='favicon']");
  const faviconClearInput = form.querySelector("input[name='favicon-clear']");
  const faviconPreview = document.querySelector("[data-favicon-preview]");
  faviconInput?.addEventListener("change", () => {
    const file = faviconInput.files?.[0];
    if (file && faviconPreview) {
      faviconPreview.src = URL.createObjectURL(file);
      faviconPreview.hidden = false;
    }
  });
  faviconClearInput?.addEventListener("change", () => {
    if (!faviconPreview) return;
    if (faviconClearInput.checked) faviconPreview.hidden = true;
    else if (faviconPreview.dataset.savedSrc) {
      faviconPreview.src = faviconPreview.dataset.savedSrc;
      faviconPreview.hidden = false;
    }
  });

  document.querySelector("[data-discard]")?.addEventListener("click", () => {
    if (!dirty || window.confirm("Descartar todas as alterações ainda não salvas?")) window.location.reload();
  });
  document.querySelector("[data-show-preview]")?.addEventListener("click", () => {
    document.querySelector("[data-appearance-preview]")?.scrollIntoView({ behavior: "smooth", block: "center" });
  });
  form.addEventListener("submit", (event) => {
    if (event.submitter?.matches("[data-confirm-restore]") && !window.confirm("Restaurar todas as configurações originais? Essa ação será publicada imediatamente.")) {
      event.preventDefault();
      return;
    }
    dirty = false;
  });
  window.addEventListener("beforeunload", (event) => {
    if (!dirty) return;
    event.preventDefault();
    event.returnValue = "";
  });
});
