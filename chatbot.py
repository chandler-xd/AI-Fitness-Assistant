import re

INTENTS = {
    "greeting": {
        "patterns": [
            r"\bhi\b", r"\bhello\b", r"\bhey\b"
        ],
        "response": "Hey! I’m your AI Fitness Assistant. Ask me about workouts, diet, or training tips."
    },

    "beginner": {
        "patterns": [
            r"new to (the )?gym",
            r"first time (at|in) (the )?gym",
            r"beginner",
            r"starting gym",
            r"how do i start"
        ],
        "response": "Start with full-body workouts 3 times a week. Focus on form, light weights, and consistency."
    },

    "muscle_reps": {
        "patterns": [
            r"reps for muscle",
            r"hypertrophy",
            r"muscle gain",
            r"build muscle reps"
        ],
        "response": "For muscle gain, 8–12 reps per set with moderate-to-heavy weight is ideal."
    },

    "strength_reps": {
        "patterns": [
            r"strength reps",
            r"powerlifting",
            r"get strong",
            r"lift heavier"
        ],
        "response": "For strength, train in the 3–6 rep range with heavier weights and longer rest."
    },

    "protein": {
        "patterns": [
            r"protein",
            r"whey",
            r"supplement",
            r"how much protein"
        ],
        "response": "Protein helps repair and build muscle. Aim for about 1.6–2.2g per kg of bodyweight daily. Whey is a convenient option."
    },

    "fat_loss": {
        "patterns": [
            r"fat loss",
            r"cutting",
            r"lose weight",
            r"burn fat"
        ],
        "response": "Fat loss comes from a calorie deficit. Combine strength training, some cardio, and high-protein meals."
    },

    "bulking": {
        "patterns": [
            r"bulk",
            r"bulking",
            r"gain weight",
            r"build mass"
        ],
        "response": "For bulking, eat in a small calorie surplus, train hard, and prioritize compound lifts like squats, presses, and rows."
    },

    "chest_workout": {
        "patterns": [
            r"chest workout",
            r"chest exercises",
            r"train chest"
        ],
        "response": "Chest workout: Bench Press, Incline Dumbbell Press, Chest Flyes, and Push-ups."
    },

    "back_workout": {
        "patterns": [
            r"back workout",
            r"lats",
            r"upper back"
        ],
        "response": "Back workout: Pull-ups or Lat Pulldown, Rows, Face Pulls, and Deadlifts."
    },

    "leg_workout": {
        "patterns": [
            r"leg workout",
            r"legs day",
            r"quads",
            r"hamstrings"
        ],
        "response": "Leg workout: Squats, Leg Press, Lunges, Romanian Deadlifts, and Calf Raises."
    },

    "rest": {
        "patterns": [
            r"rest day",
            r"recovery",
            r"overtraining"
        ],
        "response": "Rest is when muscles grow. Train 3–5 days a week and get 7–9 hours of sleep for best recovery."
    },

    "motivation": {
        "patterns": [
            r"motivate",
            r"tired",
            r"no energy",
            r"feel lazy",
            r"lazy today"
        ],
        "response": "Discipline beats motivation. Show up, even on bad days. Consistency over time changes everything."
    }
}


def clean(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)  # remove punctuation
    return text


def get_response(user_input: str) -> str:
    text = clean(user_input)

    for intent in INTENTS.values():
        for pattern in intent["patterns"]:
            if re.search(pattern, text):
                return intent["response"]

    return (
        "I’m still learning. You can ask me about workouts, bulking, cutting, "
        "protein, reps, recovery, or beginner tips."
    )
