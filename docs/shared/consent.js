/* Dragon App — custom consent banner for Google Consent Mode v2.
   The default (denied) state and the Google tag are set in <head> before this
   runs. This file shows the banner when no choice is stored yet and calls
   gtag('consent','update', ...) when the visitor accepts or rejects. */
(function () {
  "use strict";
  var KEY = "dragonConsent";

  function get() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }
  function set(v) { try { localStorage.setItem(KEY, v); } catch (e) {} }

  function update(granted) {
    if (typeof window.gtag !== "function") return;
    var v = granted ? "granted" : "denied";
    window.gtag("consent", "update", {
      ad_storage: v,
      ad_user_data: v,
      ad_personalization: v,
      analytics_storage: v
    });
  }

  function init() {
    var banner = document.getElementById("consent-banner");
    if (!banner) return;
    var choice = get();
    if (choice === "granted" || choice === "denied") return; // decided already

    banner.removeAttribute("hidden");
    var accept = banner.querySelector(".consent-accept");
    var reject = banner.querySelector(".consent-reject");
    if (accept) accept.addEventListener("click", function () {
      set("granted"); update(true); banner.setAttribute("hidden", "");
    });
    if (reject) reject.addEventListener("click", function () {
      set("denied"); update(false); banner.setAttribute("hidden", "");
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
