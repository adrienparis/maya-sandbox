import speech_recognition as sr
import pyttsx3

# Initialize the recognizer
r = sr.Recognizer()

# Function to convert text to
# speech
def SpeakText(command):

    # Initialize the engine
    engine = pyttsx3.init()
    engine.say(command)
    engine.runAndWait()
audioFiles = []
audioFiles.append(r"C:\Users\Adrien Paris\Downloads\fifties_fifth_test_complete08.wav")
audioFiles.append(r"C:\Users\Adrien Paris\Downloads\openingbraindamageapplenag02.wav")
audioFiles.append(r"C:\Users\Adrien Paris\Downloads\openingbraindamage05.wav")
audioFiles.append(r"C:\Users\Adrien Paris\Downloads\bw_a4_death_trap01.wav")

for audioFile in audioFiles:
    sr.AudioFile(audioFile)

    # Loop infinitely for user to
    # speak

    # Exception handling to handle
    # exceptions at the runtime
    try:

        # use the microphone as source for input.
        with sr.AudioFile(audioFile) as source2:

            # wait for a second to let the recognizer
            # adjust the energy threshold based on
            # the surrounding noise level
            r.adjust_for_ambient_noise(source2, duration=0.2)

            #listens for the user's input
            audio2 = r.listen(source2)

            # Using google to recognize audio
            MyText = r.recognize_google(audio2)
            MyText = MyText.lower()

            print("Did you say "+MyText)
            SpeakText("Did you say "+MyText + " ?")

    except sr.RequestError as e:
        print("Could not request results; {0}".format(e))

    except sr.UnknownValueError:
        print("unknown error occured")