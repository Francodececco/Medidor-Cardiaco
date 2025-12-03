import sys
import serial
import serial.tools.list_ports
from PyQt5 import QtWidgets
from interfaz_login import Ui_LoginForm
from interfaz_monitor import Ui_Form
from PyQt5.QtCore import QTimer
import pyqtgraph as pg


# ------------------ LOGIN ------------------ #
class LoginWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_LoginForm()
        self.ui.setupUi(self)
        self.ui.btnLogin.clicked.connect(self.verificar_login)

    def verificar_login(self):
        usuario = self.ui.txtUsuario.text()
        clave = self.ui.txtPassword.text()

        if usuario == "admin" and clave == "1234":
            self.monitor = MonitorWindow()
            self.monitor.show()
            self.close()
        else:
            self.ui.lblMensaje.setText("Usuario o contraseña incorrectos")


# ------------------ MONITOR ------------------ #
class MonitorWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.arduino = None
        self.threshold = 520

        # Timer para leer datos
        self.timer = QTimer()
        self.timer.timeout.connect(self.leer_datos)
        self.timer.start(50)

        self.ui.btnConectar.clicked.connect(self.conectar_arduino)
        self.ui.btnRefrescar.clicked.connect(self.refrescar_puertos)

        self.refrescar_puertos()

        # ---------------- GRAFICO ECG ---------------- #
        self.plot = pg.PlotWidget()
        self.plot.setBackground('black')

        self.curva = self.plot.plot(pen=pg.mkPen(color='lime', width=2))

        self.ui.layoutGrafico.addWidget(self.plot)

        self.data_ecg = []
        self.max_points = 300


    # ------------ PUERTOS ------------ #
    def refrescar_puertos(self):
        self.ui.comboPuerto.clear()
        for p in serial.tools.list_ports.comports():
            self.ui.comboPuerto.addItem(p.device)


    def conectar_arduino(self):
        puerto = self.ui.comboPuerto.currentText()

        try:
            self.arduino = serial.Serial(puerto, 9600)
            self.ui.lblEstado.setText("Conectado ✓")
        except:
            self.ui.lblEstado.setText("Error al conectar")


    # ------------ LECTURA ARDUINO ------------ #
    def leer_datos(self):
        if not self.arduino:
            return

        if self.arduino.in_waiting:
            try:
                linea = self.arduino.readline().decode().strip()

                # ------- Valor analógico crudo ------- #
                if linea.startswith("VAL:"):
                    valor = int(linea.replace("VAL:", ""))
                    self.ui.lblBPM.setText(str(valor))

                    # Actualizar gráfico
                    self.data_ecg.append(valor)
                    if len(self.data_ecg) > self.max_points:
                        self.data_ecg.pop(0)
                    self.curva.setData(self.data_ecg)

                    # Clasificación
                    if valor > self.threshold:
                        self.ui.lblClasificacion.setText("LATIDO 🔴")
                    else:
                        self.ui.lblClasificacion.setText("Reposo 🟢")

                # ------- BPM enviados por Arduino ------- #
                if linea.startswith("BPM:"):
                    bpm = int(linea.replace("BPM:", ""))
                    self.ui.lblBPM.setText(f"{bpm} BPM")

            except:
                pass



# ------------------ EJECUTAR ------------------ #
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    login = LoginWindow()
    login.show()
    sys.exit(app.exec_())
