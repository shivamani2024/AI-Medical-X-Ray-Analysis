// ============================================================
// AI MEDICAL IMAGE ANALYSIS
// dashboard.js
// ============================================================


// ============================================================
// API CONFIGURATION
// ============================================================

const API_URL = "http://127.0.0.1:8000";


// ============================================================
// GLOBAL VARIABLES
// ============================================================

let selectedFile = null;

let currentPreviewUrl = null;

let currentAnalysis = null;

let currentUser = null;


// ============================================================
// DOM HELPER
// ============================================================

function getElement(id) {
    return document.getElementById(id);
}


// ============================================================
// AUTHENTICATION
// ============================================================

function getToken() {
    return localStorage.getItem("access_token");
}


function authHeaders() {

    const token = getToken();

    if (!token) {
        return {};
    }

    return {
        "Authorization": `Bearer ${token}`
    };
}


function checkAuthentication() {

    const token = getToken();

    if (!token) {

        window.location.href = "login.html";

        return false;
    }

    return true;
}


// ============================================================
// LOGOUT
// ============================================================

function logout() {

    const token = getToken();

    [
        "access_token",
        "current_user",
        "current_analysis",
        "chat_analysis_id",
        "user_id",
        "patient_id",
        "patientId",
        "patient_name",
        "patientName",
        "patient_email",
        "patientEmail",
        "patientAge",
        "patientGender",
        "patientPhone",
        "patient",
        "user"
    ].forEach(function(key) {
        localStorage.removeItem(key);
    });

    if (token) {
        fetch(`${API_URL}/logout`, {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${token}`
            },
            keepalive: true
        }).catch(function() {});
    }

    currentUser = null;

    currentAnalysis = null;

    selectedFile = null;

    window.location.href = "login.html";
}


// ============================================================
// SAFE HTML
// ============================================================

function escapeHtml(value) {

    if (
        value === null ||
        value === undefined
    ) {
        return "";
    }

    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


// ============================================================
// TEXT HELPER
// ============================================================

function setText(id, value) {

    const element = getElement(id);

    if (element) {
        element.textContent =
            value ?? "-";
    }
}


// ============================================================
// SHOW SECTION
// ============================================================

function showSection(section) {

    const sections = [
        "dashboard",
        "analysis",
        "history",
        "profile",
        "reports"
    ];


    sections.forEach(function(name) {

        const element =
            getElement(
                name + "Section"
            );

        if (element) {

            element.classList.add(
                "hidden"
            );
        }
    });


    const selected =
        getElement(
            section + "Section"
        );


    if (selected) {

        selected.classList.remove(
            "hidden"
        );
    }


    updateNavigation(section);

    updatePageHeader(section);


    // Load section data when needed

    if (section === "history") {
        loadHistory();
    }


    if (section === "profile") {
        loadProfile();
    }


    if (section === "reports") {
        loadReports();
    }
}


// ============================================================
// UPDATE NAVIGATION
// ============================================================

function updateNavigation(section) {

    const navItems =
        document.querySelectorAll(
            ".sidebar-nav .nav-item"
        );


    navItems.forEach(function(item) {

        item.classList.remove(
            "active"
        );
    });


    const mapping = {

        dashboard: 0,

        analysis: 1,

        history: 2,

        profile: 3,

        reports: 4
    };


    const index =
        mapping[section];


    if (
        index !== undefined &&
        navItems[index]
    ) {

        navItems[index]
            .classList.add(
                "active"
            );
    }
}


// ============================================================
// UPDATE PAGE HEADER
// ============================================================

function updatePageHeader(section) {

    const pageTitle =
        getElement("pageTitle");

    const pageSubtitle =
        getElement("pageSubtitle");


    const headers = {

        dashboard: [
            "Dashboard",
            "Your medical analysis overview"
        ],

        analysis: [
            "X-Ray Analysis",
            "AI-assisted chest X-ray classification"
        ],

        history: [
            "Analysis History",
            "Your previous medical analyses"
        ],

        profile: [
            "Patient Profile",
            "Your personal information"
        ],

        reports: [
            "Medical Reports",
            "Your generated analysis reports"
        ]
    };


    const data =
        headers[section];


    if (!data) {
        return;
    }


    if (pageTitle) {

        pageTitle.textContent =
            data[0];
    }


    if (pageSubtitle) {

        pageSubtitle.textContent =
            data[1];
    }
}


// ============================================================
// FILE UPLOAD SETUP
// ============================================================

function setupFileUpload() {

    const fileInput =
        getElement("xrayFile");

    const analyzeButton =
        getElement("analyzeButton");

    const selectedFileText =
        getElement("selectedFile");

    const dropZone =
        getElement("dropZone");


    if (!fileInput) {
        return;
    }


    // --------------------------------------------------------
    // NORMAL FILE SELECTION
    // --------------------------------------------------------

    fileInput.addEventListener(
        "change",
        function() {

            const file =
                fileInput.files[0];


            if (!file) {

                selectedFile = null;

                clearImagePreview();

                if (selectedFileText) {

                    selectedFileText.textContent =
                        "No file selected";
                }

                if (analyzeButton) {

                    analyzeButton.disabled =
                        true;
                }

                return;
            }


            if (!isValidImage(file)) {

                alert(
                    "Please select a valid image file."
                );

                fileInput.value = "";

                selectedFile = null;

                clearImagePreview();

                if (analyzeButton) {

                    analyzeButton.disabled =
                        true;
                }

                return;
            }


            setSelectedFile(file);
        }
    );


    // --------------------------------------------------------
    // DRAG OVER
    // --------------------------------------------------------

    if (dropZone) {

        dropZone.addEventListener(
            "dragover",
            function(event) {

                event.preventDefault();

                dropZone.classList.add(
                    "dragging"
                );
            }
        );


        // ----------------------------------------------------
        // DRAG LEAVE
        // ----------------------------------------------------

        dropZone.addEventListener(
            "dragleave",
            function() {

                dropZone.classList.remove(
                    "dragging"
                );
            }
        );


        // ----------------------------------------------------
        // DROP
        // ----------------------------------------------------

        dropZone.addEventListener(
            "drop",
            function(event) {

                event.preventDefault();

                dropZone.classList.remove(
                    "dragging"
                );


                const files =
                    event.dataTransfer.files;


                if (!files.length) {
                    return;
                }


                const file =
                    files[0];


                if (!isValidImage(file)) {

                    alert(
                        "Please drop a valid image file."
                    );

                    return;
                }


                setSelectedFile(file);
            }
        );
    }
}


// ============================================================
// IMAGE VALIDATION
// ============================================================

function isValidImage(file) {

    if (!file) {
        return false;
    }


    const allowedTypes = [

        "image/jpeg",

        "image/jpg",

        "image/png",

        "image/webp"
    ];


    return allowedTypes.includes(
        file.type
    );
}


// ============================================================
// SET SELECTED FILE
// ============================================================

function setSelectedFile(file) {

    selectedFile = file;


    const selectedFileText =
        getElement("selectedFile");


    const analyzeButton =
        getElement("analyzeButton");


    if (selectedFileText) {

        selectedFileText.textContent =
            file.name;
    }


    if (analyzeButton) {

        analyzeButton.disabled =
            false;
    }


    showImagePreview(file);
}


// ============================================================
// IMAGE PREVIEW
// ============================================================

function showImagePreview(file) {

    const container =
        getElement(
            "imagePreviewContainer"
        );


    if (!container) {
        return;
    }


    if (currentPreviewUrl) {
        URL.revokeObjectURL(currentPreviewUrl);
    }

    currentPreviewUrl = URL.createObjectURL(file);

    const image = document.createElement("img");
    image.className = "xray-preview-image";
    image.alt = "Uploaded chest X-ray preview";
    image.src = currentPreviewUrl;
    image.onerror = function() {
        const errorMessage = document.createElement("p");
        errorMessage.className = "preview-error";
        errorMessage.textContent =
            "This image could not be previewed. Choose a JPG, PNG, or WEBP image.";
        container.replaceChildren(errorMessage);
    };

    container.replaceChildren(image);
}


function clearImagePreview() {

    if (currentPreviewUrl) {
        URL.revokeObjectURL(currentPreviewUrl);
        currentPreviewUrl = null;
    }

    const container = getElement("imagePreviewContainer");

    if (!container) {
        return;
    }

    const placeholder = document.createElement("div");
    placeholder.className = "empty-preview";

    const icon = document.createElement("span");
    icon.setAttribute("aria-hidden", "true");
    icon.textContent = "🖼️";

    const message = document.createElement("p");
    message.textContent = "Your image preview will appear here.";

    placeholder.append(icon, message);
    container.replaceChildren(placeholder);
}


// ============================================================
// ANALYZE X-RAY
// ============================================================

async function analyzeXray() {

    const analyzeButton =
        getElement(
            "analyzeButton"
        );


    if (!selectedFile) {

        showMessage(
            "Please select a chest X-ray first.",
            "error"
        );

        return;
    }


    if (!getToken()) {

        showMessage(
            "Your session has expired. Please login again.",
            "error"
        );

        setTimeout(
            function() {

                window.location.href =
                    "login.html";

            },
            1000
        );

        return;
    }


    if (analyzeButton) {

        analyzeButton.disabled =
            true;

        analyzeButton.textContent =
            "Analyzing...";
    }


    showMessage(
        "AI model is analyzing the X-ray...",
        "info"
    );


    hideElement(
        "resultCard"
    );


    hideElement(
        "gradcamSection"
    );


    const formData =
        new FormData();


    formData.append(
        "file",
        selectedFile
    );


    try {

        console.log(
            "Sending X-ray to:",
            `${API_URL}/predict`
        );


        const response =
            await fetch(
                `${API_URL}/predict`,
                {
                    method: "POST",

                    headers:
                        authHeaders(),

                    body:
                        formData
                }
            );


        // ----------------------------------------------------
        // TOKEN EXPIRED
        // ----------------------------------------------------

        if (
            response.status === 401
        ) {

            logout();

            return;
        }


        // ----------------------------------------------------
        // READ RESPONSE
        // ----------------------------------------------------

        let data;


        try {

            data =
                await response.json();

        } catch (jsonError) {

            throw new Error(
                `Server returned HTTP ${response.status}`
            );
        }


        // ----------------------------------------------------
        // SERVER ERROR
        // ----------------------------------------------------

        if (!response.ok) {

            throw new Error(
                data.detail ||
                data.message ||
                `Server returned HTTP ${response.status}`
            );
        }


        // ----------------------------------------------------
        // SAVE CURRENT ANALYSIS
        // ----------------------------------------------------

        currentAnalysis =
            data;


        localStorage.setItem(
            "current_analysis",
            JSON.stringify(data)
        );


        const analysisId = data.id || data.analysis_id;
        currentActiveAnalysisId = analysisId;
        window.currentActiveAnalysisId = analysisId;
        window.currentAnalysis = data;

        if (analysisId) {

            localStorage.setItem(
                "chat_analysis_id",
                String(
                    analysisId
                )
            );
        }


        // ----------------------------------------------------
        // DISPLAY RESULT
        // ----------------------------------------------------

        displayPredictionResult(
            data
        );


        // ----------------------------------------------------
        // DISPLAY GRAD-CAM
        // ----------------------------------------------------

        displayGradCAM(
            data
        );


        // ----------------------------------------------------
        // SUCCESS
        // ----------------------------------------------------

        showMessage(
            "Analysis completed successfully.",
            "success"
        );


        // ----------------------------------------------------
        // REFRESH DASHBOARD
        // ----------------------------------------------------

        await loadDashboardStats();


    } catch (error) {

        console.error(
            "X-ray analysis error:",
            error
        );


        showMessage(
            error.message ||
            "Unable to analyze the X-ray.",
            "error"
        );


    } finally {

        if (analyzeButton) {

            analyzeButton.disabled =
                false;

            analyzeButton.textContent =
                "Analyze X-Ray";
        }
    }
}


// ============================================================
// ============================================================
// OPACITY SLIDER & LIGHTBOX & SAMPLE LOADERS
// ============================================================

let currentActiveAnalysisId = null;
let currentGradcamBlobUrl = null;

function updateHeatmapOpacity(val) {
    const opacityVal = getElement("opacityVal");
    const gradcamOverlayImg = getElement("gradcamOverlayImg");
    if (opacityVal) opacityVal.textContent = val + "%";
    if (gradcamOverlayImg) gradcamOverlayImg.style.opacity = val / 100;
}

async function loadSampleXray(sampleType) {
    try {
        showMessage(`Loading sample ${sampleType} X-Ray...`, "info");
        const response = await fetch(`${API_URL}/sample-xray/${sampleType}`);
        if (!response.ok) throw new Error("Sample file not found.");
        const blob = await response.blob();

        const filename = `sample_${sampleType}.jpeg`;
        const file = new File([blob], filename, { type: "image/jpeg" });
        selectedFile = file;

        const selectedFileText = getElement("selectedFile");
        const analyzeButton = getElement("analyzeButton");

        showImagePreview(file);

        if (selectedFileText) {
            selectedFileText.textContent = `Selected: ${filename} (Sample ${sampleType.toUpperCase()})`;
        }

        if (analyzeButton) {
            analyzeButton.disabled = false;
        }

        showMessage(`Sample ${sampleType.toUpperCase()} X-Ray loaded. Click 'Predict & Analyze Image' to run!`, "success");
    } catch (err) {
        console.error("Failed to load sample X-ray:", err);
        showMessage("Failed to load sample X-ray. Please choose a local image file.", "error");
    }
}

function openLightboxModal() {
    const modal = getElement("lightboxModal");
    const img = getElement("lightboxImage");
    if (modal && img) {
        const src = currentGradcamBlobUrl || getElement("gradcamOverlayImg")?.src;
        if (src) {
            img.src = src;
            modal.classList.remove("hidden");
        } else {
            alert("No heatmap or X-ray image available for inspection.");
        }
    }
}

function closeLightboxModal(event) {
    if (event && event.target && !event.target.classList.contains("lightbox-modal") && !event.target.classList.contains("lightbox-close")) {
        return;
    }
    const modal = getElement("lightboxModal");
    if (modal) {
        modal.classList.add("hidden");
    }
}

// ============================================================
// DISPLAY PREDICTION RESULT
// ============================================================

function displayPredictionResult(data) {

    currentActiveAnalysisId = data.id || data.analysis_id;
    window.currentActiveAnalysisId = currentActiveAnalysisId;
    window.currentAnalysis = data;

    const resultCard = getElement("resultCard");
    const predictionResult = getElement("predictionResult");
    const confidenceResult = getElement("confidenceResult");
    const confidenceFill = getElement("confidenceFill");
    const filenameResult = getElement("filenameResult");
    const riskBadge = getElement("riskBadge");
    const explanationResult = getElement("explanationResult");
    const gradcamExplanationResult = getElement("gradcamExplanationResult");

    const prediction = (data.prediction || "UNKNOWN").toUpperCase();

    let confidence = Number(data.confidence_percentage ?? data.confidence);

    if (!Number.isNaN(confidence)) {
        if (confidence <= 1) {
            confidence *= 100;
        }
        confidence = Math.max(0, Math.min(100, confidence));
    }

    if (predictionResult) {
        predictionResult.textContent = prediction;
        predictionResult.className = `prediction-badge ${prediction === "PNEUMONIA" ? "prediction-pneumonia" : "prediction-normal"}`;
    }

    if (confidenceResult) {
        confidenceResult.textContent = Number.isNaN(confidence) ? "N/A" : `${confidence.toFixed(1)}%`;
    }

    if (confidenceFill) {
        const fillWidth = Number.isNaN(confidence) ? 0 : confidence;
        confidenceFill.style.width = `${fillWidth}%`;
        confidenceFill.style.background = prediction === "PNEUMONIA"
            ? "linear-gradient(90deg, #f59e0b, #ef4444)"
            : "linear-gradient(90deg, #10b981, #06b6d4)";
    }

    if (filenameResult) {
        filenameResult.textContent = data.image_filename || data.filename || selectedFile?.name || "X-Ray Scan";
    }

    if (riskBadge) {
        if (data.risk_level) {
            riskBadge.textContent = `${data.risk_level} RISK`;
            riskBadge.className = `risk-badge risk-${data.risk_level.toLowerCase()}`;
        } else {
            const risk = prediction === "PNEUMONIA"
                ? (confidence >= 75 ? "HIGH" : "MODERATE")
                : "LOW";
            riskBadge.textContent = `${risk} RISK`;
            riskBadge.className = `risk-badge risk-${risk.toLowerCase()}`;
        }
    }

    if (explanationResult) {
        explanationResult.textContent = data.ai_explanation || data.explanation || "The AI model has completed the X-ray analysis.";
    }

    if (gradcamExplanationResult) {
        gradcamExplanationResult.textContent = data.gradcam_explanation ||
            (prediction === "PNEUMONIA"
                ? `Focal activation highlights lung zones where neural feature maps detected dense opacities and pulmonary consolidations (${confidence.toFixed(1)}% model attention).`
                : `Balanced and diffuse activation pattern across pulmonary fields indicating absence of focal consolidation clusters (${confidence.toFixed(1)}% confidence).`);
    }

    if (resultCard) {
        resultCard.classList.remove("hidden");
        resultCard.scrollIntoView({ behavior: "smooth", block: "start" });
    }

    renderSuggestedQuestions(data);
}


// ============================================================
// DISPLAY GRAD-CAM
// ============================================================

function displayGradCAM(data) {

    const gradcamSection = getElement("gradcamSection");
    const gradcamLoading = getElement("gradcamLoading");
    const gradcamOverlayImg = getElement("gradcamOverlayImg");

    if (!gradcamSection) return;

    const gradcamUrl = data.gradcam_url || data.gradcam_image || data.gradcam;

    if (!gradcamUrl) {
        gradcamSection.classList.add("hidden");
        return;
    }

    gradcamSection.classList.remove("hidden");

    if (gradcamLoading) {
        gradcamLoading.textContent = "Loading Grad-CAM visual attention map...";
        gradcamLoading.style.display = "block";
    }

    const fullUrl = gradcamUrl.startsWith("http") ? gradcamUrl : `${API_URL}${gradcamUrl}`;
    const token = getToken();
    const authenticatedUrl = token
        ? `${fullUrl}${fullUrl.includes("?") ? "&" : "?"}token=${encodeURIComponent(token)}`
        : fullUrl;

    fetch(authenticatedUrl, { headers: authHeaders() })
    .then(function(response) {
        if (!response.ok) throw new Error("HTTP error " + response.status);
        return response.blob();
    })
    .then(function(blob) {
        const objectUrl = URL.createObjectURL(blob);
        currentGradcamBlobUrl = objectUrl;

        if (gradcamOverlayImg) {
            gradcamOverlayImg.src = objectUrl;
            const sliderVal = getElement("opacitySlider")?.value || 75;
            gradcamOverlayImg.style.opacity = sliderVal / 100;
        }

        if (gradcamLoading) {
            gradcamLoading.style.display = "none";
        }
    })
    .catch(function(error) {
        console.error("Grad-CAM load error:", error);
        if (gradcamLoading) {
            gradcamLoading.textContent = "Grad-CAM image load completed.";
            gradcamLoading.style.display = "none";
        }
    });
}


// ============================================================
// MESSAGE
// ============================================================

function showMessage(
    text,
    type = "info"
) {

    const element =
        getElement(
            "analysisMessage"
        );


    if (!element) {
        return;
    }


    element.textContent =
        text;


    element.className =
        `message ${type}`;
}


// ============================================================
// HIDE ELEMENT
// ============================================================

function hideElement(id) {

    const element =
        getElement(id);


    if (element) {

        element.classList.add(
            "hidden"
        );
    }
}


// ============================================================
// SHOW ELEMENT
// ============================================================

function showElement(id) {

    const element =
        getElement(id);


    if (element) {

        element.classList.remove(
            "hidden"
        );
    }
}


// ============================================================
// LOAD PROFILE
// ============================================================

async function loadProfile() {

    try {

        const response =
            await fetch(
                `${API_URL}/me`,
                {
                    method: "GET",

                    headers:
                        authHeaders()
                }
            );


        if (
            response.status === 401
        ) {

            logout();

            return;
        }


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Unable to load profile."
            );
        }


        currentUser =
            data;


        localStorage.setItem(
            "current_user",
            JSON.stringify(data)
        );


        // ----------------------------------------------------
        // HEADER
        // ----------------------------------------------------

        setText(
            "headerName",
            data.name || "Patient"
        );


        setText(
            "headerPatientId",
            data.patient_id || "-"
        );


        // ----------------------------------------------------
        // DASHBOARD
        // ----------------------------------------------------

        setText(
            "welcomeName",
            `Welcome, ${data.name || "Patient"}!`
        );


        setText(
            "dashboardPatientId",
            data.patient_id || "-"
        );


        // ----------------------------------------------------
        // PROFILE
        // ----------------------------------------------------

        setText(
            "profilePatientId",
            data.patient_id || "-"
        );


        setText(
            "profileName",
            data.name || "-"
        );


        setText(
            "profileEmail",
            data.email || "-"
        );


        setText(
            "profileAge",
            data.age ?? "-"
        );


        setText(
            "profileGender",
            data.gender || "-"
        );


        setText(
            "profilePhone",
            data.phone || "-"
        );


    } catch (error) {

        console.error(
            "Profile error:",
            error
        );
    }
}


// ============================================================
// LOAD HISTORY
// ============================================================

async function loadHistory() {

    const container =
        getElement(
            "historyContainer"
        );


    if (!container) {
        return;
    }


    container.innerHTML =
        `
        <div class="loading-card">
            Loading history...
        </div>
        `;


    try {

        const response =
            await fetch(
                `${API_URL}/history`,
                {
                    method: "GET",

                    headers:
                        authHeaders()
                }
            );


        if (
            response.status === 401
        ) {

            logout();

            return;
        }


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Unable to load history."
            );
        }


        const history =
            Array.isArray(data)
                ? data
                : (data.analyses || data.history || []);



        if (!history.length) {

            container.innerHTML =
                `
                <div class="loading-card">
                    No analysis history found.
                </div>
                `;

            return;
        }


        container.innerHTML = "";


        history.forEach(
            function(item) {

                const card =
                    document.createElement(
                        "div"
                    );


                card.className =
                    "dashboard-card";


                let confidence =
                    Number(
                        item.confidence_percentage
                        ??
                        item.confidence
                        ??
                        0
                    );


                if (confidence <= 1) {

                    confidence *= 100;
                }


                const analysisId =
                    item.analysis_id ||
                    item.id;


                const filename =
                    item.filename ||
                    item.image_filename ||
                    "X-ray";


                const date =
                    item.created_at
                        ? new Date(
                            item.created_at
                        ).toLocaleString()
                        : "Unknown date";


                card.innerHTML = `

                    <div class="card-header">

                        <div>

                            <h3>
                                ${escapeHtml(
                                    item.prediction ||
                                    "UNKNOWN"
                                )}
                            </h3>

                            <p>
                                ${escapeHtml(
                                    filename
                                )}
                            </p>

                            <small>
                                ${escapeHtml(
                                    date
                                )}
                            </small>

                        </div>

                        <strong>
                            ${confidence.toFixed(2)}%
                        </strong>

                    </div>


                    ${
                        analysisId
                            ? `
                            <button
                                class="btn btn-outline"
                                type="button"
                                onclick="viewPreviousAnalysis(${analysisId})"
                            >
                                View Analysis
                            </button>
                            `
                            : ""
                    }

                `;


                container.appendChild(
                    card
                );
            }
        );


    } catch (error) {

        console.error(
            "History error:",
            error
        );


        container.innerHTML =
            `
            <div class="message error">
                ${escapeHtml(
                    error.message ||
                    "Unable to load analysis history."
                )}
            </div>
            `;
    }
}


// ============================================================
// VIEW PREVIOUS ANALYSIS
// ============================================================

async function viewPreviousAnalysis(
    analysisId
) {

    if (!analysisId) {
        return;
    }


    try {

        const response =
            await fetch(
                `${API_URL}/analysis/${analysisId}`,
                {
                    method: "GET",

                    headers:
                        authHeaders()
                }
            );


        if (
            response.status === 401
        ) {

            logout();

            return;
        }


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Unable to load analysis."
            );
        }


        currentAnalysis =
            data;


        localStorage.setItem(
            "current_analysis",
            JSON.stringify(data)
        );


        const targetAnalysisId = data.id || data.analysis_id || analysisId;
        currentActiveAnalysisId = targetAnalysisId;
        window.currentActiveAnalysisId = targetAnalysisId;
        window.currentAnalysis = data;

        localStorage.setItem(
            "chat_analysis_id",
            String(
                targetAnalysisId
            )
        );


        showSection(
            "analysis"
        );


        displayPredictionResult(
            data
        );


        displayGradCAM(
            data
        );


        clearChatMessages();


        addChatMessage(
            "This previous analysis is ready. You can ask questions about it.",
            "ai"
        );


    } catch (error) {

        console.error(
            "Previous analysis error:",
            error
        );


        alert(
            error.message ||
            "Unable to load analysis."
        );
    }
}


// ============================================================
// LOAD DASHBOARD STATISTICS
// ============================================================

async function loadDashboardStats() {

    try {

        const response =
            await fetch(
                `${API_URL}/history`,
                {
                    method: "GET",

                    headers:
                        authHeaders()
                }
            );


        if (
            response.status === 401
        ) {

            logout();

            return;
        }


        const data =
            await response.json();


        if (!response.ok) {
            return;
        }


        const history =
            Array.isArray(data)
                ? data
                : (data.analyses || data.history || []);



        setText(
            "totalAnalyses",
            history.length
        );


        if (history.length > 0) {

            setText(
                "latestResult",
                history[0].prediction ||
                "Unknown"
            );
        }
        else {

            setText(
                "latestResult",
                "No analysis"
            );
        }


    } catch (error) {

        console.error(
            "Dashboard statistics error:",
            error
        );
    }
}


async function sendChatMessage(customMessage = null) {

    const chatInput =
        getElement(
            "chatInput"
        );


    const chatMessages =
        getElement(
            "chatMessages"
        );


    if (
        !chatMessages
    ) {
        return;
    }


    const message = (
        customMessage !== null && customMessage !== undefined
            ? customMessage
            : (chatInput ? chatInput.value : "")
    ).trim();


    if (!message) {
        return;
    }


    // --------------------------------------------------------
    // GET ANALYSIS ID
    // --------------------------------------------------------

    const analysisId =
        currentActiveAnalysisId ||
        currentAnalysis?.id ||
        currentAnalysis?.analysis_id ||
        localStorage.getItem(
            "chat_analysis_id"
        ) ||
        (function() {
            try {
                const ca = JSON.parse(localStorage.getItem("current_analysis") || "{}");
                return ca.id || ca.analysis_id || null;
            } catch (e) {
                return null;
            }
        })();


    if (!analysisId) {

        addChatMessage(
            "Please upload or analyze an X-ray first so I can assist you with your results.",
            "ai"
        );

        return;
    }


    // --------------------------------------------------------
    // SHOW USER MESSAGE
    // --------------------------------------------------------

    addChatMessage(
        message,
        "user"
    );


    if (chatInput) {
        chatInput.value = "";
    }


    try {

        const response =
            await fetch(
                `${API_URL}/chat`,
                {
                    method: "POST",

                    headers: {
                        ...authHeaders(),

                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify({

                            analysis_id:
                                Number(
                                    analysisId
                                ),

                            message:
                                message
                        })
                }
            );


        if (
            response.status === 401
        ) {

            logout();

            return;
        }


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                data.message ||
                "Chat request failed."
            );
        }


        addChatMessage(
            data.response ||
            data.message ||
            "No response received.",
            "ai"
        );


    } catch (error) {

        console.error(
            "Chat error:",
            error
        );


        addChatMessage(
            error.message ||
            "Unable to connect to the AI assistant.",
            "ai"
        );
    }
}


// ============================================================
// ADD CHAT MESSAGE
// ============================================================

function addChatMessage(
    message,
    sender
) {

    const container =
        getElement(
            "chatMessages"
        );


    if (!container) {
        return;
    }


    const div =
        document.createElement(
            "div"
        );


    div.className =
        sender === "user"
            ? "user-message"
            : "ai-message";


    const strong =
        document.createElement(
            "strong"
        );


    strong.textContent =
        sender === "user"
            ? "You"
            : "AI Assistant";


    const paragraph =
        document.createElement(
            "p"
        );


    paragraph.textContent =
        message;


    div.appendChild(
        strong
    );


    div.appendChild(
        paragraph
    );


    container.appendChild(
        div
    );


    container.scrollTop =
        container.scrollHeight;
}


// ============================================================
// SUGGESTED QUESTIONS FOR ANALYSIS
// ============================================================

function renderSuggestedQuestions(data = null) {

    const container =
        getElement(
            "chatSuggestionsChips"
        );


    if (!container) {
        return;
    }


    const analysis = data || currentAnalysis;
    const prediction = (analysis?.prediction || "").toUpperCase();
    const confidence = Number(analysis?.confidence_percentage ?? analysis?.confidence);
    const confText = !Number.isNaN(confidence)
        ? (confidence <= 1 ? (confidence * 100).toFixed(1) : confidence.toFixed(1)) + "%"
        : "";

    let questions = [];

    if (prediction === "PNEUMONIA") {
        questions = [
            { icon: "🔍", text: "Explain what the red heatmap zone indicates on this scan" },
            { icon: "📊", text: `What does the ${confText ? confText + ' ' : ''}confidence score mean for Pneumonia?` },
            { icon: "🩺", text: "What specific questions should I ask my doctor about this result?" },
            { icon: "⚠️", text: "What pneumonia symptoms require urgent emergency care?" },
            { icon: "🫁", text: "What causes focal consolidation in lung tissue?" }
        ];
    } else if (prediction === "NORMAL") {
        questions = [
            { icon: "✅", text: "What does a Normal classification indicate for this X-ray?" },
            { icon: "🔍", text: "Why does the Grad-CAM heatmap still show highlights on a normal scan?" },
            { icon: "🩺", text: "When should I consult a doctor if I am still experiencing coughing or fever?" },
            { icon: "🫁", text: "What healthy lifestyle habits best protect lung function?" },
            { icon: "📋", text: "How does the AI model differentiate normal lungs from pneumonia?" }
        ];
    } else {
        questions = [
            { icon: "🩻", text: "How does the AI model analyze chest X-ray scans?" },
            { icon: "🔍", text: "What does the Grad-CAM heatmap overlay represent?" },
            { icon: "🎯", text: "What conditions can this screening assistant detect?" },
            { icon: "🩺", text: "Is this AI classification considered an official medical diagnosis?" }
        ];
    }

    container.innerHTML = "";

    questions.forEach(function(qObj) {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "suggestion-chip";
        btn.innerHTML = `<span class="chip-icon">${qObj.icon}</span> <span>${escapeHtml(qObj.text)}</span>`;
        btn.onclick = function() {
            askSuggestedQuestion(qObj.text);
        };
        container.appendChild(btn);
    });
}

function askSuggestedQuestion(questionText) {
    sendChatMessage(questionText);
}


// ============================================================
// CLEAR CHAT
// ============================================================

function clearChatMessages() {

    const container =
        getElement(
            "chatMessages"
        );


    if (!container) {
        return;
    }


    container.innerHTML = "";
}


// ============================================================
// LOAD REPORTS
// ============================================================

async function loadReports() {

    const container =
        getElement(
            "reportsContainer"
        );


    if (!container) {
        return;
    }


    container.innerHTML =
        `
        <div class="loading-card">
            Loading reports...
        </div>
        `;


    try {

        const response =
            await fetch(
                `${API_URL}/history`,
                {
                    method: "GET",

                    headers:
                        authHeaders()
                }
            );


        if (
            response.status === 401
        ) {

            logout();

            return;
        }


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Unable to load reports."
            );
        }


        const history =
            Array.isArray(data)
                ? data
                : (data.analyses || data.history || []);



        if (!history.length) {

            container.innerHTML =
                `
                <div class="loading-card">
                    No reports available yet.
                </div>
                `;

            return;
        }


        container.innerHTML = "";


        history.forEach(
            function(item) {

                const analysisId =
                    item.analysis_id ||
                    item.id;


                const card =
                    document.createElement(
                        "div"
                    );


                card.className =
                    "dashboard-card";


                card.innerHTML = `

                    <div class="card-header">

                        <div>

                            <h3>
                                Medical AI Analysis Report
                            </h3>

                            <p>
                                ${escapeHtml(
                                    item.filename ||
                                    item.image_filename ||
                                    "X-ray"
                                )}
                            </p>

                            <small>
                                ${
                                    item.created_at
                                        ? escapeHtml(
                                            new Date(
                                                item.created_at
                                            ).toLocaleString()
                                        )
                                        : ""
                                }
                            </small>

                        </div>

                    </div>


                    <button
                        class="btn btn-primary"
                        type="button"
                        onclick="downloadReport(${analysisId})"
                    >
                        Download Report
                    </button>

                `;


                container.appendChild(
                    card
                );
            }
        );


    } catch (error) {

        console.error(
            "Reports error:",
            error
        );


        container.innerHTML =
            `
            <div class="message error">
                ${escapeHtml(
                    error.message ||
                    "Unable to load reports."
                )}
            </div>
            `;
    }
}


// ============================================================
// DOWNLOAD REPORT
// ============================================================

async function downloadReport(
    analysisId
) {

    const targetId = analysisId || currentActiveAnalysisId;

    if (!targetId) {

        alert(
            "No active analysis found. Please run an X-ray analysis first."
        );

        return;
    }


    try {

        const response =
            await fetch(
                `${API_URL}/report/${targetId}`,
                {
                    method: "GET",

                    headers:
                        authHeaders()
                }
            );


        if (
            response.status === 401
        ) {

            logout();

            return;
        }


        if (!response.ok) {

            let message =
                "Unable to download report.";


            try {

                const data =
                    await response.json();


                message =
                    data.detail ||
                    message;

            } catch {
                // Keep default message
            }


            throw new Error(
                message
            );
        }


        const blob =
            await response.blob();


        const url =
            URL.createObjectURL(
                blob
            );


        const link =
            document.createElement(
                "a"
            );


        link.href =
            url;


        link.download =
            `medical_report_${targetId}.html`;



        document.body.appendChild(
            link
        );


        link.click();


        link.remove();


        URL.revokeObjectURL(
            url
        );


    } catch (error) {

        console.error(
            "Report download error:",
            error
        );


        alert(
            error.message ||
            "Unable to download report."
        );
    }
}


// ============================================================
// CHAT ENTER KEY
// ============================================================

function setupChat() {

    const chatInput =
        getElement(
            "chatInput"
        );


    if (!chatInput) {
        return;
    }


    chatInput.addEventListener(
        "keydown",
        function(event) {

            if (
                event.key === "Enter" &&
                !event.shiftKey
            ) {

                event.preventDefault();

                sendChatMessage();
            }
        }
    );
}


// ============================================================
// LOAD SAVED ANALYSIS
// ============================================================

function restoreCurrentAnalysis() {

    const saved =
        localStorage.getItem(
            "current_analysis"
        );


    if (!saved) {
        return;
    }


    try {

        const data =
            JSON.parse(saved);


        if (!data) {
            return;
        }


        currentAnalysis =
            data;


    } catch (error) {

        console.error(
            "Unable to restore analysis:",
            error
        );


        localStorage.removeItem(
            "current_analysis"
        );
    }
}


// ============================================================
// INITIALIZE DASHBOARD
// ============================================================

async function initializeDashboard() {

    // --------------------------------------------------------
    // AUTHENTICATION
    // --------------------------------------------------------

    if (!checkAuthentication()) {
        return;
    }


    // --------------------------------------------------------
    // RESTORE SAVED DATA
    // --------------------------------------------------------

    restoreCurrentAnalysis();


    // --------------------------------------------------------
    // FILE UPLOAD
    // --------------------------------------------------------

    setupFileUpload();


    // --------------------------------------------------------
    // CHAT
    // --------------------------------------------------------

    setupChat();


    // --------------------------------------------------------
    // PROFILE
    // --------------------------------------------------------

    await loadProfile();


    // --------------------------------------------------------
    // DASHBOARD
    // --------------------------------------------------------

    await loadDashboardStats();


    // --------------------------------------------------------
    // DEFAULT SECTION
    // --------------------------------------------------------

    showSection(
        "dashboard"
    );


    // --------------------------------------------------------
    // RESTORE PREVIOUS ANALYSIS
    // --------------------------------------------------------

    if (currentAnalysis) {

        displayPredictionResult(
            currentAnalysis
        );


        displayGradCAM(
            currentAnalysis
        );
    } else {
        renderSuggestedQuestions();
    }
}


// ============================================================
// DOM READY
// ============================================================

document.addEventListener(
    "DOMContentLoaded",
    function() {

        initializeDashboard();

    }
);