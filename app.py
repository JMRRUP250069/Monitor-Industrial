import customtkinter as ctk
import random
from datetime import datetime

# Configuración estetica
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class MonitorPredictivo(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Predictor de Fallas - Planta AGS")
        self.geometry("950x700")

        self.umbral_critico = 70.0
        self.robots = [
            {"id": "Brazo-A1", "temp": 28.0, "vel": 0.0},
            {"id": "Brazo-B2", "temp": 28.0, "vel": 0.0}
        ]
        
        self.setup_ui()

    def setup_ui(self):
        # Configuración de pesos de columnas/filas
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=3) # Panel de arriba más grande
        self.grid_rowconfigure(1, weight=1) # Panel de predicción
        self.grid_rowconfigure(2, weight=0) # Botón abajo

        # 1. MONITOREO (Arriba Izquierda)
        self.frame_izq = ctk.CTkFrame(self)
        self.frame_izq.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        ctk.CTkLabel(self.frame_izq, text="MONITOREO EN VIVO", font=("Roboto", 16, "bold")).pack(pady=10)
        
        self.widgets = []
        for r in self.robots:
            lbl = ctk.CTkLabel(self.frame_izq, text=f"{r['id']}: ---", font=("Roboto", 13), justify="left")
            lbl.pack(pady=15)
            self.widgets.append(lbl)

        # 2. LOGS (Arriba Derecha)
        self.frame_der = ctk.CTkScrollableFrame(self, label_text="HISTORIAL DE EVENTOS")
        self.frame_der.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # 3. PREDICCIÓN (Abajo - Abarca 2 columnas)
        self.frame_bot = ctk.CTkFrame(self, fg_color="#1a1a1a")
        self.frame_bot.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        
        ctk.CTkLabel(self.frame_bot, text="SALA DE ESTRATEGIA: PREDICCIÓN DE TENDENCIAS", 
                     font=("Roboto", 16, "bold"), text_color="#5D3FD3").pack(pady=5)
        
        self.lbl_prediccion = ctk.CTkLabel(self.frame_bot, text="Esperando datos para análisis...", 
                                           font=("Consolas", 14), justify="left")
        self.lbl_prediccion.pack(pady=10)

        # 4. BOTÓN DE INICIO (Hasta abajo)
        self.btn_inicio = ctk.CTkButton(self, text="INICIAR ANALÍTICA", command=self.ciclo, fg_color="#1f538d")
        self.btn_inicio.grid(row=2, column=0, columnspan=2, pady=20, padx=20, sticky="ew")

    def registrar(self, rid, msg, t):
        h = datetime.now().strftime("%H:%M:%S")
        log_txt = f"[{h}] {rid}: {msg} ({t:.1f}°C)\n"
        # Usamos un label simple para el log
        lbl_log = ctk.CTkLabel(self.frame_der, text=log_txt, font=("Consolas", 11), 
                               text_color="#FF8C00", justify="left")
        lbl_log.pack(pady=2, anchor="w")

    def ciclo(self):
        max_riesgo = {"id": "Ninguno", "tiempo": 999.0, "vel": 0.0}
        self.btn_inicio.configure(state="disabled", text="SISTEMA ACTIVO")

        for i, r in enumerate(self.robots):
            antigua = r["temp"]
            # Simulación: El robot A tiende a calentarse más que el B
            incremento = random.uniform(-0.5, 3.5) if i == 0 else random.uniform(-0.5, 2.0)
            r["temp"] += incremento
            r["vel"] = r["temp"] - antigua 

            # Lógica de predicción (Tiempo = Distancia / Velocidad)
            if r["vel"] > 0:
                segundos_para_fallo = (self.umbral_critico - r["temp"]) / r["vel"]
                if 0 < segundos_para_fallo < max_riesgo["tiempo"]:
                    max_riesgo = {"id": r["id"], "tiempo": segundos_para_fallo, "vel": r["vel"]}

            # Actualización de UI de los robots
            color = "#FF4B4B" if r["temp"] > 55 else "#4BB543"
            self.widgets[i].configure(
                text=f"ID: {r['id']}\nTemp: {r['temp']:.2f}°C\nVelocidad: +{r['vel']:.2f}°/s", 
                text_color=color
            )

            # Registro si pasa el umbral
            if r["temp"] > self.umbral_critico:
                self.registrar(r["id"], "FALLO CRÍTICO - REINICIO", r["temp"])
                r["temp"] = 28.0 # Reset térmico

        # Actualizar Panel de Predicción Inferior
        if max_riesgo["id"] != "Ninguno":
            resumen = (f"ALERTA DE PROXIMIDAD: {max_riesgo['id']}\n"
                       f"TENDENCIA: +{max_riesgo['vel']:.2f} °C/seg\n"
                       f"TIEMPO ESTIMADO PARA FALLO: {max_riesgo['tiempo']:.1f} segundos")
            self.lbl_prediccion.configure(text=resumen, text_color="#FFD700")
        
        self.after(1000, self.ciclo)

if __name__ == "__main__":
    app = MonitorPredictivo()
    app.mainloop()