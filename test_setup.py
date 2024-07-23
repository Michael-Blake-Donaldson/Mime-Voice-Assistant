import speech_recognition as sr

# Initialize the recognizer
recognizer = sr.Recognizer()

# Function to capture and recognize speech
def capture_speech():
    with sr.Microphone() as source:
        print("Please say something")
        # Adjust the recognizer sensitivity to ambient noise
        recognizer.adjust_for_ambient_noise(source)
        # Listen for the first phrase and extract it into audio data
        try:
            audio_data = recognizer.listen(source, timeout=5)
            print("Recognizing...")
            # Recognize speech using Google Web Speech API
            text = recognizer.recognize_google(audio_data)
            print(f"You said: {text}")
        except sr.WaitTimeoutError:
            print("Listening timed out while waiting for phrase to start")
        except sr.UnknownValueError:
            print("Sorry, I did not understand that.")
        except sr.RequestError as e:
            print(f"Could not request results; {e}")

if __name__ == "__main__":
    try:
        capture_speech()
    except Exception as e:
        print(f"An error occurred: {e}")