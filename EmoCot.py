from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "GET":
        return render_template("index.html")

    user_message = request.form["message"]

    # System instruction for EmoCo
    system_prompt = (
        "You are EmoCo, an AI that ONLY answers questions or requests related to music. "
        "You can discuss topics like genres, artists, chord progressions, instruments, "
        "songwriting, rhythm, or lyrics. "
        "If someone asks about anything unrelated to music, respond with: "
        "'Sorry, I only handle music-related questions!'"
        "you can respond to general courteous things like hello and how are you?"
        
    )

    full_prompt = f"{system_prompt}\n\nUser: {user_message}\nEmoCo:"

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "llama3", "prompt": full_prompt},
            stream=True
        )

        # Collect Ollama's streamed response
        full_response = ""
        for line in response.iter_lines():
            if line:
                data = line.decode("utf-8")
                if '"response":"' in data:
                    part = data.split('"response":"')[1].split('"')[0]
                    full_response += part

        # Convert escaped newlines into HTML <br> tags
        bot_response = full_response.strip().replace("\\n", "<br>")

    except Exception as e:
        bot_response = f"(Error contacting Ollama: {e})"

    return jsonify({"response": bot_response})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
