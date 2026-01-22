import re

INTENTS = {
    "greeting": {
        "patterns": ["hi", "hello", "hey"],
        "response": "Hey! I’m your AI Fitness Assistant. Ask me about workouts, diet, or training tips."
    },

    "beginner": {
        "patterns": ["beginner", "start gym", "new to gym", "first time"],
        "response": "Start with full-body workouts 3 times a week. Focus on form, light weights, and consistency."
    },

    "progressive_overload": {
        "patterns": ["progressive overload", "get stronger", "increase weight"],
        "response": "Progressive overload means gradually increasing weight, reps, or intensity so your muscles keep adapting and growing."
    },

    "muscle_reps": {
        "patterns": ["reps for muscle", "hypertrophy", "muscle gain reps"],
        "response": "For muscle gain, 8–12 reps per set with moderate-to-heavy weight is ideal."
    },

    "strength_reps": {
        "patterns": ["strength reps", "powerlifting", "get strong"],
        "response": "For strength, train in the 3–6 rep range with heavier weights and longer rest."
    },

    "protein": {
        "patterns": ["protein", "whey", "supplement"],
        "response": "Protein helps repair and build muscle. Aim for about 1.6–2.2g per kg of bodyweight daily. Whey is a convenient option."
    },

    "fat_loss": {
        "patterns": ["fat loss", "cutting", "lose weight"],
        "response": "Fat loss comes from a calorie deficit. Combine strength training, some cardio, and high-protein meals."
    },

    "bulking": {
        "patterns": ["bulk", "bulking", "gain weight"],
        "response": "For bulking, eat in a small calorie surplus, train hard, and prioritize compound lifts like squats, presses, and rows."
    },

    "chest_workout": {
        "patterns": ["chest workout", "chest exercises"],
        "response": "Chest workout: Bench Press, Incline Dumbbell Press, Chest Flyes, and Push-ups."
    },

    "back_workout": {
        "patterns": ["back workout", "lats", "upper back"],
        "response": "Back workout: Pull-ups or Lat Pulldown, Barbell or Dumbbell Rows, Face Pulls, and Deadlifts."
    },

    "leg_workout": {
        "patterns": ["leg workout", "legs day", "quads", "hamstrings"],
        "response": "Leg workout: Squats, Leg Press, Lunges, Romanian Deadlifts, and Calf Raises."
    },

    "rest": {
        "patterns": ["rest day", "recovery", "overtraining"],
        "response": "Rest is when muscles grow. Train 3–5 days a week and get 7–9 hours of sleep for best recovery."
    },

    "motivation": {
        "patterns": ["motivate", "tired", "no energy", "feel lazy"],
        "response": "Discipline beats motivation. Show up, even on bad days. Consistency over time changes everything."
    }
}

def get_response(user_input):
    text = user_input.lower()

    for intent in INTENTS.values():
        for p in intent["patterns"]:
            if re.search(p, text):
                return intent["response"]

    return (
        "I’m still learning. You can ask me about workouts, bulking, cutting, "
        "protein, reps, recovery, or beginner tips."
    )
