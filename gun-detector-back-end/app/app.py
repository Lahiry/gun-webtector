import cv2
import imutils
import imageio
import tempfile
from flask_cors import CORS
from flask import Flask, request, Response
from inference.models.utils import get_roboflow_model

app = Flask(__name__)
CORS(app)

# Get Roboflow model
model_name = "the-monash-guns-dataset"
model_version = "2"
model_api_key = "bYVwWj1l7c1Nxhk2E2B9"
model = get_roboflow_model(model_id="{}/{}".format(model_name, model_version), api_key=model_api_key)

def detect_guns(frame):
    # Run inference on the frame using the Roboflow model
    results = model.infer(image=frame, confidence=0.5, iou_threshold=0.5)

    if results[0]:
        bounding_box = results[0][0]

        x0, y0, x1, y1 = map(int, bounding_box[:4])
        
        frame = cv2.rectangle(frame, (x0, y0), (x1, y1), (255,255,0), 10)
        frame = cv2.putText(frame, "Gun", (x0, y0 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 2)

    return frame

def convert_to_opencv_compatible_webm(input_filename, output_filename):
    reader = imageio.get_reader(input_filename, 'ffmpeg')
    fps = reader.get_meta_data()['fps']
    writer = imageio.get_writer(output_filename, fps=fps, codec='libvpx-vp9')

    for frame in reader:
        # Aplica a detecção de armas à função
        frame_with_boxes = detect_guns(frame)

        # Verifica e ajusta as dimensões dos frames se necessário
        if frame.shape[0] != frame_with_boxes.shape[0]:
            frame_with_boxes = imutils.resize(frame_with_boxes, height=frame.shape[0])

        # Escreve apenas o frame processado no arquivo de saída
        writer.append_data(frame_with_boxes)
    writer.close()

@app.route('/process_video', methods=['POST'])
def process_video():
    # Recebe o vídeo do formulário
    video_blob = request.files['video']

    # Cria um arquivo temporário para armazenar o vídeo original
    temp_video = tempfile.NamedTemporaryFile(delete=False, suffix=".webm")
    temp_filename = temp_video.name
    temp_video.write(video_blob.read())
    temp_video.close()

    # Converte o vídeo para um formato WebM compatível com o OpenCV
    converted_filename = temp_filename.replace(".webm", "_converted.webm")
    convert_to_opencv_compatible_webm(temp_filename, converted_filename)

    # Retorna o arquivo de saída como resposta
    output_blob = open(converted_filename, 'rb').read()
    return Response(output_blob, mimetype='video/webm')

if __name__ == '__main__':
    app.run(debug=True)

