// ========================================
// Research Form - University of Ngaoundere
// ========================================

let currentLang = "fr";
let translations = {};

// --- i18n ---

async function loadTranslations(lang) {
    const response = await fetch(`/static/lang/${lang}.json`);
    translations = await response.json();
    currentLang = lang;
    applyTranslations();
    buildLikertTables();
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
            el.textContent = value;
        }
    });
    document.documentElement.lang = currentLang;
    if (translations.page && translations.page.form) {
        document.title = translations.page.form;
    }
}

function updateLangButtons() {
    document.querySelectorAll(".lang-btn").forEach((btn) => {
        btn.classList.toggle("active", btn.dataset.lang === currentLang);
    });
}

// --- Likert table generation ---

function buildLikertTables() {
    document.querySelectorAll(".likert-table").forEach((container) => {
        const section = container.dataset.section;
        const subsection = container.dataset.subsection;
        const items = container.dataset.items.split(",");

        // Get items translations
        let itemsObj;
        if (subsection) {
            itemsObj = getNestedValue(translations, `sections.${section}.${subsection}.items`);
        } else {
            itemsObj = getNestedValue(translations, `sections.${section}.items`);
        }

        if (!itemsObj) return;

        // Save current selections
        const savedSelections = {};
        items.forEach((item) => {
            const checked = container.querySelector(`input[name="${item}"]:checked`);
            if (checked) {
                savedSelections[item] = checked.value;
            }
        });

        // Build table
        const scaleLabels = translations.form.scale;
        let html = `
            <table>
                <thead>
                    <tr>
                        <th></th>
                        <th>1</th>
                        <th>2</th>
                        <th>3</th>
                        <th>4</th>
                        <th>5</th>
                    </tr>
                </thead>
                <tbody>`;

        items.forEach((item) => {
            const label = itemsObj[item] || item;
            const code = item.toUpperCase();
            html += `
                    <tr data-item="${item}">
                        <td><span class="item-code">${code}</span>${label}</td>`;
            for (let i = 1; i <= 5; i++) {
                const checked = savedSelections[item] === String(i) ? "checked" : "";
                html += `
                        <td data-label="${i}">
                            <input type="radio" name="${item}" value="${i}" ${checked} required>
                        </td>`;
            }
            html += `
                    </tr>`;
        });

        html += `
                </tbody>
            </table>`;

        container.innerHTML = html;
    });
}

// --- Validation ---

function validateForm() {
    let isValid = true;
    const requiredMsg = translations.form.required;

    // Clear previous errors
    document.querySelectorAll(".error-msg").forEach((el) => {
        el.classList.remove("visible");
        el.textContent = "";
    });
    document.querySelectorAll(".has-error").forEach((el) => {
        el.classList.remove("has-error");
    });

    // Validate gender
    const gender = document.querySelector('input[name="gender"]:checked');
    if (!gender) {
        showFieldError("gender", requiredMsg);
        isValid = false;
    }

    // Validate status
    const status = document.querySelector('input[name="status"]:checked');
    if (!status) {
        showFieldError("status", requiredMsg);
        isValid = false;
    }

    // Validate all Likert items
    document.querySelectorAll(".likert-table").forEach((container) => {
        const items = container.dataset.items.split(",");
        items.forEach((item) => {
            const checked = document.querySelector(`input[name="${item}"]:checked`);
            if (!checked) {
                const row = container.querySelector(`tr[data-item="${item}"]`);
                if (row) row.classList.add("has-error");
                isValid = false;
            }
        });
    });

    // Scroll to first error
    if (!isValid) {
        const firstError =
            document.querySelector(".error-msg.visible") ||
            document.querySelector(".has-error");
        if (firstError) {
            firstError.scrollIntoView({ behavior: "smooth", block: "center" });
        }
    }

    return isValid;
}

function showFieldError(fieldName, message) {
    const errorEl = document.querySelector(`[data-error="${fieldName}"]`);
    if (errorEl) {
        errorEl.textContent = message;
        errorEl.classList.add("visible");
    }
}

// --- Collect form data ---

function collectFormData() {
    const data = {
        language: currentLang,
    };

    // Section A
    const gender = document.querySelector('input[name="gender"]:checked');
    data.gender = gender ? gender.value : null;

    const status = document.querySelector('input[name="status"]:checked');
    data.status = status ? status.value : null;

    // Likert items
    const likertItems = [
        "io1", "io2", "io3", "io4", "io5",
        "im1", "im2", "im3", "im4", "im5",
        "g1", "g2", "g3", "g4", "g5",
        "e1", "e2", "e3", "e4", "e5",
        "a1", "a2", "a3", "a4", "a5",
        "pa1", "pa2", "pa3", "pa4",
        "po1", "po2", "po3", "po4",
        "ps1", "ps2", "ps3", "ps4",
        "pi1", "pi2", "pi3", "pi4",
    ];

    likertItems.forEach((item) => {
        const checked = document.querySelector(`input[name="${item}"]:checked`);
        data[item] = checked ? parseInt(checked.value) : null;
    });

    // Comment
    const comment = document.getElementById("comment").value.trim();
    data.comment = comment || null;

    return data;
}

// --- Submit ---

async function submitForm(data) {
    const submitBtn = document.getElementById("submit-btn");
    const successEl = document.getElementById("success-message");
    const errorEl = document.getElementById("error-message");
    submitBtn.disabled = true;
    successEl.classList.add("hidden");
    errorEl.classList.add("hidden");

    try {
        const response = await fetch("/api/responses", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data),
        });

        if (response.ok) {
            document.getElementById("survey-form").classList.add("hidden");
            successEl.classList.remove("hidden");
            window.scrollTo({ top: 0, behavior: "smooth" });
        } else {
            errorEl.classList.remove("hidden");
            submitBtn.disabled = false;
        }
    } catch (error) {
        errorEl.classList.remove("hidden");
        submitBtn.disabled = false;
    }
}

// --- Progress bar ---

function updateProgress() {
    const allRadios = document.querySelectorAll('input[type="radio"][required]');
    const uniqueNames = new Set();
    allRadios.forEach((r) => uniqueNames.add(r.name));

    const totalFields = uniqueNames.size;
    let answered = 0;
    uniqueNames.forEach((name) => {
        if (document.querySelector(`input[name="${name}"]:checked`)) {
            answered++;
        }
    });

    const percent = totalFields > 0 ? (answered / totalFields) * 100 : 0;
    let bar = document.querySelector(".progress-bar");
    if (!bar) {
        bar = document.createElement("div");
        bar.className = "progress-bar";
        document.body.prepend(bar);
    }
    bar.style.width = `${percent}%`;
}

// --- Init ---

document.addEventListener("DOMContentLoaded", () => {
    // Load default language
    loadTranslations(currentLang);

    // Language switcher
    document.querySelectorAll(".lang-btn").forEach((btn) => {
        btn.addEventListener("click", () => {
            loadTranslations(btn.dataset.lang);
        });
    });

    // Form submission
    document.getElementById("survey-form").addEventListener("submit", (e) => {
        e.preventDefault();
        if (validateForm()) {
            const data = collectFormData();
            submitForm(data);
        }
    });

    // Progress tracking
    document.getElementById("survey-form").addEventListener("change", () => {
        updateProgress();
    });
});
