import io
import cv2
import datetime
import requests
from src.Logger import Logger
from src.config import WIFI_IP
from src.config import WIFI_PORT

log = Logger()


class Image:
    def __init__(self):
        # start video stream
        log.info("Starting video feed")

        self.camera = None
        self.stream = None

    def send_data(self):
        # URL of the endpoint to send the image to
        url = "http://" + str(WIFI_IP) + ":" + str(WIFI_PORT) + "/image"

        # Byte object representing the image data
        # img_data = b'<byte object representing the image data>'
        img_data = self.stream.read()

        # Set the headers for the request
        headers = {
            "Content-Type": "image/jpeg",
        }

        # Send the image data as a binary stream in the body of the request
        response = requests.post(url, headers=headers, data=img_data)

        # Check the status code of the response
        if response.status_code == 200:
            log.info("Image sent successfully")
            # print(response.text)
            return response.text
        else:
            log.info("Failed to send image")
            return None

    # def start_video_feed(self):
    #     # Open a connection to the Raspberry Pi camera
    #     camera = cv2.VideoCapture(0)
    #     self.camera = camera
    #     # Get the video stream as a bytes object
    #     stream = io.BytesIO()
    #     self.stream = stream

    def capture_frame(self):
        self.camera = cv2.VideoCapture(0)
        self.stream = io.BytesIO()

        log.info("capturing frame")

        while True:

            # Read a frame from the camera
            grabbed, frame = self.camera.read()
            # print(frame)
            # Break the loop if there are no more frames
            if not grabbed:
                break
            # Encode the frame as JPEG
            ret, jpeg = cv2.imencode('.jpg', frame)
            # Write the JPEG data to the stream
            self.stream.write(jpeg.tobytes())

            # Reset the stream to the beginning
            self.stream.seek(0)
            # Return the stream as a response
            # return self.stream.read()

            # return_val = send_data(stream.read())

            # if return_val:
            #     break
            # yield (b'--frame\r\n'
            #        b'Content-Type: image/jpeg\r\n\r\n' + stream.read() + b'\r\n\r\n')

            # Release the camera
            self.camera.release()
