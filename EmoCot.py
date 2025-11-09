import json
import requests
from flask import Flask, render_template, request, jsonify
from markdown import markdown

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "GET":
        return render_template("index.html")

    user_message = request.form["message"]

    system_prompt = (
        "You are EmoCo, an AI that ONLY answers questions or requests related to music. "
        "You can discuss topics like genres, artists, chord progressions, instruments, "
        "songwriting, rhythm, or lyrics. "
        "If someone asks about anything unrelated to music, respond with: "
        "'Sorry, I only handle music-related questions!' "
        "You can respond to general courteous things like hello and how are you?"
    )

    try:
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": "llama3",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ]
            },
            stream=True
        )

        full_response = ""
        for line in response.iter_lines():
            if not line:
                continue
            try:
                data = json.loads(line.decode("utf-8"))
                if "message" in data and "content" in data["message"]:
                    full_response += data["message"]["content"]
            except Exception:
                continue

        bot_response = markdown(full_response.strip().replace("\n", "  \n"))

    except Exception as e:
        bot_response = f"(Error contacting Ollama: {e})"

    return jsonify({"response": bot_response})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=True)