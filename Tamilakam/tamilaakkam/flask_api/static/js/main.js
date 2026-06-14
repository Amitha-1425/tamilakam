document.addEventListener("DOMContentLoaded", () => {
    setupServerLinks();

    if (window.lucide) {
        window.lucide.createIcons();
    }

    const menuButton = document.querySelector(".menu-toggle");
    const mobileMenu = document.querySelector(".mobile-menu");

    if (menuButton && mobileMenu) {
        menuButton.addEventListener("click", () => {
            const isOpen = !mobileMenu.classList.toggle("hidden");
            menuButton.setAttribute("aria-expanded", String(isOpen));
        });
    }

    setupUploadPreview();
    setupStaticResultPage();
    setupCopyButton();
    setupDownloadButton();
});

function isStaticMode() {
    return window.location.protocol === "file:" || window.location.port === "5500";
}

function setupServerLinks() {
    if (isStaticMode()) {
        return;
    }

    const routes = {
        "index.html": "/",
        "upload.html": "/upload",
        "result.html": "/result",
        "about.html": "/about",
    };

    document.querySelectorAll("a[href]").forEach((link) => {
        const route = routes[link.getAttribute("href")];
        if (route) {
            link.setAttribute("href", route);
        }
    });
}

function setupUploadPreview() {
    const input = document.getElementById("imageInput");
    const dropZone = document.getElementById("dropZone");
    const previewPanel = document.getElementById("previewPanel");
    const preview = document.getElementById("imagePreview");
    const fileName = document.getElementById("fileName");
    const convertButton = document.getElementById("convertButton");
    const textInput = document.getElementById("tanglishText");
    const form = document.getElementById("uploadForm");

    if (!input || !dropZone) {
        return;
    }

    if (form && !isStaticMode()) {
        form.action = form.dataset.serverAction || "/upload";
        form.method = "POST";
    }

    const updateButtonState = () => {
        const hasFile = input.files && input.files.length > 0;
        const hasText = textInput && textInput.value.trim().length > 0;
        convertButton.disabled = !(hasFile || hasText);
    };

    const showFile = (file) => {
        if (!file || !file.type.startsWith("image/")) {
            return;
        }

        const reader = new FileReader();
        reader.onload = (event) => {
            preview.src = event.target.result;
            fileName.textContent = file.name;
            previewPanel.classList.remove("hidden");
            previewPanel.classList.add("grid");
            updateButtonState();
        };
        reader.readAsDataURL(file);
    };

    input.addEventListener("change", () => {
        showFile(input.files[0]);
        updateButtonState();
    });

    if (textInput) {
        textInput.addEventListener("input", updateButtonState);
    }

    ["dragenter", "dragover"].forEach((eventName) => {
        dropZone.addEventListener(eventName, (event) => {
            event.preventDefault();
            dropZone.classList.add("drag-active");
        });
    });

    ["dragleave", "drop"].forEach((eventName) => {
        dropZone.addEventListener(eventName, (event) => {
            event.preventDefault();
            dropZone.classList.remove("drag-active");
        });
    });

    dropZone.addEventListener("drop", (event) => {
        const file = event.dataTransfer.files[0];
        if (file) {
            input.files = event.dataTransfer.files;
            showFile(file);
        }
    });

    if (form) {
        form.addEventListener("submit", async (event) => {
            event.preventDefault();

            const label = form.querySelector(".button-label");
            const loading = form.querySelector(".button-loading");
            if (label && loading) {
                label.classList.add("hidden");
                loading.classList.remove("hidden");
                loading.classList.add("flex");
            }

            await runStaticConversion({
                file: input.files && input.files[0],
                imageSrc: preview && preview.src,
                text: textInput ? textInput.value.trim() : "",
            });
        });
    }

    updateButtonState();
}

