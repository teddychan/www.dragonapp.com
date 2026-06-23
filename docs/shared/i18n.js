/* Dragon App — client-side language auto-detection + preference memory.
   Static GitHub Pages can't read the visitor IP server-side, so we use the
   browser's own language list (navigator.languages), which reflects the OS /
   browser locale the visitor configured. One automatic redirect per session,
   and an explicit switcher choice is remembered across visits. */
(function () {
  "use strict";

  var LANGS = ["en-US", "zh-Hans", "zh-Hant", "ja", "ko", "es", "fr"];

  function lsGet(k) { try { return window.localStorage.getItem(k); } catch (e) { return null; } }
  function lsSet(k, v) { try { window.localStorage.setItem(k, v); } catch (e) {} }
  function ssGet(k) { try { return window.sessionStorage.getItem(k); } catch (e) { return null; } }
  function ssSet(k, v) { try { window.sessionStorage.setItem(k, v); } catch (e) {} }

  // Map any BCP-47 browser tag to one of our seven supported codes, or null.
  function matchLang(tag) {
    var t = String(tag).toLowerCase();
    if (t === "zh-hant" || t.indexOf("zh-hant") === 0 ||
        t === "zh-tw" || t === "zh-hk" || t === "zh-mo") return "zh-Hant";
    if (t === "zh-hans" || t.indexOf("zh-hans") === 0 ||
        t === "zh-cn" || t === "zh-sg" || t === "zh-my" || t === "zh") return "zh-Hans";
    var base = t.split("-")[0];
    if (base === "zh") return "zh-Hans";
    if (base === "en") return "en-US";
    if (LANGS.indexOf(base) >= 0) return base; // ja, ko, es, fr
    return null;
  }

  function bestFromBrowser() {
    var tags = (navigator.languages && navigator.languages.length)
      ? navigator.languages
      : [navigator.language || navigator.userLanguage || "en"];
    for (var i = 0; i < tags.length; i++) {
      var m = matchLang(tags[i]);
      if (m) return m;
    }
    return null;
  }

  function currentLang() {
    var l = (document.documentElement.getAttribute("lang") || "en-US");
    return LANGS.indexOf(l) >= 0 ? l : "en-US";
  }

  // Strip a leading "/<lang>/" segment, returning the page path within a language tree.
  function pagePath() {
    var parts = window.location.pathname.split("/"); // e.g. ["","ja","keykey",""]
    var head = parts[1];
    if (head && LANGS.indexOf(head) >= 0 && head !== "en-US") {
      return parts.slice(2).join("/");
    }
    return parts.slice(1).join("/");
  }

  function urlFor(lang) {
    var prefix = (lang === "en-US") ? "/" : "/" + lang + "/";
    return prefix + pagePath();
  }

  // Remember the visitor's explicit choice when they use the switcher.
  function wireSwitcher() {
    var links = document.querySelectorAll("[data-setlang]");
    for (var i = 0; i < links.length; i++) {
      links[i].addEventListener("click", function () {
        lsSet("dragonLang", this.getAttribute("data-setlang"));
      });
    }
  }

  function maybeRedirect() {
    var cur = currentLang();
    var stored = lsGet("dragonLang");
    var target = (stored && LANGS.indexOf(stored) >= 0) ? stored : bestFromBrowser();
    if (!target || target === cur) return;
    if (ssGet("dragonRedirected")) return; // at most one auto-redirect per session
    var dest = urlFor(target);
    if (dest === window.location.pathname) return;
    ssSet("dragonRedirected", "1");
    window.location.replace(dest);
  }

  // Mobile hamburger: tapping any link inside the panel collapses the menu,
  // so there's no separate close button to reach for.
  function wireNavMenu() {
    var menu = document.querySelector(".nav-menu");
    if (!menu) return;
    var links = menu.querySelectorAll(".nav-links a");
    for (var i = 0; i < links.length; i++) {
      links[i].addEventListener("click", function () {
        menu.removeAttribute("open");
      });
    }
  }

  wireSwitcher();
  wireNavMenu();
  maybeRedirect();
})();
