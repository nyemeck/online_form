// ========================================
// Dashboard - University of Ngaoundere
// ========================================

let currentLang = localStorage.getItem("admin_lang") || "fr";
let translations = {};
const token = localStorage.getItem("admin_token");

// --- Auth check ---

if (!token) {
    window.location.href = "/login";
}

// --- i18n ---

async function loadTranslations(lang) {
    const response = await fetch(`/static/lang/${lang}.json`);
    translations = await response.json();
    currentLang = lang;
    localStorage.setItem("admin_lang", lang);
    applyTranslations();
    updateLangButtons();
    loadStats();
}

function t(path) {
    return path.split(".").reduce((acc, key) => (acc && acc[key] !== undefined ? acc[key] : null), translations);
}

function applyTranslations() {
    document.querySelectorAll("[data-i18n]").forEach((el) => {
        const value = t(el.getAttribute("data-i18n"));
        if (value) el.textContent = value;
    });
    document.documentElement.lang = currentLang;
}

function updateLangButtons() {
    document.querySelectorAll(".lang-btn").forEach((btn) => {
        btn.classList.toggle("active", btn.dataset.lang === currentLang);
    });
}

// --- API calls ---

async function apiGet(endpoint) {
    const response = await fetch(endpoint, {
        headers: { "Authorization": `Bearer ${token}` },
    });
    if (response.status === 401) {
        localStorage.removeItem("admin_token");
        window.location.href = "/login";
        return null;
    }
    return response.json();
}

function apiDownload(endpoint, filename) {
    const link = document.createElement("a");
    link.href = endpoint;
    link.download = filename;

    // Use fetch with auth header
    fetch(endpoint, {
        headers: { "Authorization": `Bearer ${token}` },
    })
        .then((res) => {
            if (res.status === 401) {
                localStorage.removeItem("admin_token");
                window.location.href = "/login";
                return;
            }
            return res.blob();
        })
        .then((blob) => {
            if (!blob) return;
            const url = URL.createObjectURL(blob);
            link.href = url;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(url);
        });
}

// --- Render dashboard ---

async function loadStats() {
    const contentEl = document.getElementById("dashboard-content");
    const stats = await apiGet("/api/stats");
    if (!stats) return;

    if (stats.total === 0) {
        contentEl.innerHTML = `<div class="no-data">${t("dashboard.no_data")}</div>`;
        return;
    }

    let html = "";

    // Total card
    html += `
        <div class="total-card">
            <div class="total-number">${stats.total}</div>
            <div class="total-label">${t("dashboard.total")}</div>
        </div>`;

    // Gender stats
    html += buildStatSection(
        t("dashboard.by_gender"),
        stats.by_gender,
        t("dashboard.gender_labels"),
        stats.total
    );

    // Status stats
    html += buildStatSection(
        t("dashboard.by_status"),
        stats.by_status,
        t("dashboard.status_labels"),
        stats.total
    );

    // Language stats
    html += buildStatSection(
        t("dashboard.by_language"),
        stats.by_language,
        t("dashboard.language_labels"),
        stats.total
    );

    // Export section
    html += `
        <div class="export-section">
            <h2>${t("dashboard.export")}</h2>
            <div class="export-buttons">
                <button class="export-btn export-btn-csv" id="export-csv-btn">
                    ${t("dashboard.export_csv")}
                </button>
                <button class="export-btn export-btn-excel" id="export-excel-btn">
                    ${t("dashboard.export_excel")}
                </button>
            </div>
        </div>`;

    contentEl.innerHTML = html;

    // Bind export buttons
    document.getElementById("export-csv-btn").addEventListener("click", () => {
        apiDownload("/api/export/csv", "responses.csv");
    });
    document.getElementById("export-excel-btn").addEventListener("click", () => {
        apiDownload("/api/export/excel", "responses.xlsx");
    });
}

function buildStatSection(title, data, labels, total) {
    let rows = "";
    for (const [code, count] of Object.entries(data)) {
        const label = (labels && labels[code]) || code;
        const percent = total > 0 ? ((count / total) * 100).toFixed(1) : 0;
        rows += `
            <tr>
                <td>${label}</td>
                <td class="stat-bar-cell">
                    <div class="stat-bar">
                        <div class="stat-bar-fill" style="width: ${percent}%"></div>
                    </div>
                </td>
                <td>${count} (${percent}%)</td>
            </tr>`;
    }

    return `
        <div class="stat-section">
            <h2>${title}</h2>
            <table class="stat-table">
                <tbody>${rows}</tbody>
            </table>
        </div>`;
}

// --- Init ---

document.addEventListener("DOMContentLoaded", () => {
    loadTranslations(currentLang);

    // Language switcher
    document.querySelectorAll(".lang-btn").forEach((btn) => {
        btn.addEventListener("click", () => loadTranslations(btn.dataset.lang));
    });

    // Refresh
    document.getElementById("refresh-btn").addEventListener("click", () => {
        loadStats();
    });

    // Logout
    document.getElementById("logout-btn").addEventListener("click", () => {
        localStorage.removeItem("admin_token");
        localStorage.removeItem("admin_lang");
        window.location.href = "/login";
    });
});
