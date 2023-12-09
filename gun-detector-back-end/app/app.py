from flask import Flask, request, Response
from flask_cors import CORS
import imageio
import tempfile
import cv2
import numpy as np
import imutils

app = Flask(__name__)
CORS(app)

# Certifique-se de ter carregado um classificador Cascade para detecção de armas
gun_cascade = cv2.CascadeClassifier('cascade.xml')

def detect_guns(frame):
    frame = imutils.resize(frame, width=500)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    guns = gun_cascade.detectMultiScale(gray, 1.3, 20, minSize=(100, 100))

    for (x, y, w, h) in guns:
        frame = cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

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
