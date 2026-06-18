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

    setupTabs();
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

let currentTaskType = "tanglish_ocr";

function setupTabs() {
    const tabButtons = {
        "text_translation": document.getElementById("tab-text_translation"),
        "tanglish_ocr": document.getElementById("tab-tanglish_ocr"),
        "general_ocr": document.getElementById("tab-general_ocr")
    };
    const taskTypeInput = document.getElementById("taskTypeInput");
    const dropZone = document.getElementById("dropZone");
    const previewPanel = document.getElementById("previewPanel");
    const textInputGroup = document.getElementById("textInputGroup");
    const convertButton = document.getElementById("convertButton");

    if (!tabButtons["text_translation"]) return;

    const switchTab = (taskType) => {
        currentTaskType = taskType;
        if (taskTypeInput) taskTypeInput.value = taskType;

        // Toggle button active styling
        Object.keys(tabButtons).forEach(key => {
            const btn = tabButtons[key];
            if (!btn) return;
            if (key === taskType) {
                btn.classList.add("bg-deepMaroon", "text-white", "shadow-sm");
                btn.classList.remove("bg-white/80", "text-slate-700");
            } else {
                btn.classList.add("bg-white/80", "text-slate-700");
                btn.classList.remove("bg-deepMaroon", "text-white", "shadow-sm");
            }
        });

        // Hide/Show correct input elements
        const buttonLabel = convertButton.querySelector(".button-label");
        const input = document.getElementById("imageInput");

        if (taskType === "text_translation") {
            if (dropZone) dropZone.classList.add("hidden");
            if (previewPanel) previewPanel.classList.add("hidden");
            if (textInputGroup) textInputGroup.classList.remove("hidden");
            if (buttonLabel) {
                buttonLabel.innerHTML = '<i data-lucide="wand-sparkles" class="h-5 w-5"></i> தமிழ் மொழிபெயர்ப்பு';
            }
        } else if (taskType === "tanglish_ocr") {
            if (dropZone) dropZone.classList.remove("hidden");
            if (input && input.files && input.files.length > 0) {
                if (previewPanel) {
                    previewPanel.classList.remove("hidden");
                    previewPanel.classList.add("grid");
                }
            } else {
                if (previewPanel) previewPanel.classList.add("hidden");
            }
            if (textInputGroup) textInputGroup.classList.remove("hidden");
            if (buttonLabel) {
                buttonLabel.innerHTML = '<i data-lucide="wand-sparkles" class="h-5 w-5"></i> படம் & தமிழ் மாற்றி';
            }
        } else if (taskType === "general_ocr") {
            if (dropZone) dropZone.classList.remove("hidden");
            if (input && input.files && input.files.length > 0) {
                if (previewPanel) {
                    previewPanel.classList.remove("hidden");
                    previewPanel.classList.add("grid");
                }
            } else {
                if (previewPanel) previewPanel.classList.add("hidden");
            }
            if (textInputGroup) textInputGroup.classList.add("hidden");
            if (buttonLabel) {
                buttonLabel.innerHTML = '<i data-lucide="scan-line" class="h-5 w-5"></i> பொது உரை கண்டறி';
            }
        }

        if (window.lucide) {
            window.lucide.createIcons();
        }

        // Refresh convert button disabled state
        const triggerText = document.getElementById("tanglishText");
        const hasFile = input && input.files && input.files.length > 0;
        const hasText = triggerText && triggerText.value.trim().length > 0;

        if (taskType === "text_translation") {
            convertButton.disabled = !hasText;
        } else if (taskType === "tanglish_ocr") {
            convertButton.disabled = !(hasFile || hasText);
        } else if (taskType === "general_ocr") {
            convertButton.disabled = !hasFile;
        }
    };

    Object.keys(tabButtons).forEach(key => {
        const btn = tabButtons[key];
        if (btn) {
            btn.addEventListener("click", () => switchTab(key));
        }
    });

    switchTab("text_translation");
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
        if (currentTaskType === "text_translation") {
            convertButton.disabled = !hasText;
        } else if (currentTaskType === "tanglish_ocr") {
            convertButton.disabled = !(hasFile || hasText);
        } else if (currentTaskType === "general_ocr") {
            convertButton.disabled = !hasFile;
        }
    };

    const showFile = (file) => {
        if (!file || !file.type.startsWith("image/")) {
            return;
        }

        const reader = new FileReader();
        reader.onload = (event) => {
            preview.src = event.target.result;
            fileName.textContent = file.name;
            if (currentTaskType !== "text_translation") {
                previewPanel.classList.remove("hidden");
                previewPanel.classList.add("grid");
            }
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
        event.preventDefault();
        const file = event.dataTransfer.files[0];
        if (file) {
            input.files = event.dataTransfer.files;
            showFile(file);
            updateButtonState();
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
                taskType: currentTaskType
            });
        });
    }

    updateButtonState();
}

