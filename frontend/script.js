// ============================================
// AI Medical Image Analysis - Frontend
// ============================================

const API_URL = "https://ai-medical-x-ray-analysis-1.onrender.com";

const USER_SESSION_KEYS = [
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
];

function clearUserSession() {
    USER_SESSION_KEYS.forEach(function(key) {
        localStorage.removeItem(key);
    });
}


// ============================================
// REGISTER
// ============================================

const registerForm =
    document.getElementById("registerForm");

if (registerForm) {

    registerForm.addEventListener(
        "submit",
        async function (event) {

            event.preventDefault();

            const message =
                document.getElementById("registerMessage");

            // ========================================
            // GET FORM VALUES
            // ========================================

            const name =
                document.getElementById("name").value.trim();

            const email =
                document.getElementById("email").value.trim();

            const password =
                document.getElementById("password").value;

            const age =
                document.getElementById("age").value;

            const gender =
                document.getElementById("gender").value;

            const phone =
                document.getElementById("phone").value.trim();


            // ========================================
            // VALIDATION
            // ========================================

            if (!name) {

                message.textContent =
                    "Please enter your full name.";

                message.className =
                    "message error";

                return;
            }


            if (!email) {

                message.textContent =
                    "Please enter your email.";

                message.className =
                    "message error";

                return;
            }


            if (!password) {

                message.textContent =
                    "Please enter your password.";

                message.className =
                    "message error";

                return;
            }


            if (password.length < 8) {

                message.textContent =
                    "Password must contain at least 8 characters.";

                message.className =
                    "message error";

                return;
            }


            if (!age) {

                message.textContent =
                    "Please enter your age.";

                message.className =
                    "message error";

                return;
            }


            if (!gender) {

                message.textContent =
                    "Please select your gender.";

                message.className =
                    "message error";

                return;
            }


            if (!phone) {

                message.textContent =
                    "Please enter your phone number.";

                message.className =
                    "message error";

                return;
            }


            try {

                message.textContent =
                    "Creating your account...";

                message.className =
                    "message";


                // ========================================
                // REGISTER REQUEST
                // ========================================

                const response =
                    await fetch(
                        `${API_URL}/register`,
                        {
                            method: "POST",

                            headers: {
                                "Content-Type":
                                    "application/json",

                                "Accept":
                                    "application/json"
                            },

                            body: JSON.stringify({

                                name: name,

                                email: email,

                                password: password,

                                age: parseInt(age),

                                gender: gender,

                                phone: phone

                            })
                        }
                    );


                // ========================================
                // READ RESPONSE
                // ========================================

                const data =
                    await response.json();


                console.log(
                    "Registration HTTP status:",
                    response.status
                );


                // ========================================
                // REGISTRATION ERROR
                // ========================================

                if (!response.ok) {

                    let errorMessage =
                        "Registration failed.";


                    // FastAPI string error
                    if (
                        typeof data.detail ===
                        "string"
                    ) {

                        errorMessage =
                            data.detail;

                    }


                    // FastAPI validation errors
                    else if (
                        Array.isArray(data.detail)
                    ) {

                        errorMessage =
                            data.detail
                                .map(
                                    item =>
                                        item.msg ||
                                        JSON.stringify(item)
                                )
                                .join(", ");

                    }


                    // Backend object error
                    else if (
                        data.detail &&
                        typeof data.detail ===
                        "object"
                    ) {

                        errorMessage =
                            data.detail.message ||
                            data.detail.error ||
                            data.detail.detail ||
                            JSON.stringify(
                                data.detail
                            );

                    }


                    // Backend message
                    else if (
                        data.message
                    ) {

                        errorMessage =
                            typeof data.message ===
                            "string"
                                ? data.message
                                : JSON.stringify(
                                    data.message
                                );

                    }


                    // Backend error
                    else if (
                        data.error
                    ) {

                        errorMessage =
                            typeof data.error ===
                            "string"
                                ? data.error
                                : JSON.stringify(
                                    data.error
                                );

                    }


                    message.textContent =
                        errorMessage;

                    message.className =
                        "message error";

                    return;
                }


                // ========================================
                // SUCCESS
                // ========================================

                clearUserSession();

                message.textContent =
                    `Registration successful! Your Patient ID is ${data.patient_id}`;

                message.className =
                    "message success";


                // ========================================
                // REDIRECT TO LOGIN
                // ========================================

                setTimeout(
                    function () {

                        window.location.href =
                            "login.html";

                    },
                    2000
                );


            }

            catch (error) {

                console.error(
                    "Registration error:",
                    error
                );


                message.textContent =
                    "Unable to connect to the backend.";

                message.className =
                    "message error";

            }

        }
    );

}


// ============================================
// LOGIN
// ============================================

const loginForm =
    document.getElementById("loginForm");


if (loginForm) {

    loginForm.addEventListener(
        "submit",
        async function (event) {

            event.preventDefault();


            const message =
                document.getElementById(
                    "loginMessage"
                );


            const email =
                document.getElementById(
                    "loginEmail"
                ).value.trim();


            const password =
                document.getElementById(
                    "loginPassword"
                ).value;


            // ========================================
            // VALIDATION
            // ========================================

            if (!email) {

                message.textContent =
                    "Please enter your email.";

                message.className =
                    "message error";

                return;
            }


            if (!password) {

                message.textContent =
                    "Please enter your password.";

                message.className =
                    "message error";

                return;
            }


                try {

                    clearUserSession();

                message.textContent =
                    "Signing in...";

                message.className =
                    "message";


                // ========================================
                // LOGIN REQUEST
                // ========================================

                const response =
                    await fetch(
                        `${API_URL}/login`,
                        {
                            method: "POST",

                            headers: {

                                "Content-Type":
                                    "application/json",

                                "Accept":
                                    "application/json"

                            },

                            body:
                                JSON.stringify({

                                    email:
                                        email,

                                    password:
                                        password,

                                    remember_me:
                                        document.getElementById("rememberMe")?.checked ?? true

                                })

                        }
                    );


                // ========================================
                // READ RESPONSE
                // ========================================

                const data =
                    await response.json();


                console.log(
                    "Login HTTP status:",
                    response.status
                );


                // ========================================
                // LOGIN ERROR
                // ========================================

                if (!response.ok) {

                    let errorMessage =
                        "Login failed.";


                    // Backend returned string
                    if (
                        typeof data.detail ===
                        "string"
                    ) {

                        errorMessage =
                            data.detail;

                    }


                    // FastAPI validation errors
                    else if (
                        Array.isArray(data.detail)
                    ) {

                        errorMessage =
                            data.detail
                                .map(
                                    item =>
                                        item.msg ||
                                        JSON.stringify(item)
                                )
                                .join(", ");

                    }


                    // Backend returned object
                    else if (
                        data.detail &&
                        typeof data.detail ===
                        "object"
                    ) {

                        errorMessage =
                            data.detail.message ||
                            data.detail.error ||
                            data.detail.detail ||
                            JSON.stringify(
                                data.detail
                            );

                    }


                    // Backend returned message
                    else if (
                        data.message
                    ) {

                        errorMessage =
                            typeof data.message ===
                            "string"
                                ? data.message
                                : JSON.stringify(
                                    data.message
                                );

                    }


                    // Backend returned error
                    else if (
                        data.error
                    ) {

                        errorMessage =
                            typeof data.error ===
                            "string"
                                ? data.error
                                : JSON.stringify(
                                    data.error
                                );

                    }


                    message.textContent =
                        errorMessage;

                    message.className =
                        "message error";

                    return;
                }


                // ========================================
                // CHECK TOKEN
                // ========================================

                if (
                    !data.access_token
                ) {

                    message.textContent =
                        "Login response did not contain an access token.";

                    message.className =
                        "message error";

                    return;
                }


                // ========================================
                // GET PATIENT
                // ========================================

                const patient =
                    data.patient || data.user || {};


                // ========================================
                // SAVE ACCESS TOKEN & PROFILE
                // ========================================

                localStorage.setItem(
                    "access_token",
                    data.access_token
                );

                localStorage.setItem(
                    "user_id",
                    String(patient.id || "")
                );

                localStorage.setItem(
                    "patient_id",
                    patient.patient_id || ""
                );

                localStorage.setItem(
                    "patientId",
                    patient.patient_id || ""
                );

                localStorage.setItem(
                    "patient_name",
                    patient.name || ""
                );

                localStorage.setItem(
                    "patientName",
                    patient.name || ""
                );

                localStorage.setItem(
                    "patient_email",
                    patient.email || ""
                );

                localStorage.setItem(
                    "patientEmail",
                    patient.email || ""
                );

                if (patient.age) {
                    localStorage.setItem("patientAge", String(patient.age));
                }

                if (patient.gender) {
                    localStorage.setItem("patientGender", patient.gender);
                }

                if (patient.phone) {
                    localStorage.setItem("patientPhone", patient.phone);
                }

                localStorage.setItem(
                    "patient",
                    JSON.stringify(patient)
                );

                localStorage.setItem(
                    "user",
                    JSON.stringify(patient)
                );

                localStorage.setItem(
                    "current_user",
                    JSON.stringify(patient)
                );



                // ========================================
                // LOGIN SUCCESS
                // ========================================

                message.textContent =
                    "Login successful!";

                message.className =
                    "message success";


                // ========================================
                // REDIRECT
                // ========================================

                setTimeout(
                    function () {

                        window.location.href =
                            "welcome.html";

                    },
                    1000
                );


            }

            catch (error) {

                console.error(
                    "Login error:",
                    error
                );


                message.textContent =
                    "Unable to connect to the backend.";

                message.className =
                    "message error";

            }

        }
    );

}


// ============================================
// END OF SCRIPT.JS
// ============================================