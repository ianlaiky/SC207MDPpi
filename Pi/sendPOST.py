import requests

# URL of the endpoint to send the image to
url = "http://example.com/image"

# Byte object representing the image data
img_data = b'<byte object representing the image data>'

# Set the headers for the request
headers = {
    "Content-Type": "image/jpeg",
}

# Send the image data as a binary stream in the body of the request
response = requests.post(url, headers=headers, data=img_data)

# Check the status code of the response
if response.status_code == 200:
    print("Image sent successfully")
else:
    print("Failed to send image")