async function runStaticConversion({ file, imageSrc, text, taskType = "text_translation" }) {
    let sourceText = text;
    let tamilText = "";
    let status = "";
    let imageUrl = imageSrc || "../static/images/sample-document.svg";
    let backendSuccess = false;

    // Local WASM Tesseract.js fallback function
    const runLocalOcr = async () => {
        if (file && window.Tesseract) {
            try {
                const loadingText = document.querySelector(".button-loading");
                if (loadingText) {
                    loadingText.innerHTML = '<span class="loader"></span> பட உரை கண்டறியப்படுகிறது...';
                }
                const result = await window.Tesseract.recognize(file, "eng");
                return (result.data.text || "").trim();
            } catch (error) {
                console.error("Browser Tesseract OCR failed:", error);
            }
        }
        return "";
    };

    // Submit request to the local Flask backend endpoint
    try {
        const formData = new FormData();
        formData.append("task_type", taskType);
        if (text) {
            formData.append("tanglish_text", text);
        }
        if (file) {
            formData.append("image", file);
        }

        const fetchUrl = isStaticMode() ? "http://127.0.0.1:5000/api/convert" : "/api/convert";
        const response = await fetch(fetchUrl, {
            method: "POST",
            body: formData
        });

        if (response.ok) {
            const data = await response.json();
            sourceText = data.tanglish_text || data.ocr_text || sourceText;
            tamilText = data.tamil_text;
            status = data.ocr_error || status || "";
            if (data.image_url) {
                imageUrl = isStaticMode() && !data.image_url.startsWith("http")
                    ? `http://127.0.0.1:5000${data.image_url}`
                    : data.image_url;
            }
            backendSuccess = true;
        } else {
            try {
                const data = await response.json();
                status = `Backend Error: ${data.error || "Execution failed."}`;
            } catch (err) {
                status = `Backend Error: Status ${response.status}`;
            }
        }
    } catch (e) {
        console.warn("Backend API offline or unreachable. Running offline browser fallback.", e);
        status = "Offline Fallback Mode Active";
    }

    // Client-side execution fallback if the server is offline
    if (!backendSuccess) {
        if (taskType === "text_translation") {
            if (sourceText) {
                // Query serverless Magic Loops translation directly since local backend is offline
                try {
                    const transResp = await fetch("https://magicloops.dev/api/loop/cfea40be-57cc-4495-ae35-9712d9d52af8/run", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ tanglishText: sourceText })
                    });
                    if (transResp.ok) {
                        const transData = await transResp.json();
                        let rawTamil = transData.tamilText || "";
                        if (rawTamil) {
                            tamilText = rawTamil
                                .replace(/நலக்கி/g, "நாளைக்கு")
                                .replace(/செரி/g, "சரி")
                                .replace(/எங்கே/g, "எங்க")
                                .replace(/சரி\s+அஹ்(?!\w)/g, "சரியா?")
                                .replace(/சரி\s+ஆ(?!\w)/g, "சரியா?")
                                .replace(/சரி\s+அ(?!\w)/g, "சரியா?");
                            backendSuccess = true;
                            status = "Server Offline (Serverless Translation Success)";
                        }
                    }
                } catch (e) {
                    console.error("Direct serverless translation failed:", e);
                }

                if (!tamilText) {
                    tamilText = `Error: Local Server Offline.\n\nPlease start the backend server by running:\npython tamilaakkam/flask_api/app.py`;
                }
            } else {
                tamilText = "Error: No text input provided.";
            }
        } else if (taskType === "tanglish_ocr") {
            let textToTranslate = text;
            let usingOcr = false;
            
            if (file) {
                const extracted = await runLocalOcr();
                if (extracted) {
                    textToTranslate = extracted;
                    usingOcr = true;
                }
            }
            
            if (textToTranslate) {
                // Query serverless Magic Loops translation directly since local backend is offline
                try {
                    const transResp = await fetch("https://magicloops.dev/api/loop/cfea40be-57cc-4495-ae35-9712d9d52af8/run", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ tanglishText: textToTranslate })
                    });
                    if (transResp.ok) {
                        const transData = await transResp.json();
                        let rawTamil = transData.tamilText || "";
                        if (rawTamil) {
                            tamilText = rawTamil
                                .replace(/நலக்கி/g, "நாளைக்கு")
                                .replace(/செரி/g, "சரி")
                                .replace(/எங்கே/g, "எங்க")
                                .replace(/சரி\s+அஹ்(?!\w)/g, "சரியா?")
                                .replace(/சரி\s+ஆ(?!\w)/g, "சரியா?")
                                .replace(/சரி\s+அ(?!\w)/g, "சரியா?");
                            backendSuccess = true;
                            status = usingOcr 
                                ? "Server Offline (Browser OCR & Serverless Translation)"
                                : "Server Offline (Serverless Translation Success)";
                        }
                    }
                } catch (e) {
                    console.error("Direct serverless translation failed:", e);
                }

                if (!tamilText) {
                    tamilText = `Error: Local Server Offline.\n\nPlease start the backend server by running:\npython app.py`;
                }
            } else {
                tamilText = "Error: No text or image provided.";
            }
        } else if (taskType === "general_ocr") {
            const extracted = await runLocalOcr();
            if (extracted) {
                sourceText = extracted;
                tamilText = "";
                backendSuccess = true;
                status = "Browser Local OCR Success";
            } else {
                sourceText = "Error: Local OCR failed to read image.";
                tamilText = "";
            }
        }
    }

    sessionStorage.setItem("tamilaakkamResult", JSON.stringify({
        imageName: file ? file.name : "Manual Text Input",
        imageSrc: imageUrl,
        tanglishText: sourceText,
        tamilText: tamilText,
        status: status,
        taskType: taskType
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

    // UI Panels to customize layout
    const imageCard = document.getElementById("imageCardPanel");
    const outputGrid = document.getElementById("resultOutputGrid");
    const tamilOutputCard = document.getElementById("tamilOutputCardPanel");
    const tanglishTitle = document.getElementById("tanglishOutputTitle");

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

    // Adapt layout configuration based on active task type
    const taskType = result.taskType || "tanglish_ocr";

    if (taskType === "text_translation") {
        if (imageCard) imageCard.classList.remove("hidden");
        if (outputGrid) {
            outputGrid.classList.remove("max-w-3xl", "mx-auto");
            outputGrid.classList.add("lg:grid-cols-[0.9fr_1.1fr]");
        }
        if (imageName && (result.imageName === "Manual Text Input" || result.imageName === "Typed Text")) {
            imageName.textContent = "Typed Text";
        }
        if (tamilOutputCard) tamilOutputCard.classList.remove("hidden");
        if (tanglishTitle) tanglishTitle.textContent = "தட்டச்சு செய்த ஆங்கில உரை (Tanglish)";
    } else if (taskType === "tanglish_ocr") {
        if (imageCard) imageCard.classList.remove("hidden");
        if (outputGrid) {
            outputGrid.classList.remove("max-w-3xl", "mx-auto");
            outputGrid.classList.add("lg:grid-cols-[0.9fr_1.1fr]");
        }
        if (tamilOutputCard) tamilOutputCard.classList.remove("hidden");
        if (tanglishTitle) {
            if (result.imageName === "Manual Text Input" || result.imageName === "Typed Text" || !result.imageSrc || result.imageSrc.includes("sample-document")) {
                tanglishTitle.textContent = "தட்டச்சு செய்த ஆங்கில உரை (Tanglish)";
                if (imageName) imageName.textContent = "Typed Text";
            } else {
                tanglishTitle.textContent = "படத்திலிருந்து கண்டறிந்த உரை (Tanglish)";
            }
        }
    } else if (taskType === "general_ocr") {
        if (imageCard) imageCard.classList.remove("hidden");
        if (outputGrid) {
            outputGrid.classList.remove("max-w-3xl", "mx-auto");
            outputGrid.classList.add("lg:grid-cols-[0.9fr_1.1fr]");
        }
        if (tamilOutputCard) tamilOutputCard.classList.add("hidden");
        if (tanglishTitle) tanglishTitle.textContent = "கண்டறியப்பட்ட ஆங்கில உரை (General OCR)";
    }
}

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
