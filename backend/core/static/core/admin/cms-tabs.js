(function () {
  function initCmsTabs() {
    var panes = Array.prototype.slice.call(document.querySelectorAll('.cms-lang-pane'))
    if (!panes.length) {
      return
    }

    var firstPane = panes[0]
    if (!firstPane.parentNode) {
      return
    }

    var tabContainer = document.createElement('div')
    tabContainer.className = 'cms-lang-tabs'

    var tabEntries = panes.map(function (pane) {
      var paneClass = Array.prototype.slice.call(pane.classList).find(function (name) {
        return name.indexOf('cms-lang-pane-') === 0
      }) || ''
      var language = paneClass.replace('cms-lang-pane-', '')
      var legend = pane.querySelector('h2, h3, .module-heading')
      var label = legend ? legend.textContent.trim() : language.toUpperCase()

      var button = document.createElement('button')
      button.type = 'button'
      button.className = 'cms-lang-tab'
      button.textContent = label
      button.dataset.cmsLang = language
      tabContainer.appendChild(button)

      return { pane: pane, button: button, language: language }
    })

    firstPane.parentNode.insertBefore(tabContainer, firstPane)

    function activate(language) {
      tabEntries.forEach(function (entry) {
        var isActive = entry.language === language
        entry.pane.classList.toggle('is-active', isActive)
        entry.button.classList.toggle('is-active', isActive)
      })
    }

    tabEntries.forEach(function (entry) {
      entry.button.addEventListener('click', function () {
        activate(entry.language)
      })
    })

    var preferred = tabEntries.some(function (entry) { return entry.language === 'ro' }) ? 'ro' : tabEntries[0].language
    activate(preferred)
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initCmsTabs)
  } else {
    initCmsTabs()
  }
})()
