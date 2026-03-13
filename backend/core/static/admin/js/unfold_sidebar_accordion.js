(function () {
  function isGroupOpen(groupElement) {
    var list = groupElement.querySelector("ol");
    if (!list) {
      return false;
    }
    return window.getComputedStyle(list).display !== "none";
  }

  function closeGroup(groupElement) {
    var trigger = groupElement.querySelector("h2.cursor-pointer");
    if (!trigger) {
      return;
    }
    if (isGroupOpen(groupElement)) {
      trigger.click();
    }
  }

  function initSidebarAccordion() {
    var container = document.getElementById("nav-sidebar-apps");
    if (!container) {
      return;
    }

    var groups = Array.prototype.slice.call(
      container.querySelectorAll("div[x-data]")
    ).filter(function (group) {
      return Boolean(group.querySelector("h2.cursor-pointer") && group.querySelector("ol"));
    });

    if (!groups.length) {
      return;
    }

    var activeLink = container.querySelector("a.active");
    if (activeLink) {
      var activeGroup = activeLink.closest("div[x-data]");
      groups.forEach(function (group) {
        if (group !== activeGroup) {
          closeGroup(group);
        }
      });
    }
  }

  document.addEventListener("DOMContentLoaded", initSidebarAccordion);
})();
