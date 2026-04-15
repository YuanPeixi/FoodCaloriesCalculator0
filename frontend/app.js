/**
 * Food Calories Calculator — Frontend Application
 *
 * Handles image upload, API communication, and result rendering.
 */

(function () {
    "use strict";

    // ─── DOM References ────────────────────────────────────────
    const tabs = document.querySelectorAll(".tab");
    const tabContents = document.querySelectorAll(".tab-content");

    const singleUploadArea = document.getElementById("single-upload-area");
    const singleFile = document.getElementById("single-file");
    const singlePreview = document.getElementById("single-preview");
    const singlePlaceholder = document.getElementById("single-placeholder");
    const btnRecognize = document.getElementById("btn-recognize");

    const beforeUploadArea = document.getElementById("before-upload-area");
    const beforeFile = document.getElementById("before-file");
    const beforePreview = document.getElementById("before-preview");
    const beforePlaceholder = document.getElementById("before-placeholder");

    const afterUploadArea = document.getElementById("after-upload-area");
    const afterFile = document.getElementById("after-file");
    const afterPreview = document.getElementById("after-preview");
    const afterPlaceholder = document.getElementById("after-placeholder");
    const btnCompare = document.getElementById("btn-compare");

    const loadingEl = document.getElementById("loading");
    const resultsEl = document.getElementById("results");
    const resultsContent = document.getElementById("results-content");

    // ─── State ─────────────────────────────────────────────────
    let singleImageFile = null;
    let beforeImageFile = null;
    let afterImageFile = null;

    // ─── Tab Switching ─────────────────────────────────────────
    tabs.forEach((tab) => {
        tab.addEventListener("click", () => {
            tabs.forEach((t) => t.classList.remove("active"));
            tabContents.forEach((c) => c.classList.remove("active"));
            tab.classList.add("active");
            document
                .getElementById("tab-" + tab.dataset.tab)
                .classList.add("active");
        });
    });

    // ─── Helpers ───────────────────────────────────────────────
    function getSelectedModel() {
        const radio = document.querySelector('input[name="model"]:checked');
        return radio ? radio.value : "openrouter";
    }

    function setupUpload(area, fileInput, preview, placeholder, onFile) {
        area.addEventListener("click", () => fileInput.click());
        area.addEventListener("dragover", (e) => {
            e.preventDefault();
            area.classList.add("has-image");
        });
        area.addEventListener("dragleave", () => {
            if (!preview.src) area.classList.remove("has-image");
        });
        area.addEventListener("drop", (e) => {
            e.preventDefault();
            const file = e.dataTransfer.files[0];
            if (file) handleFile(file, area, preview, placeholder, onFile);
        });
        fileInput.addEventListener("change", () => {
            const file = fileInput.files[0];
            if (file) handleFile(file, area, preview, placeholder, onFile);
        });
    }

    function handleFile(file, area, preview, placeholder, onFile) {
        const reader = new FileReader();
        reader.onload = (e) => {
            preview.src = e.target.result;
            preview.classList.remove("hidden");
            placeholder.classList.add("hidden");
            area.classList.add("has-image");
        };
        reader.readAsDataURL(file);
        onFile(file);
    }

    function showLoading() {
        loadingEl.classList.remove("hidden");
        resultsEl.classList.add("hidden");
    }

    function hideLoading() {
        loadingEl.classList.add("hidden");
    }

    function showError(msg) {
        hideLoading();
        resultsEl.classList.remove("hidden");
        resultsContent.innerHTML =
            '<div class="result-description" style="background:#ffeaa7;color:#d63031;">' +
            "⚠️ " + escapeHtml(msg) +
            "</div>";
    }

    function escapeHtml(text) {
        const div = document.createElement("div");
        div.textContent = text;
        return div.innerHTML;
    }

    // ─── Food Table Rendering ──────────────────────────────────
    function foodTable(foods, totalCalories) {
        if (!foods || foods.length === 0) {
            return "<p>未识别到食物</p>";
        }
        let html = '<table class="food-table">';
        html +=
            "<thead><tr><th>食物</th><th>热量/100g</th><th>估计重量(g)</th><th>估计热量(kcal)</th></tr></thead>";
        html += "<tbody>";
        foods.forEach((f) => {
            html += "<tr>";
            html += "<td>" + escapeHtml(f.name) + "</td>";
            html += "<td>" + f.calories_per_100g.toFixed(1) + "</td>";
            html += "<td>" + f.estimated_grams.toFixed(1) + "</td>";
            html += "<td>" + f.estimated_calories.toFixed(1) + "</td>";
            html += "</tr>";
        });
        html += '<tr class="total-row">';
        html += '<td colspan="3">总计</td>';
        html += "<td>" + totalCalories.toFixed(1) + " kcal</td>";
        html += "</tr>";
        html += "</tbody></table>";
        return html;
    }

    // ─── Render Single Result ──────────────────────────────────
    function renderSingleResult(data) {
        hideLoading();
        resultsEl.classList.remove("hidden");

        let html = '<span class="model-badge">模型: ' + escapeHtml(data.model_used) + "</span>";
        if (data.description) {
            html += '<div class="result-description">' + escapeHtml(data.description) + "</div>";
        }
        html += foodTable(data.foods, data.total_calories);
        resultsContent.innerHTML = html;
    }

    // ─── Render Comparison Result ──────────────────────────────
    function renderComparisonResult(data) {
        hideLoading();
        resultsEl.classList.remove("hidden");

        let html = '<span class="model-badge">模型: ' + escapeHtml(data.model_used) + "</span>";
        if (data.description) {
            html += '<div class="result-description">' + escapeHtml(data.description) + "</div>";
        }

        html += '<p class="section-title">🍽️ 饭前食物</p>';
        html += foodTable(
            data.before_foods,
            data.before_foods.reduce((s, f) => s + f.estimated_calories, 0)
        );

        html += '<p class="section-title">🥢 饭后剩余</p>';
        html += foodTable(
            data.after_foods,
            data.after_foods.reduce((s, f) => s + f.estimated_calories, 0)
        );

        html += '<p class="section-title">✅ 实际摄入</p>';
        html += foodTable(data.consumed_foods, data.total_consumed_calories);

        resultsContent.innerHTML = html;
    }

    // ─── API Calls ─────────────────────────────────────────────
    async function recognizeFood() {
        if (!singleImageFile) return;
        showLoading();
        btnRecognize.disabled = true;

        const form = new FormData();
        form.append("image", singleImageFile);
        form.append("model", getSelectedModel());

        try {
            const res = await fetch("/api/food/recognize", {
                method: "POST",
                body: form,
            });
            if (!res.ok) {
                const err = await res.json().catch(() => ({}));
                throw new Error(err.detail || "请求失败 (" + res.status + ")");
            }
            const data = await res.json();
            renderSingleResult(data);
        } catch (err) {
            showError(err.message);
        } finally {
            btnRecognize.disabled = false;
        }
    }

    async function compareMeals() {
        if (!beforeImageFile || !afterImageFile) return;
        showLoading();
        btnCompare.disabled = true;

        const form = new FormData();
        form.append("before_image", beforeImageFile);
        form.append("after_image", afterImageFile);
        form.append("model", getSelectedModel());

        try {
            const res = await fetch("/api/food/compare", {
                method: "POST",
                body: form,
            });
            if (!res.ok) {
                const err = await res.json().catch(() => ({}));
                throw new Error(err.detail || "请求失败 (" + res.status + ")");
            }
            const data = await res.json();
            renderComparisonResult(data);
        } catch (err) {
            showError(err.message);
        } finally {
            btnCompare.disabled = false;
        }
    }

    // ─── Wiring ────────────────────────────────────────────────
    setupUpload(singleUploadArea, singleFile, singlePreview, singlePlaceholder, (f) => {
        singleImageFile = f;
        btnRecognize.disabled = false;
    });

    setupUpload(beforeUploadArea, beforeFile, beforePreview, beforePlaceholder, (f) => {
        beforeImageFile = f;
        if (afterImageFile) btnCompare.disabled = false;
    });

    setupUpload(afterUploadArea, afterFile, afterPreview, afterPlaceholder, (f) => {
        afterImageFile = f;
        if (beforeImageFile) btnCompare.disabled = false;
    });

    btnRecognize.addEventListener("click", recognizeFood);
    btnCompare.addEventListener("click", compareMeals);
})();