async function runStaticConversion({ file, imageSrc, text }) {
    let sourceText = text;
    let tamilText = "";
    let status = "";
    let imageUrl = imageSrc || "../static/images/sample-document.svg";
    let backendHandled = false;

    // 1) Try the Flask backend first (handles OCR + Magic Loops/Gemini translation server-side)
    if (!isStaticMode()) {
        try {
            const formData = new FormData();
            if (file) {
                formData.append("image", file);
            }
            if (text) {
                formData.append("tanglish_text", text);
            }

            const response = await fetch("/api/convert", {
                method: "POST",
                body: formData
            });

            if (response.ok) {
                const data = await response.json();
                sourceText = data.tanglish_text || data.ocr_text || sourceText;
                tamilText = data.tamil_text || "";
                if (data.image_url) {
                    imageUrl = data.image_url;
                }
                backendHandled = true;
            } else {
                let errMsg = `Server returned status ${response.status}`;
                try {
                    const data = await response.json();
                    errMsg = data.error || errMsg;
                } catch (e) { /* ignore */ }
                tamilText = `Error: ${errMsg}`;
                backendHandled = true;
            }
        } catch (e) {
            console.warn("Flask backend not reachable, using client-side fallback.", e);
        }
    }

    // 2) Client-side fallback (static mode, or backend unreachable): Tesseract OCR + Magic Loops
    if (!backendHandled) {
        if (!sourceText && file) {
            if (!window.Tesseract) {
                status = "Browser OCR library could not load. Type Tanglish text manually and try again.";
            } else {
                try {
                    const result = await window.Tesseract.recognize(file, "eng");
                    sourceText = (result.data.text || "")
                        .replace(/[\r\n]+/g, " ")
                        .replace(/["“”]/g, "")
                        .replace(/\s+/g, " ")
                        .trim();
                    if (!sourceText) {
                        status = "OCR did not find clear text. Type Tanglish text manually for better result.";
                    }
                } catch (error) {
                    status = "Browser OCR failed. Type Tanglish text manually and try again.";
                }
            }
        }

        if (!sourceText) {
            sourceText = "";
        }
        sourceText = sourceText.replace(/[\r\n]+/g, " ").replace(/\s+/g, " ").trim();

        if (sourceText) {
            try {
                const response = await fetch("https://magicloops.dev/api/loop/cfea40be-57cc-4495-ae35-9712d9d52af8/run", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ tanglishText: sourceText })
                });
                if (response.ok) {
                    const data = await response.json();
                    tamilText = data.tamilText || "";
                    if (!tamilText) {
                        tamilText = "Error: Translation service returned an empty result. Try running this via the Flask server (python app.py) for a more reliable Gemini-based translation.";
                    }
                } else {
                    tamilText = `Error: Translation service responded with status ${response.status}. Try running this via the Flask server (python app.py) for a more reliable result.`;
                }
            } catch (err) {
                console.error("Magic Loops translation failed:", err);
                tamilText = "Error: Could not reach the translation service (network blocked or service down). Try running this via the Flask server: python tamilaakkam/flask_api/app.py";
            }
        } else {
            tamilText = "";
        }
    }

    sessionStorage.setItem("tamilaakkamResult", JSON.stringify({
        imageName: file ? file.name : "Typed Text",
        imageSrc: imageUrl,
        tanglishText: sourceText,
        tamilText: tamilText,
        status: status,
    }));

    window.location.href = isStaticMode() ? "result.html" : "/result";
}

function setupStaticResultPage() {
    const saved = sessionStorage.getItem("tamilaakkamResult");
    if (!saved) {
        return;
    }

    let result;
    try {
        result = JSON.parse(saved);
    } catch {
        return;
    }

    const imageName = document.getElementById("imageName");
    const resultImage = document.getElementById("resultImage");
    const tanglishOutput = document.getElementById("tanglishOutput");
    const tamilOutput = document.getElementById("tamilOutput");
    const status = document.getElementById("ocrStatus");

    if (imageName && result.imageName) {
        imageName.textContent = result.imageName;
    }

    if (resultImage && result.imageSrc) {
        resultImage.src = result.imageSrc;
    }

    if (tanglishOutput && result.tanglishText) {
        tanglishOutput.textContent = result.tanglishText;
    }

    if (tamilOutput && result.tamilText) {
        tamilOutput.textContent = result.tamilText;
    }

    if (status && result.status) {
        status.textContent = result.status;
        status.classList.remove("hidden");
    }
}

// Removed injectSettingsUI and setupSettingsModalEvents since API key configuration has been shifted entirely to the backend .env file.

function setupCopyButton() {
    const copyButton = document.querySelector("[data-copy-target]");
    if (!copyButton) {
        return;
    }

    copyButton.addEventListener("click", async () => {
        const target = document.getElementById(copyButton.dataset.copyTarget);
        if (!target) {
            return;
        }

        await navigator.clipboard.writeText(target.textContent.trim());
        const originalText = copyButton.innerHTML;
        copyButton.innerHTML = '<i data-lucide="check" class="h-5 w-5"></i> நகலெடுக்கப்பட்டது';
        window.lucide.createIcons();

        setTimeout(() => {
            copyButton.innerHTML = originalText;
            window.lucide.createIcons();
        }, 1400);
    });
}

function setupDownloadButton() {
    const downloadButton = document.getElementById("downloadText");
    const output = document.getElementById("tamilOutput");

    if (!downloadButton || !output) {
        return;
    }

    downloadButton.addEventListener("click", () => {
        const blob = new Blob([output.textContent.trim()], { type: "text/plain;charset=utf-8" });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = "tamilaakkam-tamil-output.txt";
        link.click();
        URL.revokeObjectURL(url);
    });
}