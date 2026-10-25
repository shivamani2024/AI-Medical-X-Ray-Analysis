# ============================================
# Resend Email Service
# ============================================

import os

import resend

from dotenv import load_dotenv


# ============================================
# Load Environment Variables
# ============================================

load_dotenv()


RESEND_API_KEY = os.getenv(
    "RESEND_API_KEY"
)

if RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY



# ============================================
# Send OTP Email
# ============================================

def send_otp_email(
    recipient_email: str,
    otp: str
):

    subject = (
        "AI Medical Image Analysis - "
        "Password Reset OTP"
    )


    html_body = f"""
    <html>

    <body>

        <h2>
            AI Medical Image Analysis
        </h2>

        <p>
            You requested to reset your password.
        </p>

        <p>
            Your OTP is:
        </p>

        <h1>
            {otp}
        </h1>

        <p>
            This OTP is valid for
            <strong>10 minutes</strong>.
        </p>

        <p>
            If you did not request a password
            reset, please ignore this email.
        </p>

        <br>

        <p>
            Regards,<br>
            AI Medical Image Analysis Team
        </p>

    </body>

    </html>
    """


    params = {

        "from": "AI Medical App <onboarding@resend.dev>",

        "to": [recipient_email],

        "subject": subject,

        "html": html_body

    }


    try:

        response = resend.Emails.send(
            params
        )

        print(
            "OTP email sent successfully!"
        )

        print(
            "Resend response:",
            response
        )

        return response


    except Exception as e:

        print(
            "Resend email error:",
            e
        )

        raise