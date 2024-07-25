import sys
import subprocess
from PyQt5.QtWidgets import QApplication, QDialog, QLabel, QPushButton, QVBoxLayout, QFileDialog, QMessageBox, QLineEdit
import qdarkstyle
from qdarkstyle import load_stylesheet, LightPalette, DarkPalette

class RunasAdminDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Run as Admin")
        
        self.ruta_script = ""
        self.comando = []

        self.label = QLabel("Please Select a Python File...", self)
        
        self.button_select = QPushButton("Select Python File", self)
        self.button_select.clicked.connect(self.seleccionar_archivo_python)

        self.password_label = QLabel("Enter Sudo Password:", self)
        self.password_input = QLineEdit(self)

        self.button_run = QPushButton("Run as Admin", self)
        self.button_run.clicked.connect(self.ejecutar_como_administrador)
        self.button_run.setEnabled(False)  # Disabled until a file is selected
        self.password_input.setEnabled(False)  # Disabled until a file is selected

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.button_select)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.button_run)
        self.setLayout(layout)

    def seleccionar_archivo_python(self):
        """Abre el administrador de archivos para seleccionar el archivo que contiene
           el código Python que se quiere ejecutar con permisos de administrador.
        """
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Python File", "", "Python Files (*.py);;All Files (*)", options=options)
        if file_path:
            self.ruta_script = file_path
            self.label.setText(f"Selected: {file_path}")
            self.button_run.setEnabled(True)
            self.password_input.setEnabled(True)
        else:
            self.label.setText("No file selected. Please select a Python file.")

    def ejecutar_como_administrador(self):
        if not self.ruta_script:
            QMessageBox.warning(self, "No File Selected", "Please select a Python file to run as admin.")
            return
        
        password = self.password_input.text()
        if not password:
            QMessageBox.warning(self, "No Password Entered", "Please enter the sudo password.")
            return

        try:
            # Minimiza la ventana y ejecuta el comando con sudo y automatizar la entrada de la contraseña
            self.showMinimized()
            comando_sudo = f"echo '{password}' | sudo -S python3 '{self.ruta_script}'"
            result = subprocess.run(comando_sudo, shell=True, capture_output=True, text=True)

            if result.returncode == 0:
                QMessageBox.warning(self, "Success", "Script executed successfully.")
                print("result.stdout:",result.stdout)
                sys.exit(0) #mejor cerrar la app para cerrar y olvidar el password de administrador
                
            else:
                mensaje = f"Error al ejecutar el script: {result.stderr}"
                QMessageBox.warning(self, "Execution Error", f"""{mensaje}
verifique su contraseña de administrador
o seleccione otro archivo de Python.

Las librerias que requieren acceso a bajo
nivel con permisos de administrador deben
ser instaladas con sudo.
                                                                          
                """)
                print("Algún Error Aconteció al ejecutar python file")
                print("mensaje result.returncode != 0:",mensaje)
                #sys.exit(1) #mejor que vuelva a intentar con otro archivo o password para solucionar el error

        except subprocess.CalledProcessError as e:
            mensaje = f"Excepcion al ejecutar el script: {e}\n\nSalida de error: {e.stderr}"
            QMessageBox.Critical(self, "Exeption Error", f"""{mensaje}
su contraseña debe coincidir ok,
sin embargo ocurrio una excepcion
seleccione otro archivo de Python
                                     
                """)
            print("Algúna exception Aconteció")
            print("mensaje subprocess.CalledProcessError:",mensaje)
            sys.exit(1) #ante una exepcion es mejor que se cierre el programa


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet(DarkPalette))
    dialog = RunasAdminDialog()
    dialog.exec_()
