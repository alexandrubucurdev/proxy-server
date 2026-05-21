import os
import re
import google.generativeai as genai
from flask import Flask, request, jsonify

app = Flask(__name__)

# Ia cheia API din variabila de mediu GEMINI_API_KEY (tu ai numit-o GEMINI_API?
# Asigură-te că pe Render ai setat exact numele pe care îl folosești aici)
# Dacă ai numit-o "GEMINI_API", schimbă rândul de mai jos în:
# GEMINI_API_KEY = os.environ.get("GEMINI_API")
GEMINI_API_KEY = os.environ.get("GEMINI_API")  # <-- verifică numele exact!

if not GEMINI_API_KEY:
    raise RuntimeError("Lipsește variabila de mediu GEMINI_API_KEY (sau GEMINI_API)")

# Configurează clientul Gemini
genai.configure(api_key=GEMINI_API_KEY)

# Alege modelul Gemini cu vedere (gemini-1.5-flash e rapid și ieftin)
model = genai.GenerativeModel("gemini-1.5-flash")

@app.route('/solve', methods=['POST'])
def solve():
    data = request.get_json()
    if not data or 'base64' not in data:
        return jsonify({"error": "Missing base64"}), 400

    base64_image = data['base64']

    # Construiește cererea pentru Gemini
    prompt = (
        "Aceasta este o imagine cu o grilă de test. "
        "Răspunde doar cu litera răspunsului corect (ex: A). "
        "Nu adăuga alte cuvinte sau explicații."
    )

    # Pregătește conținutul multimodal (text + imagine)
    # Imaginea e encodată base64, o trimitem ca parte din request
    try:
        response = model.generate_content(
            [
                prompt,
                {"mime_type": "image/jpeg", "data": base64_image}  # Gemini acceptă și base64 direct
            ],
            generation_config={
                "max_output_tokens": 10,
                "temperature": 0
            }
        )

        # Rezolvă răspunsul
        answer = response.text.strip()

        # Extrage prima literă de la A la E (sau orice literă mare)
        match = re.search(r'\b([A-E])\b', answer)
        if match:
            return match.group(1)
        # Dacă nu găsește, returnează primul caracter
        return answer[:1] if len(answer) > 0 else "?"

    except Exception as e:
        print("Eroare Gemini:", str(e))
        return jsonify({"error": "Internal error"}), 500

if __name__ == '__main__':
    # Render va seta variabila PORT; local folosește 10000
    port = int(os.environ.get("PORT", 10000))
    app.run(debug=True, host='0.0.0.0', port=port)