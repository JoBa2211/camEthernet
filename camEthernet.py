import socket
import cv2

import tkinter as tk

def main():
	from PIL import Image, ImageTk

	ventana = tk.Tk()
	frame_controles = tk.Frame(ventana)
	frame_controles.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

	# Usar un frame interno para centrar y limitar el ancho
	frame_interno = tk.Frame(frame_controles)
	frame_interno.pack(anchor="center")
	frame_main = tk.Frame(ventana)
	# IP local
	tk.Label(frame_interno, text="IP local:").grid(row=0, column=0, sticky="e", padx=2)
	entry_ip_local = tk.Entry(frame_interno, width=15)
	entry_ip_local.grid(row=0, column=1, padx=2)
	frame_main.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
	# Obtener IP local automáticamente
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.connect(("8.8.8.8", 80))
		ip_local = s.getsockname()[0]
		s.close()
	except Exception:
		ip_local = "127.0.0.1"
	entry_ip_local.insert(0, ip_local)

	# IP destino
	tk.Label(frame_interno, text="IP destino:").grid(row=0, column=2, sticky="e", padx=2)
	entry_ip_destino = tk.Entry(frame_interno, width=15)
	entry_ip_destino.grid(row=0, column=3, padx=2)
	# Frame inferior para controles de red
	# Puerto
	tk.Label(frame_interno, text="Puerto:").grid(row=0, column=4, sticky="e", padx=2)
	entry_puerto = tk.Entry(frame_interno, width=6)
	entry_puerto.grid(row=0, column=5, padx=2)
	entry_puerto.insert(0, "5000")
	# Botones en una segunda fila
	btn_iniciar = tk.Button(frame_interno, text="Iniciar transmisión")
	btn_iniciar.grid(row=1, column=0, columnspan=3, pady=5, sticky="ew")
	btn_detener = tk.Button(frame_interno, text="Detener transmisión")
	btn_detener.grid(row=1, column=3, columnspan=3, pady=5, sticky="ew")

	# Frame izquierdo: lista de cámaras
	frame_lista = tk.Frame(frame_main)
	frame_lista.pack(side=tk.LEFT, fill=tk.Y)

	scrollbar = tk.Scrollbar(frame_lista, orient=tk.VERTICAL)
	lista_camaras = tk.Listbox(frame_lista, height=8, width=40, yscrollcommand=scrollbar.set)
	scrollbar.config(command=lista_camaras.yview)
	scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
	lista_camaras.pack(side=tk.LEFT, fill=tk.BOTH)

	# Frame derecho: video
	frame_video = tk.Frame(frame_main, width=320, height=180, bg="black")
	frame_video.pack_propagate(False)
	frame_video.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=10)

	label_video = tk.Label(frame_video, bg="black")
	label_video.pack(fill=tk.BOTH, expand=True)
	label_video.pack_forget()  # Oculto por defecto

	# Placeholder para mensaje de cámara oculta
	label_placeholder = tk.Label(frame_video, bg="black", fg="white", font=("Arial", 14),
								 text="Cámara oculta\nDale al botón para desbloquearla", justify="center")
	label_placeholder.place(relx=0.5, rely=0.5, anchor="center", relwidth=1, relheight=1)

	mostrar_video = [False]
	cap = [None]
	camara_idx = [None]

	def buscar_camaras():
		camaras = []
		max_cameras = 5  # Reducimos el número de cámaras a buscar
		for i in range(max_cameras):
			try:
				cap = cv2.VideoCapture(i)
				if cap.isOpened():
					width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
					height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
					fps = cap.get(cv2.CAP_PROP_FPS)
					if not fps or fps == 0:
						fps = 'N/A'
					nombre = f"Cámara {i} - {width}x{height} @ {fps}fps"
					camaras.append({'idx': i, 'nombre': nombre})
				cap.release()
			except Exception as e:
				print(f"Error al buscar cámara {i}: {str(e)}")
				continue
		return camaras

	camaras = buscar_camaras()

	for cam in camaras:
		lista_camaras.insert(tk.END, cam['nombre'])

	# Seleccionar la primera cámara por defecto si hay alguna
	if camaras:
		lista_camaras.selection_set(0)

	def actualizar_video():
		if mostrar_video[0] and cap[0] is not None and cap[0].isOpened():
			ret, frame = cap[0].read()
			if ret:
				h, w, _ = frame.shape
				label_w = label_video.winfo_width()
				label_h = label_video.winfo_height()
				if label_w < 10 or label_h < 10:
					label_w, label_h = 320, 180
				aspect = w / h
				if label_w / label_h > aspect:
					new_h = label_h
					new_w = int(aspect * new_h)
				else:
					new_w = label_w
					new_h = int(new_w / aspect)
				frame_disp = cv2.resize(frame, (new_w, new_h))
				img = cv2.cvtColor(frame_disp, cv2.COLOR_BGR2RGB)
				img = Image.fromarray(img)
				imgtk = ImageTk.PhotoImage(image=img)
				label_video.imgtk = imgtk
				label_video.config(image=imgtk)
		ventana.after(30, actualizar_video)

	def on_ver_video():
		if not mostrar_video[0]:
			sel = lista_camaras.curselection()
			if not sel:
				return
			idx = camaras[sel[0]]['idx']
			if cap[0] is not None:
				cap[0].release()
			cap[0] = cv2.VideoCapture(idx)
			camara_idx[0] = idx
			label_placeholder.place_forget()
			label_video.pack(fill=tk.BOTH, expand=True)
			mostrar_video[0] = True
			btn_ver.config(text="Ocultar video")
		else:
			if cap[0] is not None:
				cap[0].release()
			label_video.pack_forget()
			label_placeholder.place(relx=0.5, rely=0.5, anchor="center", relwidth=1, relheight=1)
			mostrar_video[0] = False
			btn_ver.config(text="Ver video")

	def on_cambio_camara(event):
		# Siempre ocultar video y resetear botón
		if cap[0] is not None:
			cap[0].release()
		label_video.pack_forget()
		label_placeholder.place(relx=0.5, rely=0.5, anchor="center", relwidth=1, relheight=1)
		mostrar_video[0] = False
		btn_ver.config(text="Ver video")

	lista_camaras.bind('<<ListboxSelect>>', on_cambio_camara)

	btn_ver = tk.Button(frame_video, text="Ver video", command=on_ver_video)
	btn_ver.pack(pady=5)

	def on_close():
		if cap[0] is not None:
			cap[0].release()
		ventana.destroy()

	ventana.protocol("WM_DELETE_WINDOW", on_close)
	actualizar_video()
	ventana.mainloop()

if __name__ == "__main__":
	main()
