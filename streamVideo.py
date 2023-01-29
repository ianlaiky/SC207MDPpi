from flask import Flask, Response, request
import io
import cv2
import datetime

app = Flask(__name__)

@app.route('/video_feed')
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
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + stream.read() + b'\r\n\r\n')
    # Release the camera
    camera.release()

@app.route('/')
def index():
    # Render the HTML template with the video feed URL
    return '''
    <html>
    <head>
        <title>Raspberry Pi Camera</title>
    </head>
    <body>
        <img src="{{ url_for('video_feed') }}">
        <br>
        <button onclick="saveImage()">Save Image</button>
        <script>
            function saveImage() {
                var xhr = new XMLHttpRequest();
                xhr.open("GET", "/save_image", true);
                xhr.send();
                alert("Image saved");
            }
        </script>
    </body>
    </html>
    '''

@app.route('/save_image')
def save_image():
    # Open a connection to the Raspberry Pi camera
    camera = cv2.VideoCapture(0)
    # Read a frame from the camera
    grabbed, frame = camera.read()
    # Generate a file name with the current date and time
    now = datetime.datetime.now()
    file_name = now.strftime('image_%Y%m%d_%H%M%S.jpg')
    # Save the frame as an image file
    cv2.imwrite(file_name, frame)
    # Release the camera
    camera.release()
    # Return an empty response
    return Response(status=204)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
