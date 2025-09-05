import cv2

import tkinter as tk

def main():
	from PIL import Image, ImageTk

	ventana = tk.Tk()
	ventana.title("camEthernet.py")
	ventana.geometry("600x300")

	frame_main = tk.Frame(ventana)
	frame_main.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

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
		for i in range(20):
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
		return camaras

	camaras = buscar_camaras()
	for cam in camaras:
		lista_camaras.insert(tk.END, cam['nombre'])

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
