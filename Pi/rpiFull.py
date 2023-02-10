import io
import cv2
import datetime
import requests


def send_data(data):
    # URL of the endpoint to send the image to
    url = "http://192.168.29.142:8080/image"

    # Byte object representing the image data
    # img_data = b'<byte object representing the image data>'
    img_data = data

    # Set the headers for the request
    headers = {
        "Content-Type": "image/jpeg",
    }

    # Send the image data as a binary stream in the body of the request
    response = requests.post(url, headers=headers, data=img_data)

    # Check the status code of the response
    if response.status_code == 200:
        print("Image sent successfully")
        return True
    else:
        print("Failed to send image")
        return False


def video_feed():
    # Open a connection to the Raspberry Pi camera
    camera = cv2.VideoCapture(0)
    # Get the video stream as a bytes object
    stream = io.BytesIO()
    while True:
        # Read a frame from the camera
        grabbed, frame = camera.read()
        # Break the loop if there are no more frames
        if not grabbed:
            break
        # Encode the frame as JPEG
        ret, jpeg = cv2.imencode('.jpg', frame)
        # Write the JPEG data to the stream
        stream.write(jpeg.tobytes())
        # Reset the stream to the beginning
        stream.seek(0)
        # Return the stream as a response

        return_val = send_data(stream.read())

        if return_val:
            break
        # yield (b'--frame\r\n'
        #        b'Content-Type: image/jpeg\r\n\r\n' + stream.read() + b'\r\n\r\n')
    # Release the camera
    camera.release()

if __name__ == "__main__":
    video_feed()