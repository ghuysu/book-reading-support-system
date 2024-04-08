import pyttsx3

def text_to_speech(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

text = "In the heart of the bustling city, Sarah sat by the window of her favorite café, sipping her steaming cup of coffee. The sunlight filtered through the trees outside, casting dappled shadows on the cobblestone pavement. It was a peaceful moment amidst the urban chaos, and Sarah cherished these quiet mornings before the city fully awakened."
text_to_speech(text)
