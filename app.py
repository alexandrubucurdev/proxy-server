from flask import Flask, request, jsonify
import requests
import os
import re

app = Flask(__name__)

# Cheia API este luată din variabilele de mediu (NU o scrie aici)
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY nu este setată!")

API_URL = "https://api.openai.com/v1/chat/completions"

@app.route('/solve', methods=['POST'])
def solve():
    data = request.get_json()
    if not data or 'base64' not in data:
        return jsonify({"error": "Missing base64"}), 400

    base64_image = data['base64']

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-4o",  # sau "gpt-4o-mini" dacă vrei costuri mai mici
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Aceasta este o imagine cu o grilă de test. "
                            "Răspunde doar cu litera răspunsului corect (ex: A). "
                            "Nu adăuga alte cuvinte sau explicații."
                        )
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 10,
        "temperature": 0
    }

    try:
        r = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        r.raise_for_status()
        answer = r.json()['choices'][0]['message']['content'].strip()

        # Extrage prima literă de la A la E (sau orice literă mare)
        match = re.search(r'\b([A-E])\b', answer)
        if match:
            return match.group(1)
        # Dacă nu găsește, returnează primul caracter (sperând că e litera)
        return answer[:1] if len(answer) > 0 else "?"

    except requests.exceptions.Timeout:
        return jsonify({"error": "Timeout"}), 504
    except Exception as e:
        print("Eroare:", str(e))
        return jsonify({"error": "Internal error"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=10000)