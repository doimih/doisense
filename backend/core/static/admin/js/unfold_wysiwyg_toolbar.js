(function () {
  const SIMPLE_MODE_SELECTORS = [
    '[data-trix-button-group="block-headings"]',
    '[data-trix-button-group="block-tools"]',
  ];

  document.addEventListener("trix-initialize", function (event) {
    const editor = event.target;
    if (!editor || !editor.dataset) {
      return;
    }

    const mode = (editor.dataset.toolbarMode || "complete").toLowerCase();
    const toolbar = editor.toolbarElement;
    if (!toolbar || mode !== "simple") {
      return;
    }

    SIMPLE_MODE_SELECTORS.forEach(function (selector) {
      toolbar.querySelectorAll(selector).forEach(function (element) {
        element.remove();
      });
    });
  });
})();
