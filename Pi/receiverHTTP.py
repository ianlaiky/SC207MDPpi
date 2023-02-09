from flask import Flask, request
import os

app = Flask(__name__)

@app.route("/image", methods=["POST"])
def save_image():
    # Get the binary data of the image from the request
    img_data = request.data

    # Save the image to a directory
    with open("/path/to/image.jpg", "wb") as f:
        f.write(img_data)

    # Return a success status code
    return "Image received and saved", 200

if __name__ == "__main__":
    app.run()