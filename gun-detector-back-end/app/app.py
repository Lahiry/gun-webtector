import cv2
import imutils
import imageio
import tempfile
from io import BytesIO
from flask_cors import CORS
from datetime import datetime
import matplotlib.pyplot as plt
from flask import Flask, request, Response
from inference.models.utils import get_roboflow_model

app = Flask(__name__)
CORS(app)

# List to store the number of detections per frame
detections_count = []

# List to store the timestamps of each frame
timestamps = []

# Get Roboflow Gun-Detection Model
model_name = "the-monash-guns-dataset"
model_version = "2"
# Replace with your Roboflow API Key
model_api_key = "API_KEY"
model = get_roboflow_model(model_id="{}/{}".format(model_name, model_version), api_key=model_api_key)


# Function to detect guns in a frame
def detect_guns(frame, timestamp):
    # Run inference on the frame using the Roboflow model
    results = model.infer(image=frame, confidence=0.5, iou_threshold=0.5)

    # If there are any detections, draw a bounding box and label each one
    if results[0]:
        for detection in results[0]:
            x0, y0, x1, y1 = map(int, detection[:4])
            
            frame = cv2.rectangle(frame, (x0, y0), (x1, y1), (255, 255, 0), 10)
            frame = cv2.putText(frame, "Gun", (x0, y0 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 2)

        # Append the number of detections to the list
        detections_count.append(len(results[0]))
    else:
        # If there are no detections, append 0 to the list
        detections_count.append(0)

    # Append the timestamp to the list
    timestamps.append(timestamp)

    return frame


# Function to convert a video to a WebM format compatible with OpenCV
def convert_to_opencv_compatible_webm(input_filename, output_filename):
    reader = imageio.get_reader(input_filename, 'ffmpeg')
    fps = reader.get_meta_data()['fps']
    writer = imageio.get_writer(output_filename, fps=fps, codec='libvpx-vp9')

    for i, frame in enumerate(reader):
        # Get frame timestamp
        timestamp = datetime.now().strftime("%H:%M:%S")

        # Apply gun detection to the frame
        frame_with_boxes = detect_guns(frame, timestamp)

        # Resize the frame with bounding boxes to match the original frame size
        if frame.shape[0] != frame_with_boxes.shape[0]:
            frame_with_boxes = imutils.resize(frame_with_boxes, height=frame.shape[0])

        # Write the frame to the output video
        writer.append_data(frame_with_boxes)

    writer.close()


# Route to process the video
@app.route('/process_video', methods=['POST'])
def process_video():
    # Receeive the video formData
    video_blob = request.files['video']

    # Create a temporary file to store the video
    temp_video = tempfile.NamedTemporaryFile(delete=False, suffix=".webm")
    temp_filename = temp_video.name
    temp_video.write(video_blob.read())
    temp_video.close()

    # Convert the video to a WebM format compatible with OpenCV and apply gun detection
    converted_filename = temp_filename.replace(".webm", "_converted.webm")
    convert_to_opencv_compatible_webm(temp_filename, converted_filename)

    # Return the final video to the frontend
    output_blob = open(converted_filename, 'rb').read()
    return Response(output_blob, mimetype='video/webm')


# Route to get the detection graph
@app.route('/get_graph', methods=['GET'])
def get_graph():

    # Creates the graph of detections per timestamp
    plt.plot(timestamps, detections_count)
    plt.xlabel('Horário')
    plt.ylabel('Número de Detecções')
    plt.xticks(rotation=45, ha='right')

    # Save the graph as a PNG image
    buffer = BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    buffer.seek(0)
    plt.close()

    # Return the graph to the frontend
    output_blob = buffer.getvalue()
    return Response(output_blob, mimetype='image/png')


if __name__ == '__main__':
    app.run(debug=True)