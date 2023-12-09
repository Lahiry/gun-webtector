import cv2
import imutils
import datetime
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import csv

csv_file_path = 'Log.csv'
gun_cascade = cv2.CascadeClassifier('cascade.xml')
camera = cv2.VideoCapture(0)
fps = camera.get(5) #atributo para pegar fps da câmera
rtlist_size = fps*2 # Por meio de testes, descobrimos que esse tamanho de lista equivale aproximadamente à 5 segundos
last_saved = datetime.datetime.now()-datetime.timedelta(seconds=5)

timestamps = []
weapon_counts = [] 

print(f"Camera FPS: {fps}")

def salva_timestamp(start, finish):
	with open(csv_file_path, mode='a', newline='') as file:
		writer = csv.writer(file)
		date = datetime.datetime.now().strftime("%d %b %Y")
		writer.writerow([date, start, finish])

with open(csv_file_path, mode='w') as file:
		writer = csv.writer(file)
		writer.writerow(["Date", "Start", "End", "File"])

# Função de animação do matplot, para gráficos atualizados em realtime
def animate(i):
	# dentro da funcção de animação do matplot, fazemos a lógica da classificação com OpenCV

	global last_saved
	ret, frame = camera.read()

	if frame is None: #para evitar problemas quando não há captura		
		raise("NAO TEM FRAME")

	################################# PRE PROCCESS ###################################
	frame = imutils.resize(frame, width=500)
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	################################ DETECTION #######################################
	guns = gun_cascade.detectMultiScale(gray, 1.3, 50)

	# Lógica para manter a fila com o tamanho correto
	if len(weapon_counts) == rtlist_size:
		weapon_counts.pop(0)
		timestamps.pop(0)

	if len(guns) > 0:
		weapon_counts.append(1) 
	else:
		weapon_counts.append(0)
	timestamps.append(datetime.datetime.now())		
	
	for (x, y, w, h) in guns:
		frame = cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
		roi_gray = gray[y:y + h, x:x + w]
		roi_color = frame[y:y + h, x:x + w]
	
	cv2.putText(frame, datetime.datetime.now().strftime("%H:%M:%S"),
				(10, frame.shape[0] - 10),
				cv2.FONT_HERSHEY_SIMPLEX,
				0.6, (0, 0, 255), 1)
	
	if np.sum(weapon_counts)/rtlist_size >= 0.5:
		print(f"ARMA DETECTADA ==== > 50% COMO ATIVO")
		if datetime.datetime.now()-last_saved >= datetime.timedelta(seconds=5):
			salva_timestamp(timestamps[0].strftime("%H:%M:%S"), timestamps[-1].strftime("%H:%M:%S"))
			# cv2.imwrite(f"./Imagens/{filename}", frame)
			print("========== SALVO NO LOG ===========")
			last_saved = datetime.datetime.now()
	
	cv2.imshow("Security Feed", frame)

	# Plotting the graph
	plt.cla()
	plt.plot(timestamps, weapon_counts, "b-")
		
	# Verificação se aperta "q" no teclado para interromper a captura
	key = cv2.waitKey(1) & 0xFF
	if key == ord('q'):
		camera.release()
		cv2.destroyAllWindows()
		plt.close(plt.gcf())

# prepara a animação e roda ela com o intervalo variado dado o FPS da camera usada, sendo chamada apenas quando a câmera realmente capturou algo

ani = FuncAnimation(plt.gcf(), animate, interval=(1000/fps), cache_frame_data=False)
plt.tight_layout()
plt.show()

