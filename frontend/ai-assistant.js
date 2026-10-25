/* ============================================================
   MEDICAI FLOATING AI ASSISTANT
   PHASE 2.3 - DYNAMIC SUGGESTED QUESTIONS
   ============================================================ */

(function () {

    const API_URL = "http://127.0.0.1:8000";

    let assistantOpen = false;
    let isSending = false;
    let latestAnalysisId = null;

    /* ========================================================
       AUTH
       ======================================================== */

    function getToken() {
        return localStorage.getItem("access_token");
    }


    /* ========================================================
       SUGGESTED QUESTIONS
       ======================================================== */

    const questionSets = {

        general: [
            "What does my latest result mean?",
            "What is my confidence score?",
            "What symptoms should I monitor?",
            "What should I discuss with my doctor?",
            "When should I seek urgent medical help?"
        ],

        result: [
            "What does the confidence score mean?",
            "Does this result confirm the condition?",
            "What symptoms should I monitor?",
            "What should I discuss with my doctor?",
            "How is this condition diagnosed?"
        ],

        confidence: [
            "What does the confidence score mean?",
            "Does high AI confidence mean I definitely have the condition?",
            "Why can AI confidence differ from a diagnosis?",
            "What should I discuss with my doctor?",
            "How is this condition diagnosed?"
        ],

        symptoms: [
            "When should I seek urgent medical help?",
            "What symptoms should I monitor?",
            "What should I discuss with my doctor?",
            "How is this condition diagnosed?",
            "What healthy steps can I take now?"
        ],

        doctor: [
            "What information should I tell my doctor?",
            "What questions should I ask my doctor?",
            "What tests might my doctor recommend?",
            "How is this condition diagnosed?",
            "When should I seek urgent medical help?"
        ],

        urgent: [
            "What symptoms require urgent medical attention?",
            "What symptoms should I monitor?",
            "What should I discuss with my doctor?",
            "How is this condition diagnosed?",
            "What healthy steps can I take now?"
        ],

        pneumonia: [
            "What does my pneumonia result mean?",
            "What symptoms should I monitor?",
            "How is pneumonia diagnosed?",
            "What should I discuss with my doctor?",
            "When should I seek urgent medical help?"
        ],

        healthy: [
            "What symptoms should I monitor?",
            "What healthy steps can I take now?",
            "What should I discuss with my doctor?",
            "When should I seek urgent medical help?",
            "How is this condition diagnosed?"
        ]

    };


    let currentQuestionSet = "general";


    /* ========================================================
       CREATE ASSISTANT UI
       ======================================================== */

    function createAssistant() {

        if (document.getElementById("floatingAiAssistant")) {
            return;
        }

        const wrapper = document.createElement("div");

        wrapper.id = "floatingAiAssistant";

        wrapper.innerHTML = `

            <button
                id="aiFloatingButton"
                class="ai-floating-button"
                type="button"
                aria-label="Open MediAI"
            >
                <span class="ai-floating-icon">
                    🤖
                </span>

                <span class="ai-floating-label">
                    MediAI
                </span>
            </button>


            <div
                id="aiAssistantPanel"
                class="ai-assistant-panel"
                aria-hidden="true"
            >

                <div class="ai-assistant-header">

                    <div class="ai-assistant-title">

                        <div class="ai-robot-avatar">
                            🤖
                        </div>

                        <div>

                            <strong>
                                MediAI
                            </strong>

                            <span>
                                Medical AI Assistant
                            </span>

                        </div>

                    </div>


                    <button
                        id="aiCloseButton"
                        class="ai-close-button"
                        type="button"
                        aria-label="Close MediAI"
                    >
                        ×
                    </button>

                </div>


                <div class="ai-status">

                    <span class="ai-status-dot"></span>

                    <span id="aiStatusText">
                        Checking your analysis...
                    </span>

                </div>


                <div
                    id="aiAssistantMessages"
                    class="ai-assistant-messages"
                >

                    <div
                        class="
                            ai-floating-message
                            ai-message-bubble
                        "
                    >

                        <div class="ai-message-avatar">
                            🤖
                        </div>

                        <div class="ai-message-content">

                            <strong>
                                MediAI
                            </strong>

                            <p>
                                Hello! I'm your AI medical
                                assistant. I can help you
                                understand your X-ray
                                analysis and answer
                                general health questions.
                            </p>

                        </div>

                    </div>

                </div>


                <div class="ai-suggested-container">

                    <div class="ai-suggested-title">
                        Suggested questions
                    </div>

                    <div
                        id="aiSuggestedList"
                        class="ai-suggested-list"
                    >
                    </div>

                </div>


                <div class="ai-input-area">

                    <input
                        id="aiAssistantInput"
                        type="text"
                        placeholder="Ask something..."
                        autocomplete="off"
                    >

                    <button
                        id="aiSendButton"
                        class="ai-send-button"
                        type="button"
                        aria-label="Send message"
                    >
                        ➤
                    </button>

                </div>


                <div class="ai-assistant-disclaimer">

                    AI responses are for educational
                    assistance only and are not medical
                    diagnoses.

                </div>

            </div>
        `;


        document.body.appendChild(wrapper);

        setupEvents();

        renderSuggestedQuestions();

        loadLatestAnalysis();
    }


    /* ========================================================
       EVENTS
       ======================================================== */

    function setupEvents() {

        const floatingButton =
            document.getElementById("aiFloatingButton");

        const closeButton =
            document.getElementById("aiCloseButton");

        const sendButton =
            document.getElementById("aiSendButton");

        const input =
            document.getElementById("aiAssistantInput");


        if (floatingButton) {

            floatingButton.addEventListener(
                "click",
                toggleAssistant
            );

        }


        if (closeButton) {

            closeButton.addEventListener(
                "click",
                closeAssistant
            );

        }


        if (sendButton) {

            sendButton.addEventListener(
                "click",
                function () {
                    sendMessage();
                }
            );

        }


        if (input) {

            input.addEventListener(
                "keydown",
                function (event) {

                    if (event.key === "Enter") {

                        event.preventDefault();

                        sendMessage();

                    }

                }
            );

        }

    }


    /* ========================================================
       OPEN / CLOSE ASSISTANT
       ======================================================== */

    function toggleAssistant() {

        if (assistantOpen) {
            closeAssistant();
        } else {
            openAssistant();
        }

    }


    function openAssistant() {

        const panel =
            document.getElementById(
                "aiAssistantPanel"
            );

        const button =
            document.getElementById(
                "aiFloatingButton"
            );


        if (!panel) {
            return;
        }


        assistantOpen = true;


        panel.classList.add(
            "ai-assistant-open"
        );


        panel.setAttribute(
            "aria-hidden",
            "false"
        );


        if (button) {

            button.classList.add(
                "ai-button-open"
            );

        }


        const input =
            document.getElementById(
                "aiAssistantInput"
            );


        if (input) {

            setTimeout(
                function () {
                    input.focus();
                },
                200
            );

        }

    }


    function closeAssistant() {

        const panel =
            document.getElementById(
                "aiAssistantPanel"
            );

        const button =
            document.getElementById(
                "aiFloatingButton"
            );


        if (!panel) {
            return;
        }


        assistantOpen = false;


        panel.classList.remove(
            "ai-assistant-open"
        );


        panel.setAttribute(
            "aria-hidden",
            "true"
        );


        if (button) {

            button.classList.remove(
                "ai-button-open"
            );

        }

    }


    /* ========================================================
       LOAD LATEST ANALYSIS
       ======================================================== */

    async function loadLatestAnalysis() {

        const token = getToken();

        const status =
            document.getElementById(
                "aiStatusText"
            );


        if (!status) {
            return;
        }


        if (!token) {

            status.textContent =
                "Please log in first.";

            return;

        }


        try {

            const response =
                await fetch(
                    `${API_URL}/history`,
                    {
                        method: "GET",

                        headers: {
                            "Authorization":
                                `Bearer ${token}`
                        }
                    }
                );


            if (response.status === 401) {

                status.textContent =
                    "Session expired.";

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


            const historyList = Array.isArray(data)
                ? data
                : (data.history && Array.isArray(data.history) ? data.history : []);

            if (historyList.length > 0) {
                const first = historyList[0];
                latestAnalysisId = first.id || first.analysis_id || null;

                status.textContent =
                    "Analysis available";

            } else {

                latestAnalysisId = null;

                status.textContent =
                    "No analysis available yet";

            }


        } catch (error) {

            console.error(
                "MediAI history error:",
                error
            );


            status.textContent =
                "Analysis status unavailable";

        }

    }


    /* ========================================================
       DETECT QUESTION CATEGORY
       ======================================================== */

    function detectQuestionCategory(question) {

        const text =
            question
                .toLowerCase()
                .trim();


        /* GREETINGS */

        if (
            text === "hi" ||
            text === "hello" ||
            text === "hey" ||
            text === "good morning" ||
            text === "good afternoon" ||
            text === "good evening"
        ) {

            return "general";

        }


        /* URGENT / EMERGENCY */

        if (
            text.includes("urgent") ||
            text.includes("emergency") ||
            text.includes("immediately") ||
            text.includes("severe") ||
            text.includes("emergency help")
        ) {

            return "urgent";

        }


        /* SYMPTOMS */

        if (
            text.includes("symptom") ||
            text.includes("cough") ||
            text.includes("fever") ||
            text.includes("breathing") ||
            text.includes("shortness of breath") ||
            text.includes("chest pain")
        ) {

            return "symptoms";

        }


        /* DOCTOR */

        if (
            text.includes("doctor") ||
            text.includes("physician") ||
            text.includes("healthcare provider") ||
            text.includes("discuss")
        ) {

            return "doctor";

        }


        /* CONFIDENCE */

        if (
            text.includes("confidence") ||
            text.includes("percentage") ||
            text.includes("certainty")
        ) {

            return "confidence";

        }


        /* PNEUMONIA */

        if (
            text.includes("pneumonia")
        ) {

            return "pneumonia";

        }


        /* RESULT */

        if (
            text.includes("result") ||
            text.includes("analysis") ||
            text.includes("x-ray") ||
            text.includes("xray") ||
            text.includes("finding") ||
            text.includes("mean")
        ) {

            return "result";

        }


        /* HEALTH */

        if (
            text.includes("health") ||
            text.includes("healthy") ||
            text.includes("improve") ||
            text.includes("what can i do")
        ) {

            return "healthy";

        }


        return "general";
    }


    /* ========================================================
       UPDATE SUGGESTED QUESTIONS
       ======================================================== */

    function updateSuggestedQuestions(userQuestion) {

        currentQuestionSet =
            detectQuestionCategory(
                userQuestion
            );


        renderSuggestedQuestions();

    }


    /* ========================================================
       RENDER SUGGESTED QUESTIONS
       ======================================================== */

    function renderSuggestedQuestions() {

        const container =
            document.getElementById(
                "aiSuggestedList"
            );


        if (!container) {
            return;
        }


        container.innerHTML = "";


        const questions =
            questionSets[
                currentQuestionSet
            ] ||
            questionSets.general;


        questions.forEach(
            function (question) {

                const button =
                    document.createElement(
                        "button"
                    );


                button.type = "button";


                button.className =
                    "ai-suggested-question";


                button.textContent =
                    question;


                button.addEventListener(
                    "click",
                    function () {

                        sendMessage(
                            question
                        );

                    }
                );


                container.appendChild(
                    button
                );

            }
        );

    }


    /* ========================================================
       SEND MESSAGE
       ======================================================== */

    async function sendMessage(
        suggestedQuestion = null
    ) {

        if (isSending) {
            return;
        }


        const input =
            document.getElementById(
                "aiAssistantInput"
            );


        if (!input) {
            return;
        }


        const question =
            suggestedQuestion ||
            input.value.trim();


        if (!question) {
            return;
        }


        updateSuggestedQuestions(
            question
        );


        if (!latestAnalysisId) {
            latestAnalysisId =
                localStorage.getItem("chat_analysis_id") ||
                window.currentActiveAnalysisId ||
                (window.currentAnalysis && (window.currentAnalysis.id || window.currentAnalysis.analysis_id)) ||
                null;
        }

        if (!latestAnalysisId) {

            await loadLatestAnalysis();

        }

        if (!latestAnalysisId) {
            latestAnalysisId =
                localStorage.getItem("chat_analysis_id") ||
                window.currentActiveAnalysisId ||
                (window.currentAnalysis && (window.currentAnalysis.id || window.currentAnalysis.analysis_id)) ||
                null;
        }

        if (!latestAnalysisId) {

            addAiMessage(
                "I don't currently have an X-ray analysis available for this account. Please upload or analyze an X-ray first."
            );

            return;

        }


        isSending = true;


        const sendButton =
            document.getElementById(
                "aiSendButton"
            );


        if (sendButton) {

            sendButton.disabled = true;

        }


        if (!suggestedQuestion) {

            input.value = "";

        }


        addUserMessage(
            question
        );


        addLoadingMessage();


        try {

            const token =
                getToken();


            if (!token) {

                throw new Error(
                    "Please log in again."
                );

            }


            const activeId = latestAnalysisId ||
                window.currentActiveAnalysisId ||
                localStorage.getItem("chat_analysis_id") ||
                (function() {
                    try {
                        const ca = JSON.parse(localStorage.getItem("current_analysis") || "{}");
                        return ca.id || ca.analysis_id || null;
                    } catch (e) {
                        return null;
                    }
                })();

            if (!activeId) {
                removeLoadingMessage();
                addAiMessage(
                    "Please upload or analyze a chest X-ray first so I can review your scan details and answer your questions."
                );
                return;
            }

            latestAnalysisId = activeId;

            const payload = {
                message: question,
                analysis_id: Number(activeId)
            };

            const response =
                await fetch(
                    `${API_URL}/chat`,
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json",
                            "Authorization":
                                `Bearer ${token}`
                        },

                        body: JSON.stringify(payload)
                    }
                );



            const data =
                await response.json();


            removeLoadingMessage();


            if (response.status === 401) {

                addAiMessage(
                    "Your session has expired. Please log in again."
                );

                return;

            }


            if (!response.ok) {

                throw new Error(
                    data.detail ||
                    "AI assistant failed."
                );

            }


            const answer =
                data.response ||
                data.answer ||
                data.message ||
                data.reply;


            if (!answer) {

                throw new Error(
                    "The AI returned an empty response."
                );

            }


            addAiMessage(
                answer
            );


            updateSuggestedQuestions(
                question
            );

        } catch (error) {

            console.error(
                "MediAI chat error:",
                error
            );


            removeLoadingMessage();


            addAiMessage(
                "Sorry, I could not process your question right now. Please try again."
            );

        } finally {

            isSending = false;


            if (sendButton) {

                sendButton.disabled = false;

            }


            input.focus();

        }

    }


    /* ========================================================
       ADD USER MESSAGE
       ======================================================== */

    function addUserMessage(text) {

        const messages =
            document.getElementById(
                "aiAssistantMessages"
            );


        if (!messages) {
            return;
        }


        const element =
            document.createElement(
                "div"
            );


        element.className =
            "ai-floating-message ai-user-bubble";


        element.innerHTML = `

            <div class="ai-user-content">

                <strong>
                    You
                </strong>

                <p>
                    ${escapeHtml(text)}
                </p>

            </div>

        `;


        messages.appendChild(
            element
        );


        scrollMessages();

    }


    /* ========================================================
       ADD AI MESSAGE
       ======================================================== */

    function addAiMessage(text) {

        const messages =
            document.getElementById(
                "aiAssistantMessages"
            );


        if (!messages) {
            return;
        }


        const element =
            document.createElement(
                "div"
            );


        element.className =
            "ai-floating-message ai-message-bubble";


        element.innerHTML = `

            <div class="ai-message-avatar">
                🤖
            </div>

            <div class="ai-message-content">

                <strong>
                    MediAI
                </strong>

                <div class="ai-response-text">
                    ${formatResponse(text)}
                </div>

            </div>

        `;


        messages.appendChild(
            element
        );


        scrollMessages();

    }


    /* ========================================================
       LOADING / TYPING INDICATOR
       ======================================================== */

    function addLoadingMessage() {

        const messages =
            document.getElementById(
                "aiAssistantMessages"
            );


        if (!messages) {
            return;
        }


        const element =
            document.createElement(
                "div"
            );


        element.id =
            "aiTypingIndicator";


        element.className =
            "ai-floating-message ai-message-bubble";


        element.innerHTML = `

            <div class="ai-message-avatar">
                🤖
            </div>

            <div class="ai-message-content">

                <strong>
                    MediAI
                </strong>

                <div class="ai-typing">

                    <span></span>
                    <span></span>
                    <span></span>

                </div>

            </div>

        `;


        messages.appendChild(
            element
        );


        scrollMessages();

    }


    function removeLoadingMessage() {

        const element =
            document.getElementById(
                "aiTypingIndicator"
            );


        if (element) {

            element.remove();

        }

    }


    /* ========================================================
       FORMAT AI RESPONSE
       ======================================================== */

    function formatResponse(text) {

        let result =
            escapeHtml(
                String(text)
            );


        /* HEADINGS */

        result =
            result.replace(
                /^###\s*(.+)$/gm,
                '<div class="ai-section-heading">$1</div>'
            );


        result =
            result.replace(
                /^##\s*(.+)$/gm,
                '<div class="ai-section-heading">$1</div>'
            );


        result =
            result.replace(
                /^#\s*(.+)$/gm,
                '<div class="ai-section-heading">$1</div>'
            );


        /* BOLD */

        result =
            result.replace(
                /\*\*(.*?)\*\*/g,
                "<strong>$1</strong>"
            );


        /* BULLETS */

        result =
            result.replace(
                /^[\t ]*[\*\-]\s+(.+)$/gm,
                '<div class="ai-bullet">• $1</div>'
            );


        /* NUMBERED LIST */

        result =
            result.replace(
                /^(?!<div class="ai-section-heading">)(\d+)\.\s+(.+)$/gm,
                '<div class="ai-numbered-item"><span>$1.</span> $2</div>'
            );


        /* NEW LINES */

        result =
            result.replace(
                /\r?\n/g,
                "<br>"
            );


        /* EXTRA BREAKS */

        result =
            result.replace(
                /(<br>\s*){3,}/g,
                "<br><br>"
            );


        /* BREAK AFTER HEADING */

        result =
            result.replace(
                /(<div class="ai-section-heading">.*?<\/div>)<br>/g,
                "$1"
            );


        /* BREAK BEFORE BULLET */

        result =
            result.replace(
                /<br>(<div class="ai-bullet">)/g,
                "$1"
            );


        /* BREAK BEFORE NUMBER */

        result =
            result.replace(
                /<br>(<div class="ai-numbered-item">)/g,
                "$1"
            );


        return result;

    }


    /* ========================================================
       ESCAPE HTML
       ======================================================== */

    function escapeHtml(text) {

        const div =
            document.createElement(
                "div"
            );


        div.textContent =
            text;


        return div.innerHTML;

    }


    /* ========================================================
       SCROLL CHAT
       ======================================================== */

    function scrollMessages() {

        const messages =
            document.getElementById(
                "aiAssistantMessages"
            );


        if (!messages) {
            return;
        }


        setTimeout(
            function () {

                messages.scrollTop =
                    messages.scrollHeight;

            },
            50
        );

    }


    /* ========================================================
       INITIALIZE
       ======================================================== */

    function initialize() {

        if (
            document.readyState ===
            "loading"
        ) {

            document.addEventListener(
                "DOMContentLoaded",
                createAssistant
            );

        } else {

            createAssistant();

        }

    }


    initialize();

})();