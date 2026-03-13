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

  function openGroup(groupElement) {
    var trigger = groupElement.querySelector("h2.cursor-pointer");
    if (!trigger) {
      return;
    }
    if (!isGroupOpen(groupElement)) {
      trigger.click();
    }
  }

  function openOnlyGroup(groups, targetGroup) {
    groups.forEach(function (group) {
      if (group === targetGroup) {
        openGroup(group);
      } else {
        closeGroup(group);
      }
    });
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

    groups.forEach(function (group) {
      var trigger = group.querySelector("h2.cursor-pointer");
      if (!trigger) {
        return;
      }

      trigger.addEventListener("click", function () {
        window.requestAnimationFrame(function () {
          if (!isGroupOpen(group)) {
            return;
          }
          openOnlyGroup(groups, group);
        });
      });

      // Keep navigation intuitive: opening a section on hover also collapses others.
      trigger.addEventListener("mouseenter", function () {
        openOnlyGroup(groups, group);
      });
    });

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
