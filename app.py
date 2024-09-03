from flask import Flask, render_template, request, jsonify
import os
import google.generativeai as genai
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    generation_config=generation_config,
    system_instruction="Give the output in the form of points specifically used for technical education and career guidance in India in a simple and short way and for any program codes try to give it in the form of code snippet with syntax of programming language",
)

history = []

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message")

    if not user_input.strip():
        return jsonify({"response": "Please enter a message."})

    chat_session = model.start_chat(history=history)

    model_response = ""
    try:
        response = chat_session.send_message(user_input)
        for part in response.parts:
            if hasattr(part, "text"):
                model_response += part.text

        # Ensure the response is formatted in points
        if model_response:
            model_response =model_response .replace("**","")
            model_response = model_response.strip().replace("\n", "\n ")

    except Exception as e:
        model_response = "Sorry, I couldn't generate a response due to an error."

    history.append({"role": "user", "parts": [user_input]})
    history.append({"role": "model", "parts": [model_response]})

    return jsonify({"response": model_response})

if __name__ == "__main__":
    app.run(debug=True)
