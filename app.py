from flask import Flask, request, jsonify
from bot_logic import get_answer_from_gemini

app = Flask(__name__)

# --- Configuration ---
# Replace with your actual public Google Drive PDF links
PDF_URLS = [
    "https://drive.google.com/file/d/1n9TbyKBxk9EKbwlVpBToNM4AeoM9LCK-/view?usp=sharing",
]

@app.route("/message", methods=["POST"])
def message():
    """
    Endpoint for Kakao i Open Builder 'Skill'.
    """
    try:
        data = request.get_json()
        user_message = data["userRequest"]["utterance"]

        # Call Gemini logic
        answer = get_answer_from_gemini(user_message, PDF_URLS)

        # Prepare KakaoTalk response format
        response = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": answer
                        }
                    }
                ]
            }
        }
        return jsonify(response)

    except Exception as e:
        # Fallback error message
        return jsonify({
            "version": "2.0",
            "template": {
                "outputs": [{"simpleText": {"text": f"?ㅻ쪟 諛쒖깮: {str(e)}"}}]
            }
        })

if __name__ == "__main__":
    # For local testing. Use 'gunicorn' or similar for production.
    app.run(host="0.0.0.0", port=5000)
