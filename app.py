from flask import Flask, render_template, request, send_file
import cv2
import numpy as np
from io import BytesIO
import base64

app = Flask(__name__)

def resize_and_append_to_flex_frame(flex_frame_path, new_image_path):
    # Load the flex frame and resize the new image
    flex_frame = cv2.imread(flex_frame_path)
    new_image = cv2.imread(new_image_path)
    new_image_resized = cv2.resize(new_image, (647, 975))

    # Get dimensions of the flex frame and resized new image
    flex_height, flex_width, _ = flex_frame.shape
    new_image_height, new_image_width, _ = new_image_resized.shape

    # Define the region in the flex frame where the new image will be appended
    start_column = 954
    end_column = start_column + new_image_width

    # Ensure the region is within the flex frame bounds
    end_column = min(end_column, flex_width)

    # Calculate the position to align the resized new image within the specified region
    align_y = 114  # Adjust as needed
    align_x = start_column

    # Create a mask for the resized new image
    new_image_mask = np.ones_like(new_image_resized, dtype=np.uint8) * 255

    # Paste the resized new image onto the flex frame within the specified region
    flex_frame[align_y:align_y + new_image_height, align_x:end_column] = cv2.bitwise_and(new_image_resized, new_image_mask[:, :end_column - align_x, :])

    # Convert the result image to a byte buffer
    _, result_buffer = cv2.imencode('.jpg', flex_frame)

    return BytesIO(result_buffer)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Check if a file is provided in the form
        if 'new_image' in request.files:
            new_image = request.files['new_image']
            
            # Save the uploaded image
            new_image_path = "uploads/new_image.jpg"
            new_image.save(new_image_path)

            # Perform image processing
            result_image_buffer = resize_and_append_to_flex_frame("frame.jpg", new_image_path)

            # Send the result as a response
            return send_file(result_image_buffer, mimetype='image/jpeg')

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
