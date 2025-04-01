from first_page import db

def add_users():
    users_ref=db.collection("users")

    users_ref.document("user_dd").set({
        "username": "dd",
        "password": "zz",
        "role": "patient"
    })
    
    users_ref.document("user_aa").set({
        "username": "aa",
        "password": "zz",
        "role": "doctor"
    })

def add_doctors():
    doctors_ref= db.collection("doctors")

    doctors_ref.document("doctor_4111").set({
        "email": "dr.raymond@example.com",
        "phone_number": "321-221-331",
        "profession": "Therapist",
        "hospital": "California Hospital",
        "name": "Dr. Raymond Bowers",
        "injury":"Knee Tear",
        "username": "aa"
    })

def add_patients():
    patients_ref=db.collection("patients")
    patients_ref.document("patient_111").set({
        "name": "dd",
        "age": 23,
        "birthdate": "zz",
        "injury": "knee tear",
        "doctor_id": "doctor_4111"
    })

def add_exercises():
    exercises_ref = db.collection("exercises")

    exercises = [
        {"patient_id": "patient_111", "exercise_name": "Elbow Up Down", "date": "2025-03-04", "doctor_id": "doctor_4111", "sets": 2, "reps": 10},
        {"patient_id": "patient_111", "exercise_name": "Standing Leg Front Lift", "date": "2025-03-04", "doctor_id": "doctor_4111", "sets": 2, "reps": 10},
        {"patient_id": "patient_111", "exercise_name": "Side Leg Raise", "date": "2025-03-04", "doctor_id": "doctor_4111", "sets": 2, "reps": 10},
        {"patient_id": "patient_111", "exercise_name": "Side Box Step Ups", "date": "2025-03-05", "doctor_id": "doctor_4111", "sets": 2, "reps": 10},
        {"patient_id": "patient_111", "exercise_name": "Calf Stretch", "date": "2025-03-05", "doctor_id": "doctor_4111", "sets": 2, "reps": 10},
        {"patient_id": "patient_111", "exercise_name": "Single Leg Squat", "date": "2025-03-05", "doctor_id": "doctor_4111", "sets": 2, "reps": 10}
    ]

    for exercise in exercises:
        exercises_ref.add(exercise)

def add_notifications():
    notifications_ref = db.collection("notifications")

    notifications = [
        {"patient_id": "patient_111", "date": "2025-03-04", "type": "Doctor's Feedback", "message": "Keep stretching your knee regularly."},
        {"patient_id": "patient_111", "date": "2025-03-05", "type": "Reminder", "message": "Hydrate well before your next session."},
        {"patient_id": "patient_111", "date": "2025-03-05", "type": "Doctor's Feedback", "message": "Your recovery progress is great!"}
    ]

    for notification in notifications:
        notifications_ref.add(notification)

if __name__ == '__main__':
    add_users()
    add_doctors()
    add_patients()
    add_exercises()
    add_notifications()
    print("Firestore database initialized successfully!")

    
