from flask import Flask, request
from ultralytics import YOLO
import cv2

import os

image_symbols = ['1', '2', '3', '4', '5', '6', '7', '8', '9', ' A', ' B', ' Boundary', ' C', ' D', ' E', ' F', ' G',
                 ' H', ' S', ' T', ' U', ' V', ' W', ' X', ' Y', ' Z', ' down', ' left', ' right', ' stop', ' up']

app = Flask(__name__)


def predict():
    from ultralytics import YOLO
    import cv2

    model = YOLO("best.pt")

    # results = model("0.jpg")
    # success = model.export(format="onnx")  # export the model to ONNX format

    # model.predict(source="0.jpg",show=True)

    a = model.predict(source="image/image.jpg")
    for i in a:
        print(i.probs)
        print(i.boxes.cls)
        print(i.boxes.conf)



@app.route("/image", methods=["POST"])
def save_image():
    # Get the binary data of the image from the request
    img_data = request.data

    # Save the image to a directory
    with open("image/image.jpg", "wb") as f:
        f.write(img_data)

    # Return a success status code
    predict()
    return "Image received and saved", 200


@app.route('/')
def index():
    return 'hello'


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
