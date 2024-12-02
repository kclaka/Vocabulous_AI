from doctest import debug

from flask import Flask, render_template, request, jsonify
from openai import AzureOpenAI
import os
from dotenv import load_dotenv

# Azure OpenAI API Configuration
client = AzureOpenAI(
  azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"),
  api_key=os.getenv("API_KEY"),
  api_version="2024-08-01-preview"
)

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html", user_name="Guest")

@app.route("/questions", methods=["POST"])
def questions():
    difficulty = request.form.get("difficulty")
    print("Generating questions for difficulty:", difficulty)
    return render_template("questions.html", difficulty=difficulty)

@app.route("/generate", methods=["POST"])
def generate():
    difficulty = request.json.get("difficulty")
    print("Generating questions for difficulty: 111" , difficulty)
    questions = generate_questions(difficulty)
    return jsonify(questions)



# Generate a list of 10 questions based on difficulty
def generate_questions(difficulty):
    print(f"Generating English sentence completion questions for difficulty: {difficulty}")
    prompt = f"""
    You are an AI assistant tasked with generating a JSON object for an English sentence completion quiz. The quiz is designed for English learners and must contain exactly 10 questions, tailored to the given difficulty level: {difficulty}. Your output must strictly follow the JSON format provided below, without any additional explanations, comments, or conversational text.

    Format:
    {{
      "questions": [
        {{
          "sentence": "<string with a blank>",
          "options": ["<string>", "<string>", "<string>", "<string>"],
          "correct_option": "<string>"
        }},
        ...
      ]
    }}

    ### **Instructions**:
    1. Each question should provide an incomplete sentence with one blank (indicated by `____`).
    2. Offer four answer options, where only one option is correct. The other three options must be plausible but incorrect.
    3. Ensure the sentences and options are appropriate for English learners and match the given difficulty level: "{difficulty}".
    4. Do not include any explanatory text or headers in the response. Return only a valid JSON object in the format below not string.

    ### **Example (for Easy difficulty)**:
    {{
      "questions": [
        {{
          "sentence": "I ___ to the park yesterday.",
          "options": ["go", "went", "going", "gone"],
          "correct_option": "went"
        }},
        {{
          "sentence": "She is ___ a book right now.",
          "options": ["read", "reading", "reads", "readed"],
          "correct_option": "reading"
        }}
      ]
    }}

    ### Task:
    Generate 10 sentence completion questions based on the difficulty level "{difficulty}". Ensure variety in the grammar, vocabulary, and structure of the sentences while maintaining the specified difficulty level. Use the JSON format provided.

    **Repeat Instructions**:
    1. Adhere strictly to the JSON format.
    2. Include 10 questions with plausible but incorrect distractors.
    3. Do not include any explanations or conversational text.
    4. The response must be purely a valid JSON object not string.

    ### Start Generating:
    {{
      "questions": [
        ...
      ]
    }}
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1500,
        temperature=0.7,
    )
    return parse_questions(response.choices[0].message.content)


def parse_questions(response_text):
    """
    Parses the response JSON to extract questions, options, and answers.

    Args:
        response_text (str): JSON response as a string.

    Returns:
        list: A list of dictionaries, each representing a question with sentence, options, and correct_option.
    """
    import json

    try:
        # Preprocess the response text to remove ```json and ``` if present
        if response_text.startswith("```json"):
            response_text = response_text.replace("```json", "").strip()
        if response_text.endswith("```"):
            response_text = response_text.replace("```", "").strip()

        # Load the JSON string into a Python dictionary
        response_json = json.loads(response_text)

        # Extract questions list
        questions = response_json.get("questions", [])


        # Validate structure and data
        parsed_questions = []
        for question in questions:
            sentence = question.get("sentence")
            options = question.get("options", [])
            correct_option = question.get("correct_option")

            # Ensure all necessary keys exist and are valid
            if sentence and len(options) == 4 and correct_option in options:
                parsed_questions.append({
                    "sentence": sentence,
                    "options": options,
                    "correct_option": correct_option
                })
            else:
                print(f"Invalid question format detected: {question}")

        return parsed_questions

    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON: {e}")
        return []


if __name__ == '__main__':
    app.run(debug=True)

