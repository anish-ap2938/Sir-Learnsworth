import openai
from app.config.config import Config

# Ensure OpenAI API key is set
openai.api_key = Config.OPENAI_API_KEY

def generate_quiz(num_questions, topic, difficulty, knowledge_base):
    """
    Generates a quiz based on user inputs and knowledge base.

    Args:
        num_questions (int): Number of questions to generate.
        topic (str): Topic focus for the quiz.
        difficulty (str): Difficulty level ('easy', 'medium', 'hard').
        knowledge_base (str): Text content from uploaded documents.

    Returns:
        list: A list of quiz questions with options and correct answers.
    """
    prompt = f"""
You are an AI that generates multiple-choice quiz questions.

- Number of Questions: {num_questions}
- Topic: {topic}
- Difficulty Level: {difficulty}
- Knowledge Base: {knowledge_base if knowledge_base else 'None'}

Generate {num_questions} multiple-choice questions on the topic '{topic}' with a difficulty level of '{difficulty}'. Each question should have 4 options (A, B, C, D) with one correct answer. Provide the questions and options in JSON format with the correct answer indicated.

Format:
[
    {{
        "question": "Question text?",
        "options": ["Option A", "Option B", "Option C", "Option D"],
        "correct_answer": "Option A"
    }},
    ...
]
"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": prompt},
            ],
            max_tokens=1500,
            temperature=0.7,
        )

        quiz_content = response['choices'][0]['message']['content'].strip()
        # Parse the generated content into a Python list
        import json
        quiz = json.loads(quiz_content)
        return quiz
    except Exception as e:
        print("Error generating quiz:", e)
        raise e
