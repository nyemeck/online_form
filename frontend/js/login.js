// ========================================
// Login Page - University of Ngaoundere
// ========================================

let currentLang = "fr";
let translations = {};

// --- i18n ---

async function loadTranslations(lang) {
    const response = await fetch(`/static/lang/${lang}.json`);
    translations = await response.json();
    currentLang = lang;
    applyTranslations();
    updateLangButtons();
}

function getNestedValue(obj, path) {
    return path.split(".").reduce((acc, key) => (acc && acc[key] !== undefined ? acc[key] : null), obj);
}

function applyTranslations() {
    document.querySelectorAll("[data-i18n]").forEach((el) => {
        const key = el.getAttribute("data-i18n");
        const value = getNestedValue(translations, key);
        if (value) {
            if (el.tagName === "INPUT") {
                el.placeholder = value;
            } else {
                el.textContent = value;
            }
        }
    });
    document.documentElement.lang = currentLang;
    if (translations.page && translations.page.login) {
        document.title = translations.page.login;
    }
}

function updateLangButtons() {
    document.querySelectorAll(".lang-btn").forEach((btn) => {
        btn.classList.toggle("active", btn.dataset.lang === currentLang);
    });
}

// --- Init ---

document.addEventListener("DOMContentLoaded", () => {
    loadTranslations(currentLang);

    document.querySelectorAll(".lang-btn").forEach((btn) => {
        btn.addEventListener("click", () => loadTranslations(btn.dataset.lang));
    });

    // Password visibility toggle
    document.getElementById("password-toggle").addEventListener("click", () => {
        const input = document.getElementById("password");
        const icon = document.getElementById("password-toggle-icon");
        if (input.type === "password") {
            input.type = "text";
            icon.src = "/static/assets/icons/eye-off.svg";
        } else {
            input.type = "password";
            icon.src = "/static/assets/icons/eye.svg";
        }
    });

    // Login form submission
    document.getElementById("login-form").addEventListener("submit", async (e) => {
        e.preventDefault();
        const btn = document.getElementById("login-btn");
        const errorEl = document.getElementById("login-error");
        errorEl.classList.remove("visible");
        btn.disabled = true;
        btn.textContent = getNestedValue(translations, "login.loading") || "...";

        const formData = new URLSearchParams();
        formData.append("username", document.getElementById("username").value);
        formData.append("password", document.getElementById("password").value);

        try {
            const response = await fetch("/api/login", {
                method: "POST",
                headers: { "Content-Type": "application/x-www-form-urlencoded" },
                body: formData,
            });

            if (response.ok) {
                const data = await response.json();
                localStorage.setItem("admin_token", data.access_token);
                localStorage.setItem("admin_lang", currentLang);
                window.location.href = "/dashboard";
            } else if (response.status === 429) {
                errorEl.textContent = getNestedValue(translations, "login.rate_limited");
                errorEl.classList.add("visible");
                btn.disabled = false;
                btn.textContent = getNestedValue(translations, "login.submit");
            } else if (response.status === 403) {
                errorEl.textContent = getNestedValue(translations, "login.account_locked");
                errorEl.classList.add("visible");
                btn.disabled = false;
                btn.textContent = getNestedValue(translations, "login.submit");
            } else {
                errorEl.textContent = getNestedValue(translations, "login.error");
                errorEl.classList.add("visible");
                btn.disabled = false;
                btn.textContent = getNestedValue(translations, "login.submit");
            }
        } catch (error) {
            errorEl.classList.add("visible");
            btn.disabled = false;
            btn.textContent = getNestedValue(translations, "login.submit");
        }
    });
});
