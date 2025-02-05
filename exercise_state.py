from threading import Event
exercise_status={
    "Elbow Up Down":False,
    "Arm Extension":False,
    "Wall Walk Left Hand":False,
    "Standing Leg Front Lift": False,
    "Single Leg Squat":False,
    "Side Leg Raise":False,
    "Side Box Step Ups": False,
    "Front Box Step Ups":False,
    "Step Reaction Training": False,
    "Calf Stretch": False,
    "Hamstring Stretch": False,
    "Partial Wall Squat": False,
    "Seated Knee Extension": False,
}

stop_exercise_event=Event()