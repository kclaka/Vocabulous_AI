from flask import Flask, render_template, request, jsonify
from openai import AzureOpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Azure OpenAI API Configuration
client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("API_KEY"),
    api_version="2024-08-01-preview"
)

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/questions", methods=["POST"])
def questions():
    difficulty = request.form.get("difficulty")
    theme = request.form.get("theme")
    article = request.form.get("article", "")
    return render_template("questions.html", difficulty=difficulty, theme=theme, article=article)

@app.route("/generate_questions", methods=["POST"])
def generate_questions_route():
    data = request.get_json()
    difficulty = data.get("difficulty")
    theme = data.get("theme")
    article = data.get("article", "")
    questions = generate_questions(difficulty, theme, article)
    return jsonify({"questions": questions})

def generate_questions(difficulty, theme, article):
    print(f"Generating English sentence completion questions for difficulty: {difficulty}, theme: {theme}")

    # Build the prompt
    prompt = f"""
You are an AI assistant tasked with generating a JSON object for an English sentence completion quiz. The quiz is designed for English learners and must contain exactly 10 questions, tailored to the given difficulty level: "{difficulty}", and the theme: "{theme}". Your output must strictly follow the JSON format provided below, without any additional explanations, comments, or conversational text.

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

### Instructions:
1. Each question should provide an incomplete sentence with one blank (indicated by `____`).
2. Offer four answer options, where only one option is correct. The other three options must be plausible but incorrect.
3. Ensure the sentences and options are appropriate for English learners and match the given difficulty level: "{difficulty}".
4. All sentences and options should relate to the theme: "{theme}".
5. Do not include any explanatory text or headers in the response. Return only a valid JSON object in the format below, not as a string.
"""

    # Include article text if provided
    if article:
        prompt += f"""
Additional Context:
The following text has been provided to base the questions on:
\"\"\"
{article}
\"\"\"

Please ensure that the questions are derived from the content or themes present in this text.
"""
    else:
        prompt += """
If no article text is provided, generate questions based solely on the given theme.
"""

    prompt += """

### Task:
Generate 10 sentence completion questions based on the difficulty level "{difficulty}" and theme "{theme}". Ensure variety in the grammar, vocabulary, and structure of the sentences while maintaining the specified difficulty level. Use the JSON format provided.

**Repeat Instructions**:
1. Adhere strictly to the JSON format.
2. Include 10 questions with plausible but incorrect distractors.
3. Do not include any explanations or conversational text.
4. The response must be purely a valid JSON object, not a string.

### Start Generating:
{
  "questions": [
    ...
  ]
}
"""

    # Make the API call
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
    import json

    try:
        # Clean up the response
        response_text = response_text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:].strip()
        if response_text.endswith("```"):
            response_text = response_text[:-3].strip()

        # Load JSON
        response_json = json.loads(response_text)

        # Extract and validate questions
        questions = response_json.get("questions", [])
        parsed_questions = []
        for question in questions:
            sentence = question.get("sentence")
            options = question.get("options", [])
            correct_option = question.get("correct_option")

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
