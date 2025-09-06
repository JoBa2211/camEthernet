import cv2
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import socket
import threading
import numpy as np

def get_ip_address():
    try:
        # Crea un socket UDP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Conecta a un servidor externo (no hace una conexión real)
        s.connect(("8.8.8.8", 80))
        # Obtiene la IP local que se usaría para la conexión
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def main():
    ventana = tk.Tk()
    ventana.title("Cámara Ethernet")
    
    # Notebook (pestañas)
    notebook = ttk.Notebook(ventana)
    notebook.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
    
    # Tab de transmisión
    tab_transmision = ttk.Frame(notebook)
    notebook.add(tab_transmision, text="Transmisión")
    
    # Tab de recepción
    tab_recepcion = ttk.Frame(notebook)
    notebook.add(tab_recepcion, text="Recepción")

    # Frame para el video de recepción
    frame_video_rec = tk.Frame(tab_recepcion, width=640, height=480, bg="black")
    frame_video_rec.pack_propagate(False)
    frame_video_rec.pack(pady=10, fill=tk.BOTH, expand=True)

    # Label para video de recepción
    label_video_rec = tk.Label(frame_video_rec, bg="black")
    label_video_rec.pack(fill=tk.BOTH, expand=True)
    label_video_rec.pack_forget()  # Oculto por defecto

    # Placeholder para recepción
    label_placeholder_rec = tk.Label(frame_video_rec, bg="black", fg="white", font=("Arial", 14),
                                   text="Sin transmisión\nEsperando conexión...", justify="center")
    label_placeholder_rec.place(relx=0.5, rely=0.5, anchor="center", relwidth=1, relheight=1)

    # Frame para controles de recepción
    frame_controles_rec = tk.Frame(tab_recepcion)
    frame_controles_rec.pack(padx=10, pady=5, fill=tk.X, side=tk.BOTTOM)

    # Frame para los controles de recepción
    frame_campos_rec = tk.Frame(frame_controles_rec)
    frame_campos_rec.pack(pady=5)

    # Puerto para recepción en el centro
    frame_puerto = tk.Frame(frame_campos_rec)
    frame_puerto.pack(pady=5)
    tk.Label(frame_puerto, text="Puerto:").pack(side=tk.LEFT, padx=5)
    entry_puerto_rec = tk.Entry(frame_puerto, width=6)
    entry_puerto_rec.pack(side=tk.LEFT, padx=5)
    entry_puerto_rec.insert(0, "5000")

    # Frame para el estado de recepción
    frame_estado_rec = tk.Frame(frame_controles_rec)
    frame_estado_rec.pack(pady=5)

    # Label para mostrar el estado de la recepción
    label_estado_rec = tk.Label(frame_estado_rec, text="Estado: Detenido", fg="red")
    label_estado_rec.pack()
    
    # Frame principal dentro de la pestaña de transmisión
    frame_main = tk.Frame(tab_transmision)
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
    frame_video = tk.Frame(frame_main, width=640, height=480, bg="black")
    frame_video.pack_propagate(False)
    frame_video.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

    # Label para video
    label_video = tk.Label(frame_video, bg="black")
    label_video.pack(fill=tk.BOTH, expand=True)
    label_video.pack_forget()  # Oculto por defecto

    # Placeholder para mensaje de cámara oculta
    label_placeholder = tk.Label(frame_video, bg="black", fg="white", font=("Arial", 14),
                                text="Cámara oculta\nPresiona 'Ver video' para activar", justify="center")
    label_placeholder.place(relx=0.5, rely=0.5, anchor="center", relwidth=1, relheight=1)

    # Botón para ver video
    btn_ver = tk.Button(frame_video, text="Ver video", command=lambda: iniciar_video())
    btn_ver.pack(side=tk.BOTTOM, pady=5)

    # Variables globales
    mostrar_video = [False]
    cap = [None]
    recibiendo = [False]
    socket_receptor = [None]
    frame_recibido = [None]
    servidor_socket = [None]
    socket_transmisor = [None]
    transmitiendo = [False]



    def on_cambio_camara(event):
        # Detener el video actual si está reproduciéndose
        if cap[0] is not None:
            cap[0].release()
            cap[0] = None
        label_video.pack_forget()
        label_placeholder.place(relx=0.5, rely=0.5, anchor="center", relwidth=1, relheight=1)
        mostrar_video[0] = False
        btn_ver.config(text="Ver video")

    def iniciar_video():
        sel = lista_camaras.curselection()
        if not sel:
            messagebox.showwarning("Aviso", "Por favor, selecciona una cámara primero")
            return

        idx = camaras[sel[0]]['idx']
        if cap[0] is not None:
            cap[0].release()
        cap[0] = cv2.VideoCapture(idx)
        if not mostrar_video[0]:
            label_placeholder.place_forget()
            label_video.pack(fill=tk.BOTH, expand=True)
            mostrar_video[0] = True
            btn_ver.config(text="Ocultar video")
            actualizar_video()
        else:
            if cap[0] is not None:
                cap[0].release()
                cap[0] = None
            label_video.pack_forget()
            label_placeholder.place(relx=0.5, rely=0.5, anchor="center", relwidth=1, relheight=1)
            mostrar_video[0] = False
            btn_ver.config(text="Ver video")

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

    def procesar_frame(frame, label_w, label_h):
        h, w, _ = frame.shape
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
        return ImageTk.PhotoImage(image=img)

    def actualizar_video():
        if mostrar_video[0] and cap[0] is not None and cap[0].isOpened():
            try:
                ret, frame = cap[0].read()
                if ret:
                    # Procesar frame para visualización
                    label_w = label_video.winfo_width()
                    label_h = label_video.winfo_height()
                    imgtk = procesar_frame(frame, label_w, label_h)
                    label_video.imgtk = imgtk
                    label_video.config(image=imgtk)

                    # Enviar frame si estamos transmitiendo
                    if transmitiendo[0] and socket_transmisor[0]:
                        try:
                            # Comprimir frame para envío (calidad reducida para mejor rendimiento)
                            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 80]
                            _, buffer = cv2.imencode('.jpg', frame, encode_param)
                            data = buffer.tobytes()
                            # Enviar tamaño del frame primero
                            size = len(data).to_bytes(4, 'big')
                            socket_transmisor[0].sendall(size)
                            # Enviar frame
                            socket_transmisor[0].sendall(data)
                        except:
                            transmitiendo[0] = False
                            if socket_transmisor[0]:
                                socket_transmisor[0].close()
                                socket_transmisor[0] = None
                            btn_transmitir.config(text="Iniciar Transmisión", bg="green")
                            messagebox.showerror("Error", "Se perdió la conexión con el receptor")
            except:
                pass  # Ignorar errores temporales de la cámara
        
        if mostrar_video[0]:  # Solo programar el siguiente frame si seguimos mostrando video
            ventana.after(30, actualizar_video)

    # Buscar y listar cámaras
    camaras = buscar_camaras()
    for cam in camaras:
        lista_camaras.insert(tk.END, cam['nombre'])

    # Seleccionar la primera cámara por defecto si hay alguna
    if camaras:
        lista_camaras.selection_set(0)

    def iniciar_receptor():
        try:
            puerto = int(entry_puerto_rec.get())
            servidor_socket[0] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            servidor_socket[0].bind(('0.0.0.0', puerto))
            servidor_socket[0].listen(1)
            recibiendo[0] = True
            label_estado_rec.config(text="Estado: Esperando conexión...", fg="orange")
            
            def esperar_conexion():
                while recibiendo[0]:
                    try:
                        socket_receptor[0], addr = servidor_socket[0].accept()
                        respuesta = messagebox.askyesno("Nueva conexión",
                                                       f"¿Aceptar transmisión desde {addr[0]}?")
                        if respuesta:
                            label_estado_rec.config(text=f"Estado: Conectado desde {addr[0]}", fg="green")
                            recibir_frames()
                        else:
                            socket_receptor[0].close()
                            socket_receptor[0] = None
                            label_estado_rec.config(text="Estado: Esperando conexión...", fg="orange")
                    except:
                        break

            def recibir_frames():
                def recibir_datos(sock, size):
                    data = bytearray()
                    while len(data) < size:
                        try:
                            packet = sock.recv(size - len(data))
                            if not packet:
                                return None
                            data.extend(packet)
                        except:
                            return None
                    return data

                while recibiendo[0]:
                    try:
                        # Primero recibimos el tamaño del frame
                        data_size = recibir_datos(socket_receptor[0], 4)
                        if data_size is None:
                            break
                        size = int.from_bytes(data_size, 'big')
                        
                        # Luego recibimos el frame completo
                        data = recibir_datos(socket_receptor[0], size)
                        if data is None:
                            break
                        
                        # Convertimos los datos a frame
                        frame_data = np.frombuffer(data, dtype=np.uint8)
                        frame = cv2.imdecode(frame_data, cv2.IMREAD_COLOR)
                        
                        if frame is not None:
                            frame_recibido[0] = frame
                            ventana.after(0, mostrar_frame_recibido)  # Actualizar UI en el hilo principal
                    except:
                        break
                
                if socket_receptor[0]:
                    socket_receptor[0].close()
                label_estado_rec.config(text="Estado: Desconectado", fg="red")
                label_video_rec.pack_forget()
                label_placeholder_rec.place(relx=0.5, rely=0.5, anchor="center", relwidth=1, relheight=1)

            threading.Thread(target=esperar_conexion, daemon=True).start()
        
        except Exception as e:
            messagebox.showerror("Error", f"Error al iniciar recepción: {str(e)}")
            detener_receptor()

    def detener_receptor():
        recibiendo[0] = False
        if socket_receptor[0]:
            socket_receptor[0].close()
        if servidor_socket[0]:
            servidor_socket[0].close()
        label_estado_rec.config(text="Estado: Detenido", fg="red")
        label_video_rec.pack_forget()
        label_placeholder_rec.place(relx=0.5, rely=0.5, anchor="center", relwidth=1, relheight=1)

    def mostrar_frame_recibido():
        try:
            if frame_recibido[0] is not None:
                label_w = label_video_rec.winfo_width()
                label_h = label_video_rec.winfo_height()
                imgtk = procesar_frame(frame_recibido[0], label_w, label_h)
                label_video_rec.imgtk = imgtk
                label_video_rec.config(image=imgtk)
                
                if label_placeholder_rec.winfo_viewable():
                    label_placeholder_rec.place_forget()
                    label_video_rec.pack(fill=tk.BOTH, expand=True)
        except:
            pass  # Ignorar errores temporales de procesamiento

    def on_close():
        if cap[0] is not None:
            cap[0].release()
        recibiendo[0] = False
        if socket_receptor[0]:
            socket_receptor[0].close()
        if servidor_socket[0]:
            servidor_socket[0].close()
        ventana.destroy()

    # Frame inferior para controles de transmisión
    frame_controles = tk.Frame(tab_transmision)
    frame_controles.pack(padx=10, pady=5, fill=tk.X, side=tk.BOTTOM)

    # Frame para los campos de entrada
    frame_campos = tk.Frame(frame_controles)
    frame_campos.pack(pady=5)

    # IP destino y puerto
    tk.Label(frame_campos, text="IP destino:").grid(row=0, column=0, padx=5)
    entry_ip_destino = tk.Entry(frame_campos, width=15)
    entry_ip_destino.grid(row=0, column=1, padx=5)
    entry_ip_destino.insert(0, "127.0.0.1")

    tk.Label(frame_campos, text="Puerto:").grid(row=0, column=2, padx=5)
    entry_puerto = tk.Entry(frame_campos, width=6)
    entry_puerto.grid(row=0, column=3, padx=5)
    entry_puerto.insert(0, "5000")

    # Frame para los botones de transmisión
    frame_botones = tk.Frame(frame_controles)
    frame_botones.pack(pady=5)

    # Variable para controlar el estado de la transmisión
    transmitiendo = [False]

    # Botones de control de recepción
    frame_botones_rec = tk.Frame(frame_controles_rec)
    frame_botones_rec.pack(pady=5)

    btn_iniciar_rec = tk.Button(frame_botones_rec, text="Iniciar Recepción",
                               command=iniciar_receptor, bg="green", fg="white",
                               width=20, height=1)
    btn_iniciar_rec.pack(side=tk.LEFT, padx=5)

    btn_detener_rec = tk.Button(frame_botones_rec, text="Detener Recepción",
                               command=detener_receptor, bg="red", fg="white",
                               width=20, height=1)

    def toggle_transmision():
        if not transmitiendo[0]:
            try:
                # Verificar que haya una cámara seleccionada y activa
                if not cap[0] or not cap[0].isOpened():
                    messagebox.showerror("Error", "Por favor, selecciona y activa una cámara primero")
                    return

                # Obtener datos de conexión
                ip_destino = entry_ip_destino.get()
                puerto = int(entry_puerto.get())

                # Crear socket de transmisión
                socket_transmisor[0] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    socket_transmisor[0].connect((ip_destino, puerto))
                except:
                    messagebox.showerror("Error", "No se pudo conectar al receptor")
                    socket_transmisor[0].close()
                    socket_transmisor[0] = None
                    return

                transmitiendo[0] = True
                btn_transmitir.config(text="Detener Transmisión", bg="red")

            except ValueError:
                messagebox.showerror("Error", "El puerto debe ser un número")
            except Exception as e:
                messagebox.showerror("Error", f"Error al iniciar transmisión: {str(e)}")
        else:
            # Detener transmisión
            transmitiendo[0] = False
            if socket_transmisor[0]:
                socket_transmisor[0].close()
                socket_transmisor[0] = None
            btn_transmitir.config(text="Iniciar Transmisión", bg="green")

    # Botón de transmisión
    btn_transmitir = tk.Button(frame_botones, text="Iniciar Transmisión", 
                              command=toggle_transmision, bg="green", fg="white",
                              width=20, height=1)
    btn_transmitir.pack(pady=5)

    # Cambiar selección de cámara
    lista_camaras.bind('<<ListboxSelect>>', lambda e: on_cambio_camara(e))

    ventana.protocol("WM_DELETE_WINDOW", on_close)
    ventana.mainloop()

if __name__ == "__main__":
    main()