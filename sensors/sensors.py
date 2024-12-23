import RPi.GPIO as GPIO
import time
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub, SubscribeListener
import json
from face_dataset import face_dataset
from face_recognition import face_recognition
from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory
import threading  # Added for synchronization

# Global lock for synchronization
operation_lock = threading.Lock()
photo_taken_recently = False

class Listener(SubscribeListener):
    def status(self, pubnub, status):
        print(f'Status: \n{status.category.name}')


config = PNConfiguration()
config.subscribe_key = "sub-c-d26f2c06-f451-49de-8639-4b3b4c9f6928"
config.publish_key = "pub-c-09ac2b2d-7d42-488c-b044-7c0cd64110b4"
config.secret_key = "sec-c-YjM1NmFjYWtZWRiYi00Y2UzLWIzNjctNjVmOWI5N2ZiMzk2"
config.user_id = "2"

pubnub = PubNub(config)
pubnub.add_listener(Listener())

app_channel = "face_recognition"

subscription = pubnub.channel(app_channel).subscription()
subscription.on_message = lambda message: handle_message(message)
subscription.subscribe()

def handle_message(message):
    global operation_lock, photo_taken_recently

    # Log the raw message for debugging
    print(f"Raw message received: {message.message}")

    try:
        # Ensure the message is parsed into a dictionary
        if isinstance(message.message, str):
            msg = json.loads(message.message)  # Parse string to dictionary
        else:
            msg = message.message

        if "message" in msg:
            msg = msg["message"]

        # Check if the required key exists
        if "take_photo" in msg and msg["take_photo"] == 1:
            if photo_taken_recently:
                print("Photo recently taken, skipping this request.")
                return

            if operation_lock.locked():
                print("Another operation is in progress, skipping take_photo.")
                return

            # Only proceed if photo_taken is 0
            with operation_lock:  # Acquire lock
                print("Processing 'take_photo' request...")
                photo_taken_recently = True  # Set the flag to prevent immediate retries

                publish({
                    "camera_status": 1,
                    "employee_identified": 0,
                    "take_photo": 1,
                    "photo_taken": 0,
                    "employee_id": msg.get("employee_id", None)
                })

                # Call the face_dataset function
                face_dataset(msg["employee_id"])  # Ensure this function is blocking

                # After face_dataset completes, send the update
                publish({
                    "camera_status": 0,
                    "employee_identified": 0,
                    "take_photo": 0,
                    "photo_taken": 1,
                    "employee_id": msg["employee_id"]
                })

                print("Completed 'take_photo' request.")
                
                # Reset the flag after a cooldown period
                threading.Timer(5, reset_photo_taken_flag).start()  # Cooldown for 5 seconds
        else:
            print("Key 'take_photo' not found or value is not 1.")

    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
    except KeyError as e:
        print(f"KeyError: Missing key {e} in the message.")
    except Exception as e:
        print(f"Unexpected error: {e}")




def my_publish_callback(envelope, status):
    # Check whether request successfully completed or not
    if not status.is_error():
        pass
    else:
        pass


class MySubscribeCallback(SubscribeCallback):
    def presense(self, pubnub, presence):
        pass

    def status(self, pubnub, status):
        if status.category == PNStatusCategory.PNUnexpectedDisconnectCategory:
            pass
        elif status.category == PNStatusCategory.PNConnectedCategory:
            print("Connected to channel")
        elif status.category == PNStatusCategory.PNDecryptionErrorCategory:
            pass

    def message(self, pubnub, message):
        print(message.message)


pubnub.add_listener(MySubscribeCallback())


def publish(message):
    pubnub.publish().channel(app_channel).message(message).sync()


PIR_pin = 23
Buzzer_pin = 24

data = {}
data["motion"] = True

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_pin, GPIO.IN)
GPIO.setup(Buzzer_pin, GPIO.OUT)

def main():
    motion_detection()


def reset_photo_taken_flag():
    """Resets the photo_taken_recently flag after a cooldown."""
    global photo_taken_recently
    photo_taken_recently = False
    print("Ready to take photos again.")


def motion_detection():
    global operation_lock

    while True:
        if GPIO.input(PIR_pin) and not operation_lock.locked():
            print("Motion detected")
            # if operation_lock.locked():
            #     print("Another operation is in progress, skipping motion detection.")
            #     time.sleep(1)
            #     continue

            print("Processing motion detection...")
            publish({
                "camera_status": 1,
                "employee_identified": 0,
                "take_photo": 0,
                "photo_taken": 0,
                "employee_id": None
            })

            res = face_recognition()  # Ensure this function is blocking
            if res is not None and "id" in res:
                publish({
                    "camera_status": 0,
                    "employee_identified": 1,
                    "take_photo": 0,
                    "photo_taken": 0,
                    "employee_id": res["id"],
                    "confidence": res["confidence"]
                })

                time.sleep(6)  # Delay to prevent rapid retriggers
                
            print("Completed motion detection.")


def beep(repeat):
    for i in range(repeat):
        for pulse in range(30):
            GPIO.output(Buzzer_pin, True)
            time.sleep(0.001)
            GPIO.output(Buzzer_pin, False)
            time.sleep(0.02)


if __name__ == "__main__":
    main()
