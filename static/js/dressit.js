/* DressIT — interactions front : thème, menu mobile, galerie, quantités. */
(function () {
    "use strict";

    /* ---- Thème sombre / clair (mémorisé) ---- */
    const root = document.documentElement;
    const stored = localStorage.getItem("dressit-theme");
    if (stored) {
        root.setAttribute("data-theme", stored);
    }

    function toggleTheme() {
        const current = root.getAttribute("data-theme") || "dark";
        const next = current === "dark" ? "light" : "dark";
        root.setAttribute("data-theme", next);
        localStorage.setItem("dressit-theme", next);
        updateThemeIcon(next);
    }

    function updateThemeIcon(theme) {
        const btn = document.getElementById("theme-toggle");
        if (btn) btn.textContent = theme === "dark" ? "☀️" : "🌙";
    }

    document.addEventListener("DOMContentLoaded", function () {
        const btn = document.getElementById("theme-toggle");
        if (btn) {
            updateThemeIcon(root.getAttribute("data-theme") || "dark");
            btn.addEventListener("click", toggleTheme);
        }

        /* ---- Menu mobile ---- */
        const burger = document.getElementById("burger");
        const mobileNav = document.getElementById("mobile-nav");
        if (burger && mobileNav) {
            burger.addEventListener("click", function () {
                mobileNav.classList.toggle("open");
            });
        }

        /* ---- Sélecteur de langue : soumet au changement ---- */
        const langSelect = document.getElementById("lang-select");
        if (langSelect) {
            langSelect.addEventListener("change", function () {
                langSelect.closest("form").submit();
            });
        }

        /* ---- Contrôles de quantité (+/-) ---- */
        document.querySelectorAll(".qty-control").forEach(function (ctrl) {
            const input = ctrl.querySelector("input");
            const dec = ctrl.querySelector('[data-action="dec"]');
            const inc = ctrl.querySelector('[data-action="inc"]');
            const min = parseInt(input.getAttribute("min") || "1", 10);
            const max = parseInt(input.getAttribute("max") || "999", 10);
            if (dec) dec.addEventListener("click", function () {
                input.value = Math.max(min, (parseInt(input.value, 10) || min) - 1);
                input.dispatchEvent(new Event("change", { bubbles: true }));
            });
            if (inc) inc.addEventListener("click", function () {
                input.value = Math.min(max, (parseInt(input.value, 10) || min) + 1);
                input.dispatchEvent(new Event("change", { bubbles: true }));
            });
        });

        /* ---- Panier : mise à jour auto de la quantité ---- */
        document.querySelectorAll("form.cart-qty-form input[type=number]").forEach(function (input) {
            input.addEventListener("change", function () {
                input.closest("form").submit();
            });
        });

        /* ---- Galerie produit : clic sur miniature ---- */
        const mainImg = document.getElementById("gallery-main-img");
        if (mainImg) {
            document.querySelectorAll(".gallery-thumbs img").forEach(function (thumb) {
                thumb.addEventListener("click", function () {
                    mainImg.src = thumb.getAttribute("data-full") || thumb.src;
                    document.querySelectorAll(".gallery-thumbs img").forEach(function (t) {
                        t.classList.remove("active");
                    });
                    thumb.classList.add("active");
                });
            });
        }

        /* ---- Favoris : ajout/retrait sans recharger la page ---- */
        function getCookie(name) {
            const m = document.cookie.match("(^|;)\\s*" + name + "\\s*=\\s*([^;]+)");
            return m ? m.pop() : "";
        }
        document.querySelectorAll("form.wishlist-form").forEach(function (form) {
            form.addEventListener("submit", function (e) {
                e.preventDefault();
                const btn = form.querySelector("button");
                fetch(form.action, {
                    method: "POST",
                    headers: {
                        "X-Requested-With": "XMLHttpRequest",
                        "X-CSRFToken": getCookie("csrftoken"),
                    },
                })
                    .then(function (r) { return r.json(); })
                    .then(function (data) {
                        btn.classList.toggle("active", data.added);
                        if (btn.classList.contains("heart-inline")) {
                            btn.innerHTML = data.added ? "♥ " + (btn.dataset.on || "Dans vos favoris")
                                                       : "♥ " + (btn.dataset.off || "Ajouter aux favoris");
                        }
                        const badge = document.querySelector('a[href$="/favoris/"] .cart-badge');
                        const iconBtn = document.querySelector('a[href$="/favoris/"]');
                        if (data.count > 0) {
                            if (badge) { badge.textContent = data.count; }
                            else if (iconBtn) {
                                const span = document.createElement("span");
                                span.className = "cart-badge";
                                span.textContent = data.count;
                                iconBtn.appendChild(span);
                            }
                        } else if (badge) { badge.remove(); }
                    })
                    .catch(function () { form.submit(); });
            });
        });

        /* ---- Auto-masquage des toasts ---- */
        document.querySelectorAll(".toast").forEach(function (toast) {
            setTimeout(function () {
                toast.style.transition = "opacity .4s ease, transform .4s ease";
                toast.style.opacity = "0";
                toast.style.transform = "translateX(40px)";
                setTimeout(function () { toast.remove(); }, 400);
            }, 4000);
        });
    });
})();
