from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import requests

app = Flask(__name__)
socketio = SocketIO(app)

API_KEY = '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'  # Your Hugging Face API key
MODEL_ID = 'distilbert-base-uncased-distilled-squad'  # Model for question answering

# Custom keywords and answers mapping
keyword_qa = {
    "fever": "Monitor your temperature, stay hydrated, and rest. If the fever persists for more than a few days or is very high, contact a healthcare professional.",
    "diabetes": "Manage your diabetes by monitoring your blood sugar levels, following a healthy diet, exercising regularly, and taking medications as prescribed.",
    "health": "Stay hydrated, eat a balanced diet rich in fruits and vegetables, exercise regularly, get enough sleep, and manage stress.",
    "headache": "Try resting in a quiet, dark room, stay hydrated, and consider over-the-counter pain relief medications. If headaches persist, consult a doctor.",
    "cold": "Wash your hands frequently, avoid close contact with sick individuals, get vaccinated annually, and maintain a healthy lifestyle.",
    "flu": "Common symptoms include fever, cough, shortness of breath, fatigue, and loss of taste or smell. If you exhibit these symptoms, get tested.",
    "stress": "Practice relaxation techniques such as deep breathing, yoga, meditation, and engage in regular physical activity.",
    "burn": "Cool the burn under running water, cover it with a clean, non-stick bandage, and avoid using ice directly on the burn.",
    "mental health": "Engage in regular physical activity, maintain social connections, eat a balanced diet, get enough sleep, and seek help if needed.",
    "anxiety": "Practice deep breathing, talk to someone you trust, consider mindfulness techniques, and seek professional help if necessary.",
    "sleep": "Establish a regular sleep schedule, create a relaxing bedtime routine, limit screen time before bed, and ensure a comfortable sleep environment.",
    "dehydration": "Dehydration occurs when your body loses more fluids than it takes in. Drink plenty of fluids, especially in hot weather or when exercising.",
    "doctor": "Seek medical advice if you have persistent symptoms, worsening health conditions, or if you're unsure about your health.",
    "exercise": "Regular exercise helps maintain a healthy weight, boosts mental health, improves cardiovascular health, and increases lifespan.",
    "diet": "Include a variety of fruits, vegetables, whole grains, lean proteins, and healthy fats in your diet.",
    "allergy": "Symptoms may include hives, swelling, difficulty breathing, and stomach cramps. Seek medical attention for severe reactions.",
    "UTI": "Symptoms may include a burning sensation when urinating, frequent urge to urinate, and cloudy urine. Drink plenty of water and practice good hygiene.",
    "heart": "Seek immediate medical attention if you experience chest pain, as it can be a sign of a serious condition.",
    "stroke": "Signs include sudden numbness or weakness, confusion, trouble speaking, and severe headache. Seek immediate medical help.",
    "hypertension": "Hypertension, or high blood pressure, is a condition where the force of the blood against the artery walls is too high.",
    "cholesterol": "Cholesterol is a waxy substance found in your blood that is necessary for building cells but can lead to heart disease when levels are too high.",
    "cancer": "Avoid tobacco, maintain a healthy weight, exercise regularly, and get screened as recommended to reduce your risk of developing cancer.",
    "probiotics": "Probiotics are beneficial bacteria that can improve gut health and boost the immune system.",
    "mental health days": "Mental health days allow individuals to take time off to focus on their mental well-being and prevent burnout.",
    "vitamin D": "Spend time in sunlight, eat vitamin D-rich foods, or take supplements if necessary.",
    "chronic pain": "Work with your healthcare provider to develop a pain management plan, including medications and therapy.",
    "autoimmune disease": "An autoimmune disease occurs when the immune system mistakenly attacks healthy cells in the body.",
    "grief": "Allow yourself to feel your emotions, seek support from friends or professionals, and remember that healing takes time.",
    "burnout": "Set realistic goals, take breaks, and seek support from friends or professionals when needed.",
    "yoga": "Yoga improves flexibility, strength, and relaxation while promoting mental well-being.",
    "hydration": "Staying hydrated is essential for bodily functions, including temperature regulation and joint lubrication.",
}

@app.route('/')
def index():
    return render_template('index_socket.html')

@socketio.on('user_message')
def handle_message(data):
    user_message = data['message']
    print(f"Received message: {user_message}")

    # Check for keywords in user message
    response_answer = None
    for keyword, answer in keyword_qa.items():
        if keyword in user_message.lower():
            response_answer = answer
            break

    if response_answer:
        emit('chatbot_reply', {'reply': response_answer})
    else:
        # Improved context for Hugging Face API
        medical_context = (
            "As a medical assistant, provide detailed answers to medical questions. "
            "Your answers should be clear and informative. If the question is about fever, "
            "explain symptoms, monitoring, and when to seek help."
        )

        # Prepare the payload for the Hugging Face model
        payload = {
            "inputs": {
                "question": user_message,
                "context": medical_context  # Providing enhanced context about the task
            }
        }

        headers = {
            "Authorization": f"Bearer {API_KEY}"
        }

        try:
            response = requests.post(f"https://api-inference.huggingface.co/models/{MODEL_ID}", 
                                     headers=headers, json=payload)

            if response.status_code == 200:
                result = response.json()
                answer = result['answer'] if 'answer' in result else "Sorry, I couldn't find an answer to that question."
                
                emit('chatbot_reply', {'reply': answer})
            else:
                emit('chatbot_reply', {'reply': f"API error: {response.status_code} - {response.text}"})

        except Exception as e:
            print(f"Error: {e}")
            emit('chatbot_reply', {'reply': "Sorry, I can't process your request right now."})

if __name__ == '__main__':
    socketio.run(app, debug=True)
