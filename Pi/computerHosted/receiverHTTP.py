import json

from flask import Flask, request

image_symbols_old = ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'Boundary', 'C', 'D', 'E', 'F', 'G',
                     'H', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'down', 'left', 'right', 'stop', 'up']

image_symbols = ['11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', 'Boundary', '22', '23', '24',
                 '25', '26',
                 '27', '28', '29', '30', '31', '32', '33', '34', '35', '37', '39', '38', '40', '36']

app = Flask(__name__)


def predict():
    from ultralytics import YOLO
    import cv2

    model = YOLO("best.pt")

    # results = model("0.jpg")
    # success = model.export(format="onnx")  # export the model to ONNX format

    # model.predict(source="0.jpg",show=True)

    a = model.predict(source="image/image.jpg", save=True)
    return a
    # for i in a:
    #     print(i.probs)
    #     print(i.boxes.cls)
    #     print(i.boxes.conf)


@app.route("/image", methods=["POST"])
def save_image():
    # Get the binary data of the image from the request
    img_data = request.data

    # Save the image to a directory
    with open("image/image.jpg", "wb") as f:
        f.write(img_data)

    # Return a success status code

    class_data = []
    for i in predict():
        # convert torch.sensor to numpy array
        temp1 = i.boxes.cls.numpy().tolist()
        temp2 = list(i.boxes.conf.numpy().tolist())
        print("in boxes")
        temp3 = i.boxes.xywhn.numpy().tolist()
        print(temp3)
        print("END")
        for index, i in enumerate(temp1):
            temp11 = []
            temp11.append(image_symbols[int(i)])
            temp11.append(temp2[index])
            temp11.append(temp3[index][2] * temp3[index][3])
            class_data.append(temp11)
    if len(class_data) == 0:
        class_data.append([])

    strRep = json.dumps(class_data)
    print(strRep)

    return strRep, 200


@app.route('/')
def index():
    return 'hello'


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
