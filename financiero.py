import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog
import json
from datetime import datetime, timedelta
from collections import defaultdict
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import calendar
import hashlib
import secrets
from cryptography.fernet import Fernet
import base64

class SistemaSeguridad:
    def __init__(self):
        self.archivo_usuarios = "usuarios_sistema.json"
        self.archivo_clave_maestra = "clave_maestra.key"
        self.usuarios = {}
        self.intentos_fallidos = {}
        self.max_intentos = 3
        self.cargar_usuarios()
        self.cipher = self.obtener_cipher()
    
    def obtener_cipher(self):
        if os.path.exists(self.archivo_clave_maestra):
            with open(self.archivo_clave_maestra, 'rb') as f:
                key = f.read()
        else:
            key = Fernet.generate_key()
            with open(self.archivo_clave_maestra, 'wb') as f:
                f.write(key)
        return Fernet(key)
    
    def hash_password(self, password, salt=None):
        if salt is None:
            salt = secrets.token_hex(32)
        pwd_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        )
        return salt, pwd_hash.hex()
    
    def verificar_password(self, password, salt, hash_guardado):
        _, nuevo_hash = self.hash_password(password, salt)
        return nuevo_hash == hash_guardado
    
    def crear_usuario_inicial(self):
        salt, pwd_hash = self.hash_password("admin123")
        salt_resp, resp_hash = self.hash_password("admin") 
        self.usuarios = {
            "admin": {
                "nombre_completo": "Administrador",
                "email": "admin@empresa.com",
                "rol": "Administrador",
                "password_salt": salt,
                "password_hash": pwd_hash,
                "pregunta_seguridad": "¿Cuál es el nombre de tu primera mascota?", 
                "respuesta_salt": salt_resp,                                        
                "respuesta_hash": resp_hash, 
                "activo": True,
                "fecha_creacion": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "ultimo_acceso": None,
                "intentos_fallidos": 0
            }
        }
        self.guardar_usuarios()
    
    def cargar_usuarios(self):
        if os.path.exists(self.archivo_usuarios):
            try:
                with open(self.archivo_usuarios, 'r', encoding='utf-8') as f:
                    self.usuarios = json.load(f)
            except:
                self.crear_usuario_inicial()
        else:
            self.crear_usuario_inicial()
    
    def guardar_usuarios(self):
        with open(self.archivo_usuarios, 'w', encoding='utf-8') as f:
            json.dump(self.usuarios, f, ensure_ascii=False, indent=2)
    
    def autenticar(self, usuario, password):
        if usuario not in self.usuarios:
            return False, "Usuario no existe"
        
        user_data = self.usuarios[usuario]
        
        if user_data.get('intentos_fallidos', 0) >= self.max_intentos:
            return False, f"Usuario bloqueado. Contacte al administrador."
        
        if not user_data.get('activo', False):
            return False, "Usuario desactivado"
        
        if self.verificar_password(password, user_data['password_salt'], user_data['password_hash']):
            user_data['intentos_fallidos'] = 0
            user_data['ultimo_acceso'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.guardar_usuarios()
            return True, "Login exitoso"
        else:
            user_data['intentos_fallidos'] = user_data.get('intentos_fallidos', 0) + 1
            self.guardar_usuarios()
            intentos_restantes = self.max_intentos - user_data['intentos_fallidos']
            if intentos_restantes > 0:
                return False, f"Contraseña incorrecta. {intentos_restantes} intentos restantes."
            else:
                return False, "Usuario bloqueado por múltiples intentos fallidos."
    
    def crear_usuario(self, username, nombre_completo, password, rol, pregunta_seguridad="¿Cuál es el nombre de tu primera mascota?", respuesta_seguridad=""):
        if username in self.usuarios:
            return False, "El usuario ya existe"
        
        salt, pwd_hash = self.hash_password(password)
        salt_resp, resp_hash = self.hash_password(respuesta_seguridad.strip().lower()) if respuesta_seguridad else ("", "")
        
        self.usuarios[username] = {
            "nombre_completo": nombre_completo,
            "rol": rol,
            "password_salt": salt,
            "password_hash": pwd_hash,
            "pregunta_seguridad": pregunta_seguridad,
            "respuesta_salt": salt_resp,
            "respuesta_hash": resp_hash,
            "activo": True,
            "fecha_creacion": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "ultimo_acceso": None,
            "intentos_fallidos": 0
        }
        self.guardar_usuarios()
        return True, "Usuario creado exitosamente"
    
    def cambiar_password(self, username, password_actual, password_nueva):
        if username not in self.usuarios:
            return False, "Usuario no existe"
        user_data = self.usuarios[username]
        if not self.verificar_password(password_actual, user_data['password_salt'], user_data['password_hash']):
            return False, "Contraseña actual incorrecta"
        
        salt, pwd_hash = self.hash_password(password_nueva)
        user_data['password_salt'] = salt
        user_data['password_hash'] = pwd_hash
        self.guardar_usuarios()
        return True, "Contraseña cambiada exitosamente"

    def verificar_respuesta_seguridad(self, username, respuesta):
        if username not in self.usuarios:
            return False, "Usuario no existe"
            
        user_data = self.usuarios[username]
        
        if 'respuesta_hash' not in user_data or not user_data['respuesta_hash']:
            return False, "Este usuario no tiene configurada una pregunta de seguridad. Contacte al administrador."
            
        respuesta_limpia = respuesta.strip().lower()
        if self.verificar_password(respuesta_limpia, user_data['respuesta_salt'], user_data['respuesta_hash']):
            return True, "Respuesta correcta"
        return False, "Respuesta incorrecta"

    def restablecer_password(self, username, nueva_password):
        if username not in self.usuarios:
            return False
            
        salt, pwd_hash = self.hash_password(nueva_password)
        self.usuarios[username]['password_salt'] = salt
        self.usuarios[username]['password_hash'] = pwd_hash
        self.usuarios[username]['intentos_fallidos'] = 0 
        self.guardar_usuarios()
        return True

class VentanaLogin:
    def __init__(self, root, seguridad):
        self.root = root
        self.seguridad = seguridad
        self.usuario_actual = None
        self.login_exitoso = False
        
        self.root.title("🔐 Sistema de Login - AgriTrack")
        self.root.geometry("500x630")
        self.root.configure(bg='#2d5016')
        
        self.centrar_ventana()
        self.crear_interfaz()
        self.root.bind('<Return>', lambda e: self.intentar_login())
    
    def centrar_ventana(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def crear_interfaz(self):
        frame_principal = tk.Frame(self.root, bg='#2d5016')
        frame_principal.pack(expand=True, fill='both', padx=20, pady=20)
        
        tk.Label(frame_principal, text="🌾", font=('Arial', 60), bg='#2d5016', fg='white').pack(pady=(0, 10))
        tk.Label(frame_principal, text="AgriTrack", font=('Arial', 16, 'bold'), bg='#2d5016', fg='white').pack(pady=(0, 5))
        tk.Label(frame_principal, text="Inicio de Sesión", font=('Arial', 12), bg='#2d5016', fg='#90EE90').pack(pady=(0, 20))
        
        frame_login = tk.Frame(frame_principal, bg='white', relief='raised', bd=3)
        frame_login.pack(pady=10, padx=40, fill='both', expand=True)
        
        tk.Label(frame_login, text="👤 Usuario:", font=('Arial', 11, 'bold'), bg='white').pack(pady=(20, 5), anchor='w', padx=20)
        self.entry_usuario = ttk.Entry(frame_login, font=('Arial', 11), width=30)
        self.entry_usuario.pack(pady=(0, 15), padx=20)
        self.entry_usuario.focus()
        
        tk.Label(frame_login, text="🔒 Contraseña:", font=('Arial', 11, 'bold'), bg='white').pack(pady=(0, 5), anchor='w', padx=20)
        self.entry_password = ttk.Entry(frame_login, font=('Arial', 11), width=30, show='●')
        self.entry_password.pack(pady=(0, 10), padx=20)
        
        self.mostrar_pass_var = tk.BooleanVar()
        tk.Checkbutton(
            frame_login, text="Mostrar contraseña", variable=self.mostrar_pass_var,
            command=self.toggle_password, bg='white', font=('Arial', 9)
        ).pack(anchor='w', padx=20)
        
        btn_login = tk.Button(
            frame_login, text="🔓 INICIAR SESIÓN", font=('Arial', 12, 'bold'),
            bg='#4CAF50', fg='white', relief='raised', bd=3, cursor='hand2',
            command=self.intentar_login
        )
        btn_login.pack(pady=(20, 10), padx=20, fill='x')

        btn_recuperar = tk.Button(
            frame_login, text="¿Olvidaste tu contraseña?", font=('Arial', 9, 'underline'),
            bg='white', fg='#2d5016', relief='flat', cursor='hand2',
            command=self.abrir_recuperacion
        )
        btn_recuperar.pack(pady=(0, 15))
        
        frame_info = tk.Frame(frame_principal, bg='#2d5016')
        frame_info.pack(pady=5)
        
        self.label_estado = tk.Label(frame_principal, text="", font=('Arial', 10, 'bold'), bg='#2d5016', fg='#FF6B6B')
        self.label_estado.pack(pady=5)
    
    def toggle_password(self):
        if self.mostrar_pass_var.get():
            self.entry_password.config(show='')
        else:
            self.entry_password.config(show='●')
    
    def intentar_login(self):
        usuario = self.entry_usuario.get().strip()
        password = self.entry_password.get()
        if not usuario or not password:
            self.label_estado.config(text="⚠️ Complete todos los campos", fg='#FF6B6B')
            return
        exito, mensaje = self.seguridad.autenticar(usuario, password)
        if exito:
            self.label_estado.config(text="✅ " + mensaje, fg='#4CAF50')
            self.usuario_actual = usuario
            self.login_exitoso = True
            self.root.after(500, self.root.destroy)
        else:
            self.label_estado.config(text="❌ " + mensaje, fg='#FF6B6B')
            self.entry_password.delete(0, 'end')

    def abrir_recuperacion(self):
        vent_rec = tk.Toplevel(self.root)
        vent_rec.title("Recuperar Contraseña")
        vent_rec.geometry("400x550")
        vent_rec.configure(bg='#2d5016')
        vent_rec.transient(self.root)
        vent_rec.grab_set()

        frame_main = tk.Frame(vent_rec, bg='white', padx=20, pady=20)
        frame_main.pack(fill='both', expand=True, padx=15, pady=15)

        tk.Label(frame_main, text="Recuperación de Cuenta", font=('Arial', 14, 'bold'), bg='white').pack(pady=(0, 15))

        frame_paso1 = tk.Frame(frame_main, bg='white')
        frame_paso1.pack(fill='x')
        
        tk.Label(frame_paso1, text="1. Ingresa tu usuario:", font=('Arial', 10, 'bold'), bg='white').pack(anchor='w')
        entry_user = ttk.Entry(frame_paso1, width=30)
        entry_user.pack(pady=5, fill='x')

        frame_pasos_siguientes = tk.Frame(frame_main, bg='white')
        
        lbl_pregunta = tk.Label(frame_pasos_siguientes, text="", font=('Arial', 10, 'italic'), bg='white', wraplength=300)
        entry_respuesta = ttk.Entry(frame_pasos_siguientes, width=30)
        
        entry_nueva_pass = ttk.Entry(frame_pasos_siguientes, width=30, show='●')
        entry_conf_pass = ttk.Entry(frame_pasos_siguientes, width=30, show='●')
        
        lbl_estado = tk.Label(frame_main, text="", bg='white', font=('Arial', 9))
        lbl_estado.pack(side='bottom', pady=10)

        def buscar_usuario():
            user = entry_user.get().strip()
            if user in self.seguridad.usuarios:
                datos_usuario = self.seguridad.usuarios[user]
                if 'pregunta_seguridad' in datos_usuario and datos_usuario['pregunta_seguridad']:
                    lbl_pregunta.config(text=f"Pregunta: {datos_usuario['pregunta_seguridad']}")
                    frame_pasos_siguientes.pack(fill='x', pady=10)
                    btn_buscar.pack_forget() 
                    entry_user.config(state='disabled')
                    lbl_estado.config(text="")
                else:
                    lbl_estado.config(text="Usuario no tiene pregunta: Contacte al Admin", fg='red')
            else:
                lbl_estado.config(text="Usuario no encontrado", fg='red')

        btn_buscar = ttk.Button(frame_paso1, text="Buscar Usuario", command=buscar_usuario)
        btn_buscar.pack(pady=10)

        tk.Label(frame_pasos_siguientes, text="2. Respuesta de seguridad:", font=('Arial', 10, 'bold'), bg='white').pack(anchor='w', pady=(10, 0))
        lbl_pregunta.pack(anchor='w', pady=5)
        entry_respuesta.pack(fill='x')

        tk.Label(frame_pasos_siguientes, text="3. Nueva Contraseña:", font=('Arial', 10, 'bold'), bg='white').pack(anchor='w', pady=(15, 0))
        entry_nueva_pass.pack(fill='x', pady=5)
        tk.Label(frame_pasos_siguientes, text="Confirmar Contraseña:", font=('Arial', 10, 'bold'), bg='white').pack(anchor='w')
        entry_conf_pass.pack(fill='x', pady=5)

        def intentar_restablecer():
            user = entry_user.get().strip()
            resp = entry_respuesta.get()
            n_pass = entry_nueva_pass.get()
            c_pass = entry_conf_pass.get()

            if not resp or not n_pass or not c_pass:
                lbl_estado.config(text="Complete todos los campos", fg='red')
                return

            if n_pass != c_pass:
                lbl_estado.config(text="Las contraseñas no coinciden", fg='red')
                return
                
            if len(n_pass) < 6:
                lbl_estado.config(text="La contraseña debe tener al menos 6 caracteres", fg='red')
                return

            exito, msj = self.seguridad.verificar_respuesta_seguridad(user, resp)
            if exito:
                self.seguridad.restablecer_password(user, n_pass)
                messagebox.showinfo("Éxito", "Contraseña restablecida correctamente.\nYa puedes iniciar sesión.", parent=vent_rec)
                vent_rec.destroy()
            else:
                lbl_estado.config(text="Respuesta incorrecta", fg='red')

        ttk.Button(frame_pasos_siguientes, text="Restablecer Contraseña", command=intentar_restablecer).pack(pady=20)


class SistemaFinancieroAgricolaSeguro:
    def __init__(self, root, usuario_actual, seguridad):
        self.root = root
        self.usuario_actual = usuario_actual
        self.seguridad = seguridad
        self.datos_usuario = seguridad.usuarios[usuario_actual]
        self.rol_usuario = self.datos_usuario['rol']
        
        self.root.title(f"Sistema de Gestión Financiera - {self.datos_usuario['nombre_completo']}")
        self.root.geometry("1400x800")
        self.root.configure(bg='#2d5016')
        
        self.archivo_datos = "agricultura_finanzas.json"
        self.archivo_presupuesto = "agricultura_presupuesto.json"
        self.archivo_proveedores = "agricultura_proveedores.json"
        self.archivo_presupuesto_mensual = "agricultura_presupuesto_mensual.json"
        self.archivo_presupuestos_anuales = "agricultura_presupuestos_anuales.json"
        self.archivo_sobrantes_anuales = "agricultura_sobrantes_anuales.json"
        self.archivo_categorias_personalizadas = "agricultura_categorias_personalizadas.json"
        self.archivo_log_actividades = "log_actividades.json"
        
        self.transacciones = []
        self.presupuesto_anual = {}
        self.presupuesto_mensual_por_mes = {}
        self.proveedores = {}
        self.presupuesto_modificado = {}
        self.sobrantes = {}
        self.presupuestos_por_año = {}
        self.sobrantes_anuales = {}
        self.año_actual = datetime.now().year
        self.categorias_personalizadas = {}
        self.log_actividades = []
        
        self.categorias_agricolas = {
            "Insumos Agrícolas": ["Semillas", "Fertilizantes", "Pesticidas", "Abonos", "Herbicidas"],
            "Maquinaria y Equipos": ["Tractores", "Cosechadoras", "Equipos de riego", "Herramientas", "Mantenimiento"],
            "Alimentación Animal": ["Forraje", "Concentrados", "Suplementos", "Medicamentos veterinarios"],
            "Ganado y Animales": ["Compra de ganado", "Reproducción", "Cuidado veterinario"],
            "Mano de Obra": ["Salarios", "Jornaleros", "Técnicos", "Prestaciones"],
            "Servicios": ["Agua", "Electricidad", "Combustible", "Transporte"],
            "Infraestructura": ["Construcción", "Reparaciones", "Cercas", "Establos"],
            "Otros Gastos": ["Seguros", "Impuestos", "Asesoría", "Varios"]
        }
        
        self.meses = [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]
        
        self.cargar_datos()
        self.configurar_estilos()
        self.crear_widgets()
        self.registrar_actividad("Inicio de sesión")
        self.mostrar_bienvenida()

    def validar_solo_numeros(self, valor):
        if valor == "":
            return True
        try:
            int(valor)
            return True
        except ValueError:
            return False
    
    def registrar_actividad(self, actividad, detalles=""):
        log_entry = {
            'fecha_hora': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'usuario': self.usuario_actual,
            'rol': self.rol_usuario,
            'actividad': actividad,
            'detalles': detalles
        }
        self.log_actividades.append(log_entry)
        self.guardar_log_actividades()
    
    def guardar_log_actividades(self):
        try:
            with open(self.archivo_log_actividades, 'w', encoding='utf-8') as f:
                json.dump(self.log_actividades, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def cargar_log_actividades(self):
        if os.path.exists(self.archivo_log_actividades):
            try:
                with open(self.archivo_log_actividades, 'r', encoding='utf-8') as f:
                    self.log_actividades = json.load(f)
            except:
                self.log_actividades = []
    
    def verificar_permiso(self, accion):
        if self.rol_usuario == 'Administrador':
            return True
        
        permisos = {
            'Usuario': ['ver', 'editar', 'agregar', 'eliminar', 'transferir'],
            'Visualizador': ['ver']
        }
        
        if accion == 'gestion_usuarios':
            return self.rol_usuario == 'Administrador'
        
        permisos_usuario = permisos.get(self.rol_usuario, [])
        return accion in permisos_usuario
    
    def puede_modificar(self):
        return self.rol_usuario in ['Administrador', 'Usuario']
    
    def mostrar_bienvenida(self):
        mensaje = f"Bienvenido/a {self.datos_usuario['nombre_completo']}\n"
        mensaje += f"Rol: {self.rol_usuario}\n"
        mensaje += f"Último acceso: {self.datos_usuario.get('ultimo_acceso', 'Primer ingreso')}"
        messagebox.showinfo("¡Bienvenido!", mensaje)
    
    def configurar_estilos(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Title.TLabel', font=('Arial', 18, 'bold'), background='#2d5016', foreground='white')
        style.configure('Header.TLabel', font=('Arial', 13, 'bold'), background='#f0f0f0')
        style.configure('TButton', font=('Arial', 10, 'bold'))
        style.configure('Treeview', rowheight=28)
        style.configure('Treeview.Heading', font=('Arial', 10, 'bold'))
    
    def crear_widgets(self):
        header = tk.Frame(self.root, bg='#2d5016', height=80)
        header.pack(fill='x')
        tk.Label(header, text="🌾 AgriTrack SISTEMA DE GESTIÓN FINANCIERA AGRÍCOLA 🚜", 
                 font=('Arial', 20, 'bold'), bg='#2d5016', fg='white').pack(side='left', pady=20, padx=20)
        
        frame_usuario = tk.Frame(header, bg='#2d5016')
        frame_usuario.pack(side='right', padx=20)

        tk.Label(
            frame_usuario,
            text=f"👤 {self.datos_usuario['nombre_completo']}",
            font=('Arial', 11, 'bold'),
            bg='#2d5016',
            fg='#90EE90'
        ).pack(anchor='e')

        tk.Label(
            frame_usuario,
            text=f"🔑 {self.rol_usuario}",
            font=('Arial', 9),
            bg='#2d5016',
            fg='#FFD700'
        ).pack(anchor='e')
        
        self.label_año_actual = tk.Label(
            frame_usuario,
            text=f"📅 Año: {self.año_actual}",
            font=('Arial', 10, 'bold'),
            bg='#2d5016',
            fg='#87CEEB'
        )
        self.label_año_actual.pack(anchor='e')
        
        frame_botones_sesion = tk.Frame(header, bg='#2d5016')
        frame_botones_sesion.pack(side='right', padx=10)
        ttk.Button(frame_botones_sesion, text="🔒 Cambiar Contraseña", command=self.cambiar_contraseña).pack(side='top', pady=2)
        ttk.Button(frame_botones_sesion, text="🚪 Cerrar Sesión", command=self.cerrar_sesion).pack(side='top', pady=2)
        
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        self.crear_pestañas_segun_rol()
    
    def crear_pestañas_segun_rol(self):
        if self.rol_usuario == 'Administrador':
            self.tab_usuarios = ttk.Frame(self.notebook)
            self.notebook.add(self.tab_usuarios, text='👥 Gestión de Usuarios')
            self.crear_tab_usuarios()
            
            self.tab_log = ttk.Frame(self.notebook)
            self.notebook.add(self.tab_log, text='📋 Log de Actividades')
            self.crear_tab_log()
        
        self.tab_gestion_año = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_gestion_año, text='📅 Gestión de Años')
        self.crear_tab_gestion_año()
        
        self.tab_categorias_custom = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_categorias_custom, text='🏷️ Gestionar Categorías')
        self.crear_tab_categorias_custom()
        
        self.tab_presupuesto_mensual = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_presupuesto_mensual, text='💰 Presupuesto Mensual')
        self.crear_tab_presupuesto_mensual()
        
        self.tab_proveedores = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_proveedores, text='🏪 Catálogo de Proveedores')
        self.crear_tab_proveedores()
        
        self.tab_registro = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_registro, text='📝 Registro de Gastos')
        self.crear_tab_registro()
        
        self.tab_control = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_control, text='📊 Control Mensual')
        self.crear_tab_control()
        
        self.tab_sobrantes = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_sobrantes, text='💵 Gestión de Sobrantes')
        self.crear_tab_sobrantes()
        
        self.tab_graficos = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_graficos, text='📈 Gráficos y Análisis')
        self.crear_tab_graficos()

    def crear_tab_usuarios(self):
        frame_instrucciones = ttk.LabelFrame(self.tab_usuarios, text="👥 Gestión de Usuarios del Sistema", padding=15)
        frame_instrucciones.pack(fill='x', padx=10, pady=10)
        tk.Label(frame_instrucciones, text="Administre los usuarios del sistema, cree nuevos usuarios, modifique roles y permisos.", font=('Arial', 10), wraplength=1300, justify='left').pack()
        
        frame_acciones = ttk.LabelFrame(self.tab_usuarios, text="➕ Nuevo Usuario", padding=15)
        frame_acciones.pack(fill='x', padx=10, pady=10)
        
        frame_campos = tk.Frame(frame_acciones)
        frame_campos.pack(fill='x', pady=5)
        
        tk.Label(frame_campos, text="Usuario:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.entry_nuevo_usuario = ttk.Entry(frame_campos, width=20)
        self.entry_nuevo_usuario.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(frame_campos, text="Nombre Completo:", font=('Arial', 10, 'bold')).grid(row=0, column=2, sticky='w', padx=5, pady=5)
        self.entry_nuevo_nombre = ttk.Entry(frame_campos, width=30)
        self.entry_nuevo_nombre.grid(row=0, column=3, padx=5, pady=5)
        
        tk.Label(frame_campos, text="Rol:", font=('Arial', 10, 'bold')).grid(row=1, column=2, sticky='w', padx=5, pady=5)
        self.combo_nuevo_rol = ttk.Combobox(frame_campos, values=['Administrador', 'Usuario', 'Visualizador'], state='readonly', width=20)
        self.combo_nuevo_rol.grid(row=1, column=3, padx=5, pady=5)
        self.combo_nuevo_rol.current(1)
        
        tk.Label(frame_campos, text="Contraseña:", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.entry_nuevo_password = ttk.Entry(frame_campos, width=20, show='●')
        self.entry_nuevo_password.grid(row=2, column=1, padx=5, pady=5)
        
        tk.Label(frame_campos, text="Confirmar:", font=('Arial', 10, 'bold')).grid(row=2, column=2, sticky='w', padx=5, pady=5)
        self.entry_confirmar_password = ttk.Entry(frame_campos, width=20, show='●')
        self.entry_confirmar_password.grid(row=2, column=3, padx=5, pady=5)
        
        # NUEVOS CAMPOS DE PREGUNTA Y RESPUESTA DE SEGURIDAD
        tk.Label(frame_campos, text="Pregunta de Seguridad:", font=('Arial', 10, 'bold')).grid(row=3, column=0, sticky='w', padx=5, pady=5)
        self.combo_nueva_pregunta = ttk.Combobox(frame_campos, values=[
            "¿Cuál es el nombre de tu primera mascota?",
            "¿En qué ciudad naciste?",
            "¿Cuál es el nombre de tu escuela primaria?",
            "¿Cuál es tu comida favorita?"
        ], width=30, state='readonly')
        self.combo_nueva_pregunta.grid(row=3, column=1, padx=5, pady=5)
        self.combo_nueva_pregunta.current(0)
        
        tk.Label(frame_campos, text="Respuesta Segura:", font=('Arial', 10, 'bold')).grid(row=3, column=2, sticky='w', padx=5, pady=5)
        self.entry_nueva_respuesta = ttk.Entry(frame_campos, width=30)
        self.entry_nueva_respuesta.grid(row=3, column=3, padx=5, pady=5)

        ttk.Button(frame_acciones, text="✅ Crear Usuario", command=self.crear_nuevo_usuario).pack(pady=10)
        
        frame_botones = tk.Frame(self.tab_usuarios)
        frame_botones.pack(fill='x', padx=10, pady=(5, 0))
        ttk.Button(frame_botones, text="🔄 Actualizar Lista", command=self.actualizar_lista_usuarios).pack(side='left', padx=5)
        ttk.Button(frame_botones, text="🔓 Desbloquear Usuario", command=self.desbloquear_usuario_seleccionado).pack(side='left', padx=5)
        ttk.Button(frame_botones, text="❌ Desactivar Usuario", command=self.desactivar_usuario_seleccionado).pack(side='left', padx=5)
        ttk.Button(frame_botones, text="✅ Activar Usuario", command=self.activar_usuario_seleccionado).pack(side='left', padx=5)
        ttk.Button(frame_botones, text="🗑️ Eliminar Usuario", command=self.eliminar_usuario_seleccionado).pack(side='left', padx=5)

        frame_lista = ttk.LabelFrame(self.tab_usuarios, text="📋 Usuarios del Sistema", padding=10)
        frame_lista.pack(fill='both', expand=True, padx=10, pady=(5, 10))
        scroll_y = ttk.Scrollbar(frame_lista, orient='vertical')
        scroll_y.pack(side='right', fill='y')
        columnas = ('Usuario', 'Nombre Completo', 'Rol', 'Estado', 'Último Acceso', 'Fecha Creación')
        self.tree_usuarios = ttk.Treeview(frame_lista, columns=columnas, show='headings', yscrollcommand=scroll_y.set)
        scroll_y.config(command=self.tree_usuarios.yview)
        for col in columnas:
            self.tree_usuarios.heading(col, text=col)
            self.tree_usuarios.column(col, width=150, anchor='center')
        self.tree_usuarios.pack(fill='both', expand=True)
        self.actualizar_lista_usuarios()
    
    def crear_nuevo_usuario(self):
        if not self.verificar_permiso('gestion_usuarios'):
            messagebox.showerror("Error", "No tiene permisos para crear usuarios")
            return
            
        usuario = self.entry_nuevo_usuario.get().strip()
        nombre = self.entry_nuevo_nombre.get().strip()
        rol = self.combo_nuevo_rol.get()
        password = self.entry_nuevo_password.get()
        confirmar = self.entry_confirmar_password.get()
        pregunta = self.combo_nueva_pregunta.get().strip()
        respuesta = self.entry_nueva_respuesta.get().strip()
        
        if not all([usuario, nombre, password, confirmar, pregunta, respuesta]):
            messagebox.showwarning("Advertencia", "Complete todos los campos")
            return
        if password != confirmar:
            messagebox.showerror("Error", "Las contraseñas no coinciden")
            return
        if len(password) < 6:
            messagebox.showwarning("Advertencia", "La contraseña debe tener al menos 6 caracteres")
            return
            
        exito, mensaje = self.seguridad.crear_usuario(usuario, nombre, password, rol, pregunta, respuesta)
        if exito:
            messagebox.showinfo("Éxito", mensaje)
            self.registrar_actividad("Crear usuario", f"Usuario: {usuario}, Rol: {rol}")
            self.entry_nuevo_usuario.delete(0, 'end')
            self.entry_nuevo_nombre.delete(0, 'end')
            self.entry_nuevo_password.delete(0, 'end')
            self.entry_confirmar_password.delete(0, 'end')
            self.entry_nueva_respuesta.delete(0, 'end')
            self.combo_nueva_pregunta.current(0)
            self.actualizar_lista_usuarios()
        else:
            messagebox.showerror("Error", mensaje)
    
    def actualizar_lista_usuarios(self):
        for item in self.tree_usuarios.get_children():
            self.tree_usuarios.delete(item)
        for username, data in self.seguridad.usuarios.items():
            estado = "✅ Activo" if data.get('activo', False) else "❌ Inactivo"
            if data.get('intentos_fallidos', 0) >= 3:
                estado = "🔒 Bloqueado"
            self.tree_usuarios.insert('', 'end', values=(
                username, data.get('nombre_completo', ''),
                data.get('rol', ''), estado, data.get('ultimo_acceso', 'Nunca'),
                data.get('fecha_creacion', '')
            ))
    
    def desbloquear_usuario_seleccionado(self):
        if not self.verificar_permiso('gestion_usuarios'):
            messagebox.showerror("Error", "No tiene permisos para desbloquear usuarios")
            return
            
        seleccion = self.tree_usuarios.selection()
        if not seleccion: return
        username = self.tree_usuarios.item(seleccion[0])['values'][0]
        if username in self.seguridad.usuarios:
            self.seguridad.usuarios[username]['intentos_fallidos'] = 0
            self.seguridad.guardar_usuarios()
            self.registrar_actividad("Desbloquear usuario", f"Usuario: {username}")
            messagebox.showinfo("Éxito", f"Usuario {username} desbloqueado")
            self.actualizar_lista_usuarios()
    
    def desactivar_usuario_seleccionado(self):
        if not self.verificar_permiso('gestion_usuarios'):
            messagebox.showerror("Error", "No tiene permisos para desactivar usuarios")
            return
            
        seleccion = self.tree_usuarios.selection()
        if not seleccion: return
        username = self.tree_usuarios.item(seleccion[0])['values'][0]
        if username == 'admin':
            messagebox.showwarning("Advertencia", "No se puede desactivar el administrador")
            return
        if messagebox.askyesno("Confirmar", f"¿Desactivar usuario {username}?"):
            self.seguridad.usuarios[username]['activo'] = False
            self.seguridad.guardar_usuarios()
            self.registrar_actividad("Desactivar usuario", f"Usuario: {username}")
            self.actualizar_lista_usuarios()
    
    def activar_usuario_seleccionado(self):
        if not self.verificar_permiso('gestion_usuarios'):
            messagebox.showerror("Error", "No tiene permisos para activar usuarios")
            return
            
        seleccion = self.tree_usuarios.selection()
        if not seleccion: return
        username = self.tree_usuarios.item(seleccion[0])['values'][0]
        if username in self.seguridad.usuarios:
            self.seguridad.usuarios[username]['activo'] = True
            self.seguridad.guardar_usuarios()
            self.registrar_actividad("Activar usuario", f"Usuario: {username}")
            self.actualizar_lista_usuarios()
    
    def eliminar_usuario_seleccionado(self):
        if not self.verificar_permiso('gestion_usuarios'):
            messagebox.showerror("Error", "No tiene permisos para eliminar usuarios")
            return
            
        seleccion = self.tree_usuarios.selection()
        if not seleccion: return
        username = self.tree_usuarios.item(seleccion[0])['values'][0]
        if username == 'admin':
            messagebox.showwarning("Advertencia", "No se puede eliminar el administrador")
            return
        if messagebox.askyesno("Confirmar", f"¿ELIMINAR usuario {username}?\n\nEsta acción no se puede deshacer."):
            del self.seguridad.usuarios[username]
            self.seguridad.guardar_usuarios()
            self.registrar_actividad("Eliminar usuario", f"Usuario: {username}")
            self.actualizar_lista_usuarios()
    
    def crear_tab_log(self):
        if not self.verificar_permiso('gestion_usuarios'):
            return
            
        frame_filtros = ttk.LabelFrame(self.tab_log, text="🔍 Filtros", padding=10)
        frame_filtros.pack(fill='x', padx=10, pady=10)
        tk.Label(frame_filtros, text="Usuario:").pack(side='left', padx=5)
        self.combo_filtro_usuario = ttk.Combobox(frame_filtros, values=['Todos'] + list(self.seguridad.usuarios.keys()), state='readonly', width=15)
        self.combo_filtro_usuario.pack(side='left', padx=5)
        self.combo_filtro_usuario.current(0)
        ttk.Button(frame_filtros, text="🔄 Actualizar", command=self.actualizar_log).pack(side='left', padx=10)
        ttk.Button(frame_filtros, text="🗑️ Limpiar Log", command=self.limpiar_log).pack(side='left', padx=5)
        
        frame_tabla = ttk.LabelFrame(self.tab_log, text="📋 Actividades", padding=10)
        frame_tabla.pack(fill='both', expand=True, padx=10, pady=10)
        scroll_y = ttk.Scrollbar(frame_tabla, orient='vertical')
        scroll_y.pack(side='right', fill='y')
        columnas = ('Fecha/Hora', 'Usuario', 'Rol', 'Actividad', 'Detalles')
        self.tree_log = ttk.Treeview(frame_tabla, columns=columnas, show='headings', yscrollcommand=scroll_y.set)
        scroll_y.config(command=self.tree_log.yview)
        anchos = {'Fecha/Hora': 150, 'Usuario': 120, 'Rol': 120, 'Actividad': 200, 'Detalles': 400}
        for col in columnas:
            self.tree_log.heading(col, text=col)
            self.tree_log.column(col, width=anchos[col], anchor='w')
        self.tree_log.pack(fill='both', expand=True)
        self.actualizar_log()
    
    def actualizar_log(self):
        for item in self.tree_log.get_children():
            self.tree_log.delete(item)
        usuario_filtro = self.combo_filtro_usuario.get()
        for entry in reversed(self.log_actividades):
            if usuario_filtro == 'Todos' or entry['usuario'] == usuario_filtro:
                self.tree_log.insert('', 'end', values=(
                    entry['fecha_hora'], entry['usuario'], entry['rol'],
                    entry['actividad'], entry['detalles']
                ))
    
    def limpiar_log(self):
        if not self.verificar_permiso('gestion_usuarios'):
            messagebox.showerror("Error", "No tiene permisos para limpiar el log")
            return
            
        if messagebox.askyesno("Confirmar", "¿Limpiar TODO el log de actividades?"):
            self.log_actividades = []
            self.guardar_log_actividades()
            self.registrar_actividad("Limpiar log", "Log de actividades limpiado")
            self.actualizar_log()
    
    def cambiar_contraseña(self):
        ventana = tk.Toplevel(self.root)
        ventana.title("🔒 Cambiar Contraseña")
        ventana.geometry("400x400") 
        ventana.resizable(False, False)
        
        ventana.update_idletasks()
        x = (ventana.winfo_screenwidth() // 2) - (400 // 2)
        y = (ventana.winfo_screenheight() // 2) - (400 // 2)
        ventana.geometry(f'400x400+{x}+{y}')
        
        frame = ttk.Frame(ventana, padding=20)
        frame.pack(fill='both', expand=True)
        
        tk.Label(frame, text="🔑 Cambiar Contraseña", font=('Arial', 14, 'bold')).pack(pady=(0, 20))
        tk.Label(frame, text="Contraseña Actual:", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(10, 5))
        entry_actual = ttk.Entry(frame, show='●', width=30)
        entry_actual.pack(pady=(0, 10))
        
        tk.Label(frame, text="Nueva Contraseña:", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(10, 5))
        entry_nueva = ttk.Entry(frame, show='●', width=30)
        entry_nueva.pack(pady=(0, 10))
        
        tk.Label(frame, text="Confirmar Nueva:", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(10, 5))
        entry_confirmar = ttk.Entry(frame, show='●', width=30)
        entry_confirmar.pack(pady=(0, 20))
        
        def guardar_cambio():
            actual, nueva, confirmar = entry_actual.get(), entry_nueva.get(), entry_confirmar.get()
            
            if not all([actual, nueva, confirmar]): 
                return messagebox.showwarning("Advertencia", "Complete todos los campos", parent=ventana)
            if nueva != confirmar: 
                return messagebox.showerror("Error", "Las contraseñas no coinciden", parent=ventana)
            if len(nueva) < 6: 
                return messagebox.showwarning("Advertencia", "Mínimo 6 caracteres", parent=ventana)
            
            exito, mensaje = self.seguridad.cambiar_password(self.usuario_actual, actual, nueva)
            if exito:
                messagebox.showinfo("Éxito", mensaje, parent=ventana)
                self.registrar_actividad("Cambiar contraseña", "Contraseña actualizada")
                ventana.destroy()
            else:
                messagebox.showerror("Error", mensaje, parent=ventana)
        
        ttk.Button(frame, text="✅ Cambiar Contraseña", command=guardar_cambio).pack(pady=10)
    
    def cerrar_sesion(self):
        if messagebox.askyesno("Cerrar Sesión", "¿Está seguro de cerrar la sesión?"):
            self.registrar_actividad("Cierre de sesión")
            self.root.destroy()

    def crear_tab_gestion_año(self):
        self.frame_info_año = ttk.LabelFrame(self.tab_gestion_año, text=f"Información del Año {self.año_actual}", padding=15)
        self.frame_info_año.pack(fill='x', padx=10, pady=10)
        
        frame_cards = tk.Frame(self.frame_info_año, bg='white')
        frame_cards.pack(fill='x', pady=10)
        
        card1 = tk.Frame(frame_cards, bg='#2196F3', relief='raised', bd=3)
        card1.pack(side='left', fill='both', expand=True, padx=10)
        tk.Label(card1, text="AÑO ACTUAL", font=('Arial', 11, 'bold'), bg='#2196F3', fg='white').pack(pady=8)
        self.label_año_card = tk.Label(card1, text=str(self.año_actual), font=('Arial', 20, 'bold'), bg='#2196F3', fg='white')
        self.label_año_card.pack(pady=8)
        
        card2 = tk.Frame(frame_cards, bg='#4CAF50', relief='raised', bd=3)
        card2.pack(side='left', fill='both', expand=True, padx=10)
        tk.Label(card2, text="SOBRANTE AÑO ANTERIOR", font=('Arial', 11, 'bold'), bg='#4CAF50', fg='white').pack(pady=8)
        self.label_sobrante_anterior = tk.Label(card2, text="$0.00", font=('Arial', 20, 'bold'), bg='#4CAF50', fg='white')
        self.label_sobrante_anterior.pack(pady=8)
        
        card3 = tk.Frame(frame_cards, bg='#FF9800', relief='raised', bd=3)
        card3.pack(side='left', fill='both', expand=True, padx=10)
        tk.Label(card3, text="PRESUPUESTO ESTE AÑO", font=('Arial', 11, 'bold'), bg='#FF9800', fg='white').pack(pady=8)
        self.label_presupuesto_año_actual = tk.Label(card3, text="$0.00", font=('Arial', 20, 'bold'), bg='#FF9800', fg='white')
        self.label_presupuesto_año_actual.pack(pady=8)
        
        frame_acciones = ttk.LabelFrame(self.tab_gestion_año, text="Gestión de Años y Presupuestos", padding=15)
        frame_acciones.pack(fill='x', padx=10, pady=10)
        
        frame_botones = tk.Frame(frame_acciones, bg='white')
        frame_botones.pack(fill='x', pady=10)
        
        if self.puede_modificar():
            ttk.Button(frame_botones, text="Crear Presupuesto Nuevo Año", command=self.crear_presupuesto_nuevo_año, width=30).pack(side='left', padx=5)
        
        ttk.Separator(frame_acciones, orient='horizontal').pack(fill='x', pady=15)
        
        frame_selector_año = tk.Frame(frame_acciones, bg='white')
        frame_selector_año.pack(fill='x', pady=10)
        
        tk.Label(
            frame_selector_año,
            text="🔄 Cambiar Año de Trabajo:",
            font=('Arial', 12, 'bold'),
            bg='white'
        ).pack(side='left', padx=5)
        
        años_disponibles = sorted([int(y) for y in self.presupuestos_por_año.keys()], reverse=True)
        if not años_disponibles:
            años_disponibles = [self.año_actual]
        
        self.combo_año_trabajo = ttk.Combobox(
            frame_selector_año,
            values=años_disponibles,
            state='readonly',
            width=10,
            font=('Arial', 11)
        )
        self.combo_año_trabajo.pack(side='left', padx=5)
        if self.año_actual in años_disponibles:
            idx = años_disponibles.index(self.año_actual)
            self.combo_año_trabajo.current(idx)
        elif años_disponibles:
            self.combo_año_trabajo.current(0)
        
        ttk.Button(
            frame_selector_año,
            text="➡️ Cambiar a este Año",
            command=self.cambiar_año_de_trabajo
        ).pack(side='left', padx=10)
        
        self.label_info_año_selector = tk.Label(
            frame_selector_año,
            text="",
            font=('Arial', 9, 'italic'),
            fg='#666',
            bg='white'
        )
        self.label_info_año_selector.pack(side='left', padx=10)
        
        def actualizar_info_año_selector(event=None):
            año_sel = self.combo_año_trabajo.get()
            if año_sel:
                año = int(año_sel)
                if año == self.año_actual:
                    self.label_info_año_selector.config(
                        text="(Año actual)",
                        fg='#4CAF50'
                    )
                elif año < self.año_actual:
                    self.label_info_año_selector.config(
                        text="(Año pasado - solo consulta)",
                        fg='#FF9800'
                    )
                else:
                    self.label_info_año_selector.config(
                        text="(Año futuro)",
                        fg='#2196F3'
                    )
        
        self.combo_año_trabajo.bind('<<ComboboxSelected>>', actualizar_info_año_selector)
        actualizar_info_año_selector()
        
        if self.puede_modificar():
            ttk.Button(frame_botones, text="Ver Presupuestos Anteriores", command=self.ver_presupuestos_anteriores, width=30).pack(side='left', padx=5)
        
        ttk.Button(frame_botones, text="Actualizar Información", command=self.actualizar_info_año, width=30).pack(side='left', padx=5)
        
        if self.puede_modificar():
            frame_sobrantes = ttk.LabelFrame(self.tab_gestion_año, text="Gestión del Sobrante del Año Anterior", padding=15)
            frame_sobrantes.pack(fill='both', expand=True, padx=10, pady=10)
            
            tk.Label(frame_sobrantes, text="Indique qué hacer con el sobrante del año anterior:", font=('Arial', 11, 'bold')).pack(pady=10)
            
            self.opcion_sobrante_var = tk.StringVar(value="fondo_emergencia")
            opciones_frame = tk.Frame(frame_sobrantes, bg='white')
            opciones_frame.pack(fill='both', expand=True, pady=10)
            
            opciones = [
                ("Añadir al Fondo de Emergencias", "fondo_emergencia", "Guardar el dinero para situaciones imprevistas"),
                (" Distribuir en el Presupuesto del Nuevo Año", "distribuir", "Repartir proporcionalmente entre categorías"),
                ("Inversión en Infraestructura", "infraestructura", "Destinar a mejoras de la finca"),
                (" Capacitación y Tecnología", "capacitacion", "Invertir en formación y nuevas tecnologías"),
                (" Dividir según Porcentajes Personalizados", "personalizado", "Tú decides cómo repartir el dinero")
            ]
            
            for texto, valor, descripcion in opciones:
                frame_opcion = tk.Frame(opciones_frame, bg='#f5f5f5', relief='raised', bd=1)
                frame_opcion.pack(fill='x', padx=10, pady=5)
                ttk.Radiobutton(frame_opcion, text=texto, variable=self.opcion_sobrante_var, value=valor).pack(side='left', padx=10, pady=5)
                tk.Label(frame_opcion, text=descripcion, font=('Arial', 9), bg='#f5f5f5', fg='#666').pack(side='left', padx=10)
            
            ttk.Button(frame_sobrantes, text="Aplicar Decisión sobre Sobrante", command=self.aplicar_decision_sobrante, width=40).pack(pady=15)
        
        frame_historial = ttk.LabelFrame(self.tab_gestion_año, text="Historial de Años", padding=10)
        frame_historial.pack(fill='both', expand=True, padx=10, pady=10)
        
        scroll_y = ttk.Scrollbar(frame_historial, orient='vertical')
        scroll_y.pack(side='right', fill='y')
        columnas = ('Año', 'Presupuesto Total', 'Gastado', 'Sobrante', 'Decisión Sobrante')
        self.tree_historial_años = ttk.Treeview(frame_historial, columns=columnas, show='headings', yscrollcommand=scroll_y.set)
        scroll_y.config(command=self.tree_historial_años.yview)
        for col in columnas:
            self.tree_historial_años.heading(col, text=col)
            self.tree_historial_años.column(col, width=150, anchor='center')
        self.tree_historial_años.pack(fill='both', expand=True)
        
        self.actualizar_info_año()

    def crear_presupuesto_nuevo_año(self):
        if not self.puede_modificar():
            messagebox.showerror("Error", "No tiene permisos para crear presupuestos")
            return
            
        if str(self.año_actual) in self.presupuestos_por_año:
            if not messagebox.askyesno("Confirmar", 
                f"Ya existe un presupuesto para {self.año_actual}.\n¿Desea crear uno nuevo desde cero?"):
                return
        
        año_nuevo = simpledialog.askinteger(
            "Nuevo Año", 
            f"Ingrese el año para el nuevo presupuesto\n(Actual: {self.año_actual})", 
            minvalue=self.año_actual, 
            maxvalue=self.año_actual + 10
        )
        
        if not año_nuevo:
            return
        
        opciones = messagebox.askquestion(
            "Método de Creación", 
            "¿Desea copiar el presupuesto del año anterior?\n\n" +
            "SÍ: Copiar presupuesto del año anterior\n" +
            "NO: Crear presupuesto vacío desde cero", 
            icon='question'
        )
        
        if opciones == 'yes':
            año_anterior = año_nuevo - 1
            if str(año_anterior) in self.presupuestos_por_año:
                self.presupuestos_por_año[str(año_nuevo)] = dict(self.presupuestos_por_año[str(año_anterior)])
                messagebox.showinfo("Éxito", 
                    f"Presupuesto copiado del año {año_anterior} al año {año_nuevo}")
            else:
                messagebox.showwarning("Advertencia", 
                    f"No existe presupuesto para {año_anterior}.\nSe creará uno vacío.")
                self.presupuestos_por_año[str(año_nuevo)] = {}
        else:
            self.presupuestos_por_año[str(año_nuevo)] = {}
            messagebox.showinfo("Éxito", 
                f"Presupuesto vacío creado para el año {año_nuevo}")
        
        self.guardar_presupuestos_anuales()
        self.actualizar_info_año()
        self.registrar_actividad("Crear presupuesto anual", f"Año {año_nuevo}")
        
        if messagebox.askyesno("Cambiar Año", 
            f"¿Desea cambiar al año {año_nuevo} ahora?"):
            
            self.año_actual = año_nuevo
            self.presupuesto_mensual_por_mes = self.presupuestos_por_año.get(str(año_nuevo), {})
            
            if hasattr(self, 'label_año_actual'):
                self.label_año_actual.config(text=f"📅 Año: {self.año_actual}")
            
            if hasattr(self, 'label_año_card'):
                self.label_año_card.config(text=str(self.año_actual))
            
            if hasattr(self, 'combo_año_trabajo'):
                años_disponibles = sorted([int(y) for y in self.presupuestos_por_año.keys()], reverse=True)
                self.combo_año_trabajo['values'] = años_disponibles
                if año_nuevo in años_disponibles:
                    idx = años_disponibles.index(año_nuevo)
                    self.combo_año_trabajo.current(idx)
            
            self.actualizar_info_año()
            self.registrar_actividad("Cambiar año actual", f"Cambio a año {año_nuevo}")
            
            messagebox.showinfo("Éxito", 
                f"Ahora está trabajando con el año {año_nuevo}")

    def cambiar_año_de_trabajo(self):
        año_seleccionado = self.combo_año_trabajo.get()
        
        if not año_seleccionado:
            messagebox.showwarning("Advertencia", "Seleccione un año")
            return
        
        año = int(año_seleccionado)
        
        if año == self.año_actual:
            messagebox.showinfo("Información", 
                f"Ya está trabajando en el año {año}")
            return
        
        mensaje = f"¿Cambiar al año {año}?\n\n"
        
        if año < self.año_actual:
            mensaje += "⚠️ ADVERTENCIA: Es un año pasado\n"
            mensaje += "Podrá ver y consultar datos, pero se recomienda no modificar.\n\n"
        elif año > self.año_actual:
            mensaje += "ℹ️ Es un año futuro\n"
            mensaje += "Podrá configurar presupuestos anticipadamente.\n\n"
        
        mensaje += "Esto cambiará el año de trabajo del sistema."
        
        if messagebox.askyesno("Confirmar Cambio de Año", mensaje):
            año_anterior_sistema = self.año_actual
            self.año_actual = año
            
            if str(año) in self.presupuestos_por_año:
                self.presupuesto_mensual_por_mes = dict(self.presupuestos_por_año[str(año)])
            else:
                self.presupuesto_mensual_por_mes = {}
                messagebox.showinfo("Información", 
                    f"No hay presupuesto configurado para {año}.\n" +
                    "Puede crearlo en la pestaña de Presupuesto Mensual.")
            
            if hasattr(self, 'label_año_actual'):
                self.label_año_actual.config(text=f"📅 Año: {self.año_actual}")
            
            self.actualizar_info_año()
            self.registrar_actividad(
                "Cambiar año de trabajo", 
                f"De {año_anterior_sistema} a {año}"
            )
            
            self.actualizar_vistas_dependientes_año()
            
            messagebox.showinfo("Éxito", 
                f"Ahora está trabajando con el año {año}\n\n" +
                ("⚠️ Recuerde: Es un año pasado" if año < año_anterior_sistema else 
                "✅ Puede crear/editar presupuestos y gastos"))

    def actualizar_vistas_dependientes_año(self):
        if hasattr(self, 'fecha_var'):
            fecha_actual_año = datetime(self.año_actual, 1, 1).strftime('%Y-%m-%d')
            self.fecha_var.set(fecha_actual_año)

        if hasattr(self, 'actualizar_tabla_gastos'):
            try:
                self.actualizar_tabla_gastos()
            except:
                pass

        if hasattr(self, 'cargar_presupuesto_mes'):
            try:
                self.cargar_presupuesto_mes()
            except:
                pass

    def ver_presupuestos_anteriores(self):
        if not self.presupuestos_por_año:
            messagebox.showinfo("Sin Datos", "No hay presupuestos de años anteriores guardados")
            return
            
        ventana = tk.Toplevel(self.root)
        ventana.title("Presupuestos de Años Anteriores")
        ventana.geometry("800x600")
        
        frame_sel = ttk.Frame(ventana, padding=10)
        frame_sel.pack(fill='x')
        tk.Label(frame_sel, text="Seleccionar Año:", font=('Arial', 11, 'bold')).pack(side='left', padx=5)
        
        años_disponibles = sorted(self.presupuestos_por_año.keys(), reverse=True)
        combo_año = ttk.Combobox(frame_sel, values=años_disponibles, state='readonly', width=10)
        combo_año.pack(side='left', padx=5)
        if años_disponibles: combo_año.current(0)
        
        ttk.Button(frame_sel, text="Ver Detalles", command=lambda: self.mostrar_detalle_año(combo_año.get(), text_detalle)).pack(side='left', padx=10)
        
        frame_texto = ttk.Frame(ventana, padding=10)
        frame_texto.pack(fill='both', expand=True)
        scroll_y = ttk.Scrollbar(frame_texto, orient='vertical')
        scroll_y.pack(side='right', fill='y')
        
        text_detalle = tk.Text(frame_texto, height=30, width=90, font=('Courier', 10), yscrollcommand=scroll_y.set)
        text_detalle.pack(fill='both', expand=True)
        scroll_y.config(command=text_detalle.yview)
        
        if años_disponibles:
            self.mostrar_detalle_año(años_disponibles[0], text_detalle)

    def mostrar_detalle_año(self, año, text_widget):
        text_widget.delete('1.0', 'end')
        if not año or año not in self.presupuestos_por_año:
            text_widget.insert('1.0', "Seleccione un año válido")
            return
            
        presupuesto = self.presupuestos_por_año[año]
        texto = f"{'=' * 80}\nPRESUPUESTO DEL AÑO {año}\n{'=' * 80}\n\n"
        
        if not presupuesto:
            texto += "No hay presupuesto configurado para este año\n"
            text_widget.insert('1.0', texto)
            return
            
        total_año = 0
        for mes in self.meses:
            if mes in presupuesto:
                total_mes = sum(presupuesto[mes].values())
                total_año += total_mes
                texto += f"\n{mes.upper()}: ${total_mes:,.2f}\n{'-' * 80}\n"
                for categoria, monto in sorted(presupuesto[mes].items()):
                    texto += f"  {categoria:<40} ${monto:>12,.2f}\n"
        
        texto += f"\n{'=' * 80}\nTOTAL PRESUPUESTADO EN {año}: ${total_año:,.2f}\n{'=' * 80}\n"
        text_widget.insert('1.0', texto)

    def aplicar_decision_sobrante(self):
        if not self.puede_modificar():
            messagebox.showerror("Error", "No tiene permisos para aplicar decisiones sobre sobrantes")
            return
            
        año_anterior = self.año_actual - 1
        sobrante = self.calcular_sobrante_año(año_anterior)
        
        if sobrante <= 0:
            messagebox.showinfo("Sin Sobrante", f"No hay sobrante del año {año_anterior} para gestionar")
            return
            
        opcion = self.opcion_sobrante_var.get()
        
        if opcion == "fondo_emergencia":
            self.sobrantes_anuales[str(año_anterior)] = {'monto': sobrante, 'decision': 'Fondo de Emergencias', 'fecha': datetime.now().strftime('%Y-%m-%d')}
            messagebox.showinfo("Éxito", f"${sobrante:,.2f} guardado en Fondo de Emergencias")
        elif opcion == "distribuir":
            if not self.presupuesto_mensual_por_mes:
                return messagebox.showwarning("Advertencia", "Primero debe configurar el presupuesto del año actual")
            self.distribuir_sobrante_en_presupuesto(sobrante)
            self.sobrantes_anuales[str(año_anterior)] = {'monto': sobrante, 'decision': 'Distribuido en Presupuesto', 'fecha': datetime.now().strftime('%Y-%m-%d')}
            messagebox.showinfo("Éxito", f"${sobrante:,.2f} distribuido proporcionalmente")
        elif opcion == "infraestructura":
            if "Enero" not in self.presupuesto_mensual_por_mes: self.presupuesto_mensual_por_mes["Enero"] = {}
            if "Infraestructura" not in self.presupuesto_mensual_por_mes["Enero"]: self.presupuesto_mensual_por_mes["Enero"]["Infraestructura"] = 0
            self.presupuesto_mensual_por_mes["Enero"]["Infraestructura"] += sobrante
            self.sobrantes_anuales[str(año_anterior)] = {'monto': sobrante, 'decision': 'Inversión en Infraestructura', 'fecha': datetime.now().strftime('%Y-%m-%d')}
            messagebox.showinfo("Éxito", f"${sobrante:,.2f} añadido a Infraestructura en Enero")
        elif opcion == "capacitacion":
            if "Enero" not in self.presupuesto_mensual_por_mes: self.presupuesto_mensual_por_mes["Enero"] = {}
            self.presupuesto_mensual_por_mes["Enero"]["Capacitación y Tecnología"] = sobrante
            self.sobrantes_anuales[str(año_anterior)] = {'monto': sobrante, 'decision': 'Capacitación y Tecnología', 'fecha': datetime.now().strftime('%Y-%m-%d')}
            messagebox.showinfo("Éxito", f"${sobrante:,.2f} asignado a Capacitación y Tecnología")
        elif opcion == "personalizado":
            self.distribuir_sobrante_personalizado(sobrante, año_anterior)
            return
            
        self.guardar_sobrantes_anuales()
        self.guardar_datos()
        self.actualizar_info_año()
        self.registrar_actividad("Sobrante aplicado", f"Año {año_anterior}: {opcion}")

    def calcular_sobrante_año(self, año):
        presupuesto_año = self.presupuestos_por_año.get(str(año), {})
        if not presupuesto_año: return 0
        total_presupuestado = sum(sum(mes_data.values()) for mes_data in presupuesto_año.values())
        total_gastado = sum(t['monto'] for t in self.transacciones if datetime.strptime(t['fecha'], '%Y-%m-%d').year == año)
        return total_presupuestado - total_gastado

    def distribuir_sobrante_en_presupuesto(self, sobrante):
        if not self.presupuesto_mensual_por_mes: return
        total_presupuesto_actual = sum(sum(mes_data.values()) for mes_data in self.presupuesto_mensual_por_mes.values())
        if total_presupuesto_actual == 0: return
        for mes in self.presupuesto_mensual_por_mes:
            for categoria in self.presupuesto_mensual_por_mes[mes]:
                monto_actual = self.presupuesto_mensual_por_mes[mes][categoria]
                incremento = sobrante * (monto_actual / total_presupuesto_actual)
                self.presupuesto_mensual_por_mes[mes][categoria] += incremento
        self.guardar_datos()

    def distribuir_sobrante_personalizado(self, sobrante, año_anterior):
        ventana = tk.Toplevel(self.root)
        ventana.title(" Distribución Personalizada del Sobrante")
        ventana.geometry("700x600")
        
        tk.Label(ventana, text=f"Sobrante a Distribuir: ${sobrante:,.2f}", font=('Arial', 14, 'bold'), fg='#4CAF50').pack(pady=10)
        
        frame_container = ttk.Frame(ventana, padding=10)
        frame_container.pack(fill='both', expand=True)
        
        canvas = tk.Canvas(frame_container)
        scrollbar = ttk.Scrollbar(frame_container, orient="vertical", command=canvas.yview)
        frame_categorias = tk.Frame(canvas)
        frame_categorias.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=frame_categorias, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        porcentaje_entries, monto_labels = {}, {}
        todas_categorias = list(self.categorias_agricolas.keys()) + list(self.categorias_personalizadas.keys())
        
        for categoria in todas_categorias:
            frame = tk.Frame(frame_categorias, bg='#f5f5f5', relief='raised', bd=1)
            frame.pack(fill='x', padx=5, pady=3)
            tk.Label(frame, text=categoria, width=30, anchor='w', bg='#f5f5f5').pack(side='left', padx=5)
            tk.Label(frame, text="%:", bg='#f5f5f5').pack(side='left')
            entry = ttk.Entry(frame, width=10)
            entry.pack(side='left', padx=5)
            entry.insert(0, "0")
            porcentaje_entries[categoria] = entry
            label_monto = tk.Label(frame, text="$0.00", width=15, anchor='e', bg='#f5f5f5', fg='#666')
            label_monto.pack(side='left', padx=10)
            monto_labels[categoria] = label_monto
            entry.bind('<KeyRelease>', lambda e, cat=categoria: self.actualizar_monto_distribucion(porcentaje_entries[cat], monto_labels[cat], sobrante))
        
        frame_total = tk.Frame(ventana, bg='#e3f2fd', relief='raised', bd=2)
        frame_total.pack(fill='x', padx=10, pady=10)
        label_total_porcentaje = tk.Label(frame_total, text="Total: 0%", font=('Arial', 12, 'bold'), bg='#e3f2fd')
        label_total_porcentaje.pack(pady=5)
        
        def actualizar_total():
            total = sum(float(entry.get()) for entry in porcentaje_entries.values() if entry.get().replace('.','',1).isdigit())
            label_total_porcentaje.config(text=f"Total: {total:.1f}%", fg='#4CAF50' if abs(total - 100) < 0.01 else '#f44336')
            return total
            
        for entry in porcentaje_entries.values(): entry.bind('<KeyRelease>', lambda e: actualizar_total())
        
        def aplicar_distribucion():
            total = actualizar_total()
            if abs(total - 100) > 0.01: return messagebox.showerror("Error", f"Los porcentajes deben sumar 100%\nActual: {total:.1f}%")
            for categoria, entry in porcentaje_entries.items():
                try:
                    porcentaje = float(entry.get())
                    if porcentaje > 0:
                        monto = sobrante * (porcentaje / 100)
                        if "Enero" not in self.presupuesto_mensual_por_mes: self.presupuesto_mensual_por_mes["Enero"] = {}
                        if categoria not in self.presupuesto_mensual_por_mes["Enero"]: self.presupuesto_mensual_por_mes["Enero"][categoria] = 0
                        self.presupuesto_mensual_por_mes["Enero"][categoria] += monto
                except: pass
            self.sobrantes_anuales[str(año_anterior)] = {'monto': sobrante, 'decision': 'Distribución Personalizada', 'fecha': datetime.now().strftime('%Y-%m-%d')}
            self.guardar_sobrantes_anuales()
            self.guardar_datos()
            self.actualizar_info_año()
            messagebox.showinfo("Éxito", "Distribución aplicada correctamente")
            ventana.destroy()
            
        ttk.Button(ventana, text=" Aplicar Distribución", command=aplicar_distribucion).pack(pady=10)
        actualizar_total()

    def actualizar_monto_distribucion(self, entry, label, sobrante_total):
        try: label.config(text=f"${sobrante_total * (float(entry.get()) / 100):,.2f}")
        except: label.config(text="$0.00")

    def actualizar_info_año(self):
        if hasattr(self, 'frame_info_año'):
            self.frame_info_año.config(text=f"Información del Año {self.año_actual}")
        
        if hasattr(self, 'label_año_card'):
            self.label_año_card.config(text=str(self.año_actual))
        
        año_anterior = self.año_actual - 1
        sobrante_anterior = self.calcular_sobrante_año(año_anterior)
        self.label_sobrante_anterior.config(text=f"${sobrante_anterior:,.2f}")
        
        presupuesto_actual = sum(sum(m.values()) for m in self.presupuestos_por_año.get(str(self.año_actual), {}).values())
        self.label_presupuesto_año_actual.config(text=f"${presupuesto_actual:,.2f}")
        
        for item in self.tree_historial_años.get_children(): 
            self.tree_historial_años.delete(item)
        
        for año in sorted(self.presupuestos_por_año.keys(), reverse=True):
            pres_total = sum(sum(m.values()) for m in self.presupuestos_por_año[año].values())
            gastado = sum(t['monto'] for t in self.transacciones if datetime.strptime(t['fecha'], '%Y-%m-%d').year == int(año))
            sobrante = pres_total - gastado
            decision = self.sobrantes_anuales.get(año, {}).get('decision', 'N/A')
            self.tree_historial_años.insert('', 'end', values=(año, f"${pres_total:,.2f}", f"${gastado:,.2f}", f"${sobrante:,.2f}", decision))

    def crear_tab_categorias_custom(self):
        frame_instrucciones = ttk.LabelFrame(self.tab_categorias_custom, text="Información", padding=10)
        frame_instrucciones.pack(fill='x', padx=10, pady=10)
        tk.Label(frame_instrucciones, text="Agregue categorías o subcategorías personalizadas.", font=('Arial', 10)).pack()
        
        if self.puede_modificar():
            frame_acciones = ttk.LabelFrame(self.tab_categorias_custom, text=" Agregar Nueva Categoría", padding=15)
            frame_acciones.pack(fill='x', padx=10, pady=10)
            
            frame_nueva_cat = tk.Frame(frame_acciones)
            frame_nueva_cat.pack(fill='x', pady=5)
            tk.Label(frame_nueva_cat, text="Nombre:", font=('Arial', 10, 'bold')).pack(side='left', padx=5)
            self.entry_nueva_categoria = ttk.Entry(frame_nueva_cat, width=40)
            self.entry_nueva_categoria.pack(side='left', padx=5)
            ttk.Button(frame_nueva_cat, text=" Crear Categoría", command=self.agregar_nueva_categoria).pack(side='left', padx=10)
            
            frame_nueva_subcat = ttk.LabelFrame(self.tab_categorias_custom, text=" Agregar Subcategoría", padding=15)
            frame_nueva_subcat.pack(fill='x', padx=10, pady=10)
            
            frame_sub = tk.Frame(frame_nueva_subcat)
            frame_sub.pack(fill='x', pady=5)
            tk.Label(frame_sub, text="Categoría:", font=('Arial', 10, 'bold')).pack(side='left', padx=5)
            self.combo_cat_para_subcat = ttk.Combobox(frame_sub, state='readonly', width=30)
            self.combo_cat_para_subcat.pack(side='left', padx=5)
            tk.Label(frame_sub, text="Subcategoría:", font=('Arial', 10, 'bold')).pack(side='left', padx=10)
            self.entry_nueva_subcategoria = ttk.Entry(frame_sub, width=30)
            self.entry_nueva_subcategoria.pack(side='left', padx=5)
            ttk.Button(frame_sub, text=" Agregar Subcategoría", command=self.agregar_nueva_subcategoria).pack(side='left', padx=10)
            
            frame_eliminar = ttk.LabelFrame(self.tab_categorias_custom, text=" Eliminar Categoría o Subcategoría", padding=15)
            frame_eliminar.pack(fill='x', padx=10, pady=10)
            
            frame_elim = tk.Frame(frame_eliminar)
            frame_elim.pack(fill='x', pady=5)
            tk.Label(frame_elim, text="Categoría:").pack(side='left', padx=5)
            self.combo_cat_eliminar = ttk.Combobox(frame_elim, state='readonly', width=30)
            self.combo_cat_eliminar.pack(side='left', padx=5)
            self.combo_cat_eliminar.bind('<<ComboboxSelected>>', self.actualizar_subcats_eliminar)
            tk.Label(frame_elim, text="Subcategoría:").pack(side='left', padx=10)
            self.combo_subcat_eliminar = ttk.Combobox(frame_elim, state='readonly', width=30)
            self.combo_subcat_eliminar.pack(side='left', padx=5)
            ttk.Button(frame_elim, text=" Eliminar Categoría", command=self.eliminar_categoria).pack(side='left', padx=10)
            ttk.Button(frame_elim, text=" Eliminar Subcategoría", command=self.eliminar_subcategoria).pack(side='left', padx=5)
        
        frame_lista = ttk.LabelFrame(self.tab_categorias_custom, text=" Categorías y Subcategorías Actuales", padding=10)
        frame_lista.pack(fill='both', expand=True, padx=10, pady=10)
        
        frame_scroll = ttk.Frame(frame_lista)
        frame_scroll.pack(fill='both', expand=True)
        scroll_y = ttk.Scrollbar(frame_scroll, orient='vertical')
        scroll_y.pack(side='right', fill='y')
        self.text_categorias = tk.Text(frame_scroll, height=15, width=100, font=('Courier', 10), yscrollcommand=scroll_y.set)
        self.text_categorias.pack(fill='both', expand=True)
        scroll_y.config(command=self.text_categorias.yview)
        
        ttk.Button(self.tab_categorias_custom, text=" Actualizar Vista", command=self.actualizar_vista_categorias).pack(pady=10)
        
        self.actualizar_vista_categorias()

    def agregar_nueva_categoria(self):
        if not self.puede_modificar():
            messagebox.showerror("Error", "No tiene permisos para agregar categorías")
            return
            
        nombre = self.entry_nueva_categoria.get().strip()
        if not nombre: return messagebox.showwarning("Advertencia", "Debe ingresar un nombre")
        todas_categorias = {**self.categorias_agricolas, **self.categorias_personalizadas}
        if nombre in todas_categorias: return messagebox.showwarning("Advertencia", "Ya existe")
        self.categorias_personalizadas[nombre] = []
        self.guardar_categorias_personalizadas()
        self.entry_nueva_categoria.delete(0, 'end')
        self.actualizar_vista_categorias()
        self.actualizar_todas_categorias_combos() 
        messagebox.showinfo("Éxito", f"Categoría '{nombre}' creada")

    def agregar_nueva_subcategoria(self):
        if not self.puede_modificar():
            messagebox.showerror("Error", "No tiene permisos para agregar subcategorías")
            return
            
        categoria = self.combo_cat_para_subcat.get()
        subcategoria = self.entry_nueva_subcategoria.get().strip()
        if not categoria or not subcategoria: return messagebox.showwarning("Advertencia", "Complete campos")
        
        if categoria in self.categorias_personalizadas:
            if subcategoria in self.categorias_personalizadas[categoria]: return messagebox.showwarning("Advertencia", "Ya existe")
            self.categorias_personalizadas[categoria].append(subcategoria)
        elif categoria in self.categorias_agricolas:
            if categoria not in self.categorias_personalizadas: self.categorias_personalizadas[categoria] = list(self.categorias_agricolas[categoria])
            if subcategoria in self.categorias_personalizadas[categoria]: return messagebox.showwarning("Advertencia", "Ya existe")
            self.categorias_personalizadas[categoria].append(subcategoria)
            
        self.guardar_categorias_personalizadas()
        self.entry_nueva_subcategoria.delete(0, 'end')
        self.actualizar_vista_categorias()
        self.actualizar_todas_categorias_combos() 
        messagebox.showinfo("Éxito", f"Subcategoría agregada")

    def eliminar_categoria(self):
        if not self.puede_modificar():
            messagebox.showerror("Error", "No tiene permisos para eliminar categorías")
            return
            
        categoria = self.combo_cat_eliminar.get()
        if not categoria: return
        if categoria in self.categorias_agricolas and categoria not in self.categorias_personalizadas:
            return messagebox.showwarning("Advertencia", "No se pueden eliminar categorías predefinidas")
        if messagebox.askyesno("Confirmar", f"¿Eliminar '{categoria}'?"):
            del self.categorias_personalizadas[categoria]
            self.guardar_categorias_personalizadas()
            self.actualizar_vista_categorias()

    def eliminar_subcategoria(self):
        if not self.puede_modificar():
            messagebox.showerror("Error", "No tiene permisos para eliminar subcategorías")
            return
            
        categoria = self.combo_cat_eliminar.get()
        subcategoria = self.combo_subcat_eliminar.get()
        if not categoria or not subcategoria: return
        if messagebox.askyesno("Confirmar", f"¿Eliminar '{subcategoria}'?"):
            if categoria in self.categorias_agricolas and categoria not in self.categorias_personalizadas:
                self.categorias_personalizadas[categoria] = list(self.categorias_agricolas[categoria])
            if subcategoria in self.categorias_personalizadas.get(categoria, []):
                self.categorias_personalizadas[categoria].remove(subcategoria)
                self.guardar_categorias_personalizadas()
                self.actualizar_vista_categorias()
                self.actualizar_todas_categorias_combos() 

    def actualizar_subcats_eliminar(self, event=None):
        categoria = self.combo_cat_eliminar.get()
        if not categoria: self.combo_subcat_eliminar['values'] = []; return
        subcats = self.categorias_personalizadas.get(categoria, self.categorias_agricolas.get(categoria, []))
        self.combo_subcat_eliminar['values'] = subcats
        if subcats: self.combo_subcat_eliminar.current(0)

    def actualizar_vista_categorias(self):
        self.text_categorias.delete('1.0', 'end')
        todas_categorias = {cat: list(subcats) for cat, subcats in self.categorias_agricolas.items()}
        for cat, subcats in self.categorias_personalizadas.items():
            if cat in todas_categorias: todas_categorias[cat] = list(set(todas_categorias[cat] + subcats))
            else: todas_categorias[cat] = list(subcats)
            
        texto = "=" * 100 + "\nCATEGORÍAS Y SUBCATEGORÍAS ACTUALES\n" + "=" * 100 + "\n\n"
        for categoria in sorted(todas_categorias.keys()):
            tipo = " [PREDEFINIDA]" if categoria in self.categorias_agricolas and categoria not in self.categorias_personalizadas else " [PERSONALIZADA]" if categoria not in self.categorias_agricolas else " [MIXTA]"
            texto += f"\n {categoria}{tipo}\n" + "-" * 100 + "\n"
            subcats = todas_categorias[categoria]
            if subcats:
                for i, subcat in enumerate(sorted(subcats), 1): texto += f"  {i}. {subcat}\n"
            else: texto += "  (Sin subcategorías)\n"
            texto += "\n"
            
        self.text_categorias.insert('1.0', texto)
        lista_categorias = sorted(todas_categorias.keys())
        
        if hasattr(self, 'combo_cat_para_subcat'):
            self.combo_cat_para_subcat['values'] = lista_categorias
        if hasattr(self, 'combo_cat_eliminar'):
            self.combo_cat_eliminar['values'] = lista_categorias
        
        if lista_categorias:
            if hasattr(self, 'combo_cat_para_subcat'):
                self.combo_cat_para_subcat.current(0)
            if hasattr(self, 'combo_cat_eliminar'):
                self.combo_cat_eliminar.current(0)
                self.actualizar_subcats_eliminar()

    def crear_tab_presupuesto_mensual(self):
        frame_instrucciones = ttk.LabelFrame(self.tab_presupuesto_mensual, text=" Instrucciones", padding=10)
        frame_instrucciones.pack(fill='x', padx=10, pady=10)
        tk.Label(frame_instrucciones, text="Configure el presupuesto para cada mes y categoría.", font=('Arial', 10)).pack()
        
        frame_mes = ttk.Frame(self.tab_presupuesto_mensual)
        frame_mes.pack(fill='x', padx=10, pady=5)
        tk.Label(frame_mes, text="Seleccionar Mes:", font=('Arial', 12, 'bold')).pack(side='left', padx=5)
        self.combo_mes_presupuesto = ttk.Combobox(frame_mes, values=self.meses, state='readonly', width=15, font=('Arial', 11))
        self.combo_mes_presupuesto.pack(side='left', padx=5)
        self.combo_mes_presupuesto.current(0)
        self.combo_mes_presupuesto.bind('<<ComboboxSelected>>', self.cargar_presupuesto_mes)
        
        if self.puede_modificar():
            ttk.Button(frame_mes, text=" Copiar de Otro Mes", command=self.copiar_presupuesto_mes).pack(side='left', padx=5)
            ttk.Button(frame_mes, text=" Aplicar a Todos los Meses", command=self.aplicar_a_todos_meses).pack(side='left', padx=5)
            ttk.Button(frame_mes, text="🔄 Actualizar Categorías", command=self.regenerar_presupuesto_categorias).pack(side='left', padx=5)
        
        frame_categorias_container = ttk.LabelFrame(self.tab_presupuesto_mensual, text=" Presupuesto por Categoría", padding=10)
        frame_categorias_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        canvas = tk.Canvas(frame_categorias_container, bg='white')
        scrollbar = ttk.Scrollbar(frame_categorias_container, orient="vertical", command=canvas.yview)
        self.frame_categorias_presupuesto = tk.Frame(canvas, bg='white')
        self.frame_categorias_presupuesto.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.frame_categorias_presupuesto, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.presupuesto_mensual_entries = {}
        self.presupuesto_mensual_labels_modificado = {}
        
        self.regenerar_presupuesto_categorias()
        
        frame_botones = ttk.Frame(self.tab_presupuesto_mensual)
        frame_botones.pack(fill='x', padx=10, pady=10)
        
        if self.puede_modificar():
            ttk.Button(frame_botones, text=" Guardar Presupuesto del Mes", command=self.guardar_presupuesto_mes, style='Accent.TButton').pack(side='left', padx=5)
        
        ttk.Button(frame_botones, text=" Ver Resumen Anual", command=self.mostrar_resumen_anual).pack(side='left', padx=5)
        
        self.cargar_presupuesto_mes()
    
    def regenerar_presupuesto_categorias(self):
        for widget in self.frame_categorias_presupuesto.winfo_children():
            widget.destroy()
        
        self.presupuesto_mensual_entries.clear()
        self.presupuesto_mensual_labels_modificado.clear()
        
        todas_categorias = {}
        for cat, subcats in self.categorias_agricolas.items():
            todas_categorias[cat] = list(subcats)
        for cat, subcats in self.categorias_personalizadas.items():
            if cat in todas_categorias:
                todas_categorias[cat] = list(set(todas_categorias[cat] + subcats))
            else:
                todas_categorias[cat] = list(subcats)
        
        for row, categoria in enumerate(sorted(todas_categorias.keys())):
            frame_cat = tk.Frame(self.frame_categorias_presupuesto, bg='#e8f5e9', relief='raised', bd=2)
            frame_cat.grid(row=row, column=0, sticky='ew', padx=5, pady=5)
            self.frame_categorias_presupuesto.grid_columnconfigure(0, weight=1)
            
            tipo = ""
            if categoria in self.categorias_personalizadas and categoria not in self.categorias_agricolas:
                tipo = " [PERSONALIZADA]"
            
            tk.Label(frame_cat, text=categoria + tipo, font=('Arial', 11, 'bold'), bg='#e8f5e9', anchor='w').grid(row=0, column=0, sticky='w', padx=10, pady=5)
            tk.Label(frame_cat, text="Monto $:", bg='#e8f5e9').grid(row=0, column=1, padx=5)
            entry = ttk.Entry(frame_cat, width=15, font=('Arial', 10))
            entry.grid(row=0, column=2, padx=5)
            entry.insert(0, "0.00")
            self.presupuesto_mensual_entries[categoria] = entry
            
            if self.puede_modificar():
                label_mod = tk.Label(frame_cat, text="", bg='#e8f5e9', font=('Arial', 9, 'italic'), fg='red')
                label_mod.grid(row=0, column=3, padx=10)
                self.presupuesto_mensual_labels_modificado[categoria] = label_mod
                ttk.Button(frame_cat, text=" Modificar", command=lambda c=categoria: self.modificar_presupuesto_categoria(c)).grid(row=0, column=4, padx=5)
            else:
                entry.config(state='readonly')
        
        self.cargar_presupuesto_mes()

    def cargar_presupuesto_mes(self, event=None):
        mes = self.combo_mes_presupuesto.get()
        if mes in self.presupuesto_mensual_por_mes:
            presupuesto_mes = self.presupuesto_mensual_por_mes[mes]
            for categoria, entry in self.presupuesto_mensual_entries.items():
                entry.delete(0, tk.END)
                entry.insert(0, f"{presupuesto_mes.get(categoria, 0.00):.2f}")
                if self.puede_modificar():
                    if mes in self.presupuesto_modificado and categoria in self.presupuesto_modificado[mes] and self.presupuesto_modificado[mes][categoria]:
                        self.presupuesto_mensual_labels_modificado[categoria].config(text=" Modificado")
                    else: 
                        self.presupuesto_mensual_labels_modificado[categoria].config(text="")
        else:
            for entry in self.presupuesto_mensual_entries.values():
                entry.delete(0, tk.END)
                entry.insert(0, "0.00")
            if self.puede_modificar():
                for label in self.presupuesto_mensual_labels_modificado.values():
                    label.config(text="")

    def guardar_presupuesto_mes(self):
        if not self.puede_modificar():
            messagebox.showerror("Error", "No tiene permisos para guardar presupuestos")
            return
            
        mes = self.combo_mes_presupuesto.get()
        if mes not in self.presupuesto_mensual_por_mes: self.presupuesto_mensual_por_mes[mes] = {}
        for categoria, entry in self.presupuesto_mensual_entries.items():
            try: self.presupuesto_mensual_por_mes[mes][categoria] = float(entry.get())
            except ValueError: return messagebox.showerror("Error", f"Monto inválido en '{categoria}'")
        self.guardar_datos()
        self.registrar_actividad("Guardar presupuesto", f"Mes: {mes}")
        messagebox.showinfo("Éxito", f"Presupuesto de {mes} guardado correctamente")

    def modificar_presupuesto_categoria(self, categoria):
        if not self.puede_modificar():
            messagebox.showerror("Error", "No tiene permisos para modificar presupuestos")
            return
            
        mes = self.combo_mes_presupuesto.get()
        entry = self.presupuesto_mensual_entries[categoria]
        nuevo_monto = simpledialog.askfloat("Modificar Presupuesto", f"Ingrese nuevo presupuesto para '{categoria}' en {mes}:", initialvalue=float(entry.get()), minvalue=0.0)
        if nuevo_monto is not None:
            entry.delete(0, tk.END); entry.insert(0, f"{nuevo_monto:.2f}")
            if mes not in self.presupuesto_modificado: self.presupuesto_modificado[mes] = {}
            self.presupuesto_modificado[mes][categoria] = True
            self.presupuesto_mensual_labels_modificado[categoria].config(text=" Modificado")

    def copiar_presupuesto_mes(self):
        if not self.puede_modificar():
            messagebox.showerror("Error", "No tiene permisos para copiar presupuestos")
            return
            
        mes_destino = self.combo_mes_presupuesto.get()
        ventana = tk.Toplevel(self.root)
        ventana.title("Copiar Presupuesto")
        ventana.geometry("300x150")
        
        tk.Label(ventana, text=f"Copiar presupuesto a {mes_destino} desde:", font=('Arial', 11, 'bold')).pack(pady=10)
        combo_mes_origen = ttk.Combobox(ventana, values=self.meses, state='readonly', width=15)
        combo_mes_origen.pack(pady=10)
        combo_mes_origen.current(0)
        
        def copiar():
            mes_origen = combo_mes_origen.get()
            if mes_origen in self.presupuesto_mensual_por_mes:
                for categoria, monto in self.presupuesto_mensual_por_mes[mes_origen].items():
                    if categoria in self.presupuesto_mensual_entries:
                        self.presupuesto_mensual_entries[categoria].delete(0, tk.END)
                        self.presupuesto_mensual_entries[categoria].insert(0, f"{monto:.2f}")
                ventana.destroy()
                
        ttk.Button(ventana, text="Copiar", command=copiar).pack(pady=10)

    def aplicar_a_todos_meses(self):
        if not self.puede_modificar():
            messagebox.showerror("Error", "No tiene permisos para aplicar presupuestos")
            return
            
        if messagebox.askyesno("Confirmar", "¿Aplicar este presupuesto a todos los meses?"):
            presupuesto_actual = {}
            for categoria, entry in self.presupuesto_mensual_entries.items():
                try: presupuesto_actual[categoria] = float(entry.get())
                except: return messagebox.showerror("Error", "Montos inválidos")
            for mes in self.meses: self.presupuesto_mensual_por_mes[mes] = presupuesto_actual.copy()
            self.guardar_datos()
            messagebox.showinfo("Éxito", "Presupuesto aplicado a todos los meses")

    def mostrar_resumen_anual(self):
        ventana = tk.Toplevel(self.root)
        ventana.title("Resumen Presupuesto Anual")
        ventana.geometry("800x600")
        
        text = scrolledtext.ScrolledText(ventana, font=('Courier', 10), wrap=tk.WORD)
        text.pack(fill='both', expand=True, padx=10, pady=10)
        text.insert('end', "=" * 80 + "\nRESUMEN DE PRESUPUESTO ANUAL\n".center(80) + "=" * 80 + "\n\n")
        
        total_anual_por_categoria = defaultdict(float)
        for mes in self.meses:
            if mes in self.presupuesto_mensual_por_mes:
                text.insert('end', f"\n{mes.upper()}\n" + "-" * 80 + "\n")
                total_mes = 0
                for categoria, monto in self.presupuesto_mensual_por_mes[mes].items():
                    text.insert('end', f"  {categoria:40s} ${monto:>12,.2f}\n")
                    total_mes += monto
                    total_anual_por_categoria[categoria] += monto
                text.insert('end', f"\n  {'TOTAL MES':40s} ${total_mes:>12,.2f}\n")
        text.config(state='disabled')

    def crear_tab_proveedores(self):
            # --- INICIO NUEVO: Contenedor con Scroll para toda la pestaña ---
            canvas_main = tk.Canvas(self.tab_proveedores)
            scrollbar_main = ttk.Scrollbar(self.tab_proveedores, orient="vertical", command=canvas_main.yview)
            scrollable_frame = ttk.Frame(canvas_main)

            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas_main.configure(scrollregion=canvas_main.bbox("all"))
            )

            frame_id = canvas_main.create_window((0, 0), window=scrollable_frame, anchor="nw")
            
            # Esto asegura que el frame interno ocupe todo el ancho disponible
            def on_canvas_configure(event):
                canvas_main.itemconfig(frame_id, width=event.width)
            canvas_main.bind("<Configure>", on_canvas_configure)

            canvas_main.configure(yscrollcommand=scrollbar_main.set)

            canvas_main.pack(side="left", fill="both", expand=True)
            scrollbar_main.pack(side="right", fill="y")
            # --- FIN NUEVO ---

            frame_instrucciones = ttk.LabelFrame(
                scrollable_frame, # Modificado: ahora se asigna al scrollable_frame
                text="🏪 Catálogo de Proveedores",
                padding=15
            )
            frame_instrucciones.pack(fill='x', padx=10, pady=10)
            
            tk.Label(
                frame_instrucciones,
                text="Gestione sus proveedores y las categorías de productos/servicios que ofrecen.",
                font=('Arial', 10)
            ).pack()
            
            if self.puede_modificar():
                frame_form = ttk.LabelFrame(
                    scrollable_frame, # Modificado: ahora se asigna al scrollable_frame
                    text="➕ Agregar/Editar Proveedor",
                    padding=15
                )
                frame_form.pack(fill='x', padx=10, pady=10)
                
                row = 0
                
                tk.Label(frame_form, text="Nombre:", font=('Arial', 10, 'bold')).grid(
                    row=row, column=0, sticky='w', padx=5, pady=5)
                self.entry_proveedor_nombre = ttk.Entry(frame_form, width=30)
                self.entry_proveedor_nombre.grid(row=row, column=1, padx=5, pady=5)
                
                tk.Label(frame_form, text="Teléfono:", font=('Arial', 10, 'bold')).grid(
                    row=row, column=2, sticky='w', padx=5, pady=5)
                self.entry_proveedor_telefono = ttk.Entry(frame_form, width=20)
                vcmd = (self.root.register(self.validar_solo_numeros), '%P')
                self.entry_proveedor_telefono.config(validate='key', validatecommand=vcmd)
                self.entry_proveedor_telefono.grid(row=row, column=3, padx=5, pady=5)
                
                row += 1
                
                tk.Label(frame_form, text="Dirección:", font=('Arial', 10, 'bold')).grid(
                    row=row, column=0, sticky='w', padx=5, pady=5)
                self.entry_proveedor_direccion = ttk.Entry(frame_form, width=50)
                self.entry_proveedor_direccion.grid(row=row, column=1, columnspan=3, 
                                                sticky='ew', padx=5, pady=5)
                
                row += 1
                
                tk.Label(frame_form, text="Notas:", font=('Arial', 10, 'bold')).grid(
                    row=row, column=0, sticky='nw', padx=5, pady=5)
                self.text_proveedor_notas = tk.Text(frame_form, height=3, width=50)
                self.text_proveedor_notas.grid(row=row, column=1, columnspan=3, 
                                            sticky='ew', padx=5, pady=5)
                
                row += 1
                
                tk.Label(
                    frame_form,
                    text="📦 Categorías que ofrece (marque todas las que apliquen):",
                    font=('Arial', 11, 'bold'),
                    fg='#2d5016'
                ).grid(row=row, column=0, columnspan=4, sticky='w', padx=5, pady=(15, 5))
                
                row += 1
                
                frame_categorias_scroll = tk.Frame(frame_form)
                frame_categorias_scroll.grid(row=row, column=0, columnspan=4, 
                                            sticky='nsew', padx=5, pady=5)
                
                canvas_cat = tk.Canvas(frame_categorias_scroll, height=200)
                scrollbar_cat = ttk.Scrollbar(frame_categorias_scroll, orient="vertical", 
                                            command=canvas_cat.yview)
                frame_categorias_checks = tk.Frame(canvas_cat)
                
                frame_categorias_checks.bind(
                    "<Configure>",
                    lambda e: canvas_cat.configure(scrollregion=canvas_cat.bbox("all"))
                )
                
                canvas_cat.create_window((0, 0), window=frame_categorias_checks, anchor="nw")
                canvas_cat.configure(yscrollcommand=scrollbar_cat.set)
                self.frame_categorias_prov = frame_categorias_checks
                self.canvas_categorias_prov = canvas_cat
                
                canvas_cat.pack(side="left", fill="both", expand=True)
                scrollbar_cat.pack(side="right", fill="y")
                
                self.proveedor_categorias_vars = {}
                
                todas_cats = {**self.categorias_agricolas, **self.categorias_personalizadas}
                
                check_row = 0
                for categoria, subcategorias in sorted(todas_cats.items()):
                    frame_cat = tk.LabelFrame(
                        frame_categorias_checks,
                        text=categoria,
                        font=('Arial', 10, 'bold'),
                        padx=10,
                        pady=5
                    )
                    frame_cat.grid(row=check_row, column=0, sticky='ew', padx=5, pady=5)
                    
                    var_cat = tk.BooleanVar()
                    self.proveedor_categorias_vars[categoria] = {
                        'principal': var_cat,
                        'subcategorias': {}
                    }
                    
                    tk.Checkbutton(
                        frame_cat,
                        text=f"✓ {categoria} (todas)",
                        variable=var_cat,
                        font=('Arial', 9, 'bold'),
                        command=lambda c=categoria: self.toggle_todas_subcategorias(c)
                    ).pack(anchor='w')
                    
                    for subcat in subcategorias:
                        var_subcat = tk.BooleanVar()
                        self.proveedor_categorias_vars[categoria]['subcategorias'][subcat] = var_subcat
                        
                        tk.Checkbutton(
                            frame_cat,
                            text=f"  • {subcat}",
                            variable=var_subcat,
                            font=('Arial', 9)
                        ).pack(anchor='w', padx=20)
                    
                    check_row += 1
                
                row += 1
                
                frame_botones = tk.Frame(frame_form)
                frame_botones.grid(row=row, column=0, columnspan=4, pady=15)
                
                ttk.Button(
                    frame_botones,
                    text="💾 Guardar Proveedor",
                    command=self.guardar_proveedor
                ).pack(side='left', padx=5)
                
                ttk.Button(
                    frame_botones,
                    text="🗑️ Eliminar Seleccionado",
                    command=self.eliminar_proveedor
                ).pack(side='left', padx=5)
                
                ttk.Button(
                    frame_botones,
                    text="🔄 Limpiar Formulario",
                    command=self.limpiar_form_proveedor
                ).pack(side='left', padx=5)
                
                ttk.Button(
                    frame_botones,
                    text="🔄 Refrescar Categorías",
                    command=self.refrescar_categorias_proveedores
                ).pack(side='left', padx=5)
            
            frame_lista = ttk.LabelFrame(
                scrollable_frame, # Modificado: ahora se asigna al scrollable_frame
                text="📋 Lista de Proveedores",
                padding=10
            )
            # Hacemos que la tabla tenga una altura mínima para no aplastarse con el scroll
            frame_lista.pack(fill='both', expand=True, padx=10, pady=10, ipady=100) 
            
            scroll_y = ttk.Scrollbar(frame_lista, orient='vertical')
            scroll_y.pack(side='right', fill='y')
            
            columnas = ('ID', 'Nombre', 'Teléfono', 'Categorías', 'Dirección')
            self.tree_proveedores = ttk.Treeview(
                frame_lista,
                columns=columnas,
                show='headings',
                yscrollcommand=scroll_y.set
            )
            scroll_y.config(command=self.tree_proveedores.yview)
            
            anchos = {'ID': 50, 'Nombre': 200, 'Teléfono': 120, 
                    'Categorías': 400, 'Dirección': 250}
            for col in columnas:
                self.tree_proveedores.heading(col, text=col)
                self.tree_proveedores.column(col, width=anchos[col], anchor='w')
            
            self.tree_proveedores.pack(fill='both', expand=True)
            
            if self.puede_modificar():
                self.tree_proveedores.bind('<Double-Button-1>', self.cargar_proveedor_seleccionado)
            
            self.actualizar_lista_proveedores()

    def refrescar_categorias_proveedores(self):
        if not self.puede_modificar():
            messagebox.showerror("Error", "No tiene permisos para modificar proveedores")
            return
            
        self.actualizar_todas_categorias_combos()
        if not hasattr(self, 'frame_categorias_prov'):
            messagebox.showinfo("Info", "Primero abra el formulario de proveedores.")
            return
            
        for widget in self.frame_categorias_prov.winfo_children():
            widget.destroy()
            
        self.proveedor_categorias_vars = {}
        todas_cats = {cat: list(subcats) for cat, subcats in self.categorias_agricolas.items()}
        for cat, subcats in self.categorias_personalizadas.items():
            if cat in todas_cats:
                todas_cats[cat] = list(set(todas_cats[cat] + list(subcats)))
            else:
                todas_cats[cat] = list(subcats)
                
        check_row = 0
        for categoria, subcategorias in sorted(todas_cats.items()):
            frame_cat = tk.LabelFrame(
                self.frame_categorias_prov, text=categoria,
                font=('Arial', 10, 'bold'), padx=10, pady=5
            )
            frame_cat.grid(row=check_row, column=0, sticky='ew', padx=5, pady=5)
            var_cat = tk.BooleanVar()
            self.proveedor_categorias_vars[categoria] = {'principal': var_cat, 'subcategorias': {}}
            tk.Checkbutton(
                frame_cat, text=f"✓ {categoria} (todas)", variable=var_cat,
                font=('Arial', 9, 'bold'),
                command=lambda c=categoria: self.toggle_todas_subcategorias(c)
            ).pack(anchor='w')
            for subcat in subcategorias:
                var_subcat = tk.BooleanVar()
                self.proveedor_categorias_vars[categoria]['subcategorias'][subcat] = var_subcat
                tk.Checkbutton(
                    frame_cat, text=f"  • {subcat}", variable=var_subcat, font=('Arial', 9)
                ).pack(anchor='w', padx=20)
            check_row += 1
            
        if hasattr(self, 'canvas_categorias_prov'):
            self.frame_categorias_prov.update_idletasks()
            self.canvas_categorias_prov.configure(
                scrollregion=self.canvas_categorias_prov.bbox("all")
            )
        messagebox.showinfo("Actualizado", "✅ Categorías de proveedores actualizadas correctamente.")

    def toggle_todas_subcategorias(self, categoria):
        if not self.puede_modificar():
            return
            
        valor = self.proveedor_categorias_vars[categoria]['principal'].get()
        for subcat_var in self.proveedor_categorias_vars[categoria]['subcategorias'].values():
            subcat_var.set(valor)

    def guardar_proveedor(self):
        if not self.puede_modificar():
            messagebox.showerror("Error", "No tiene permisos para guardar proveedores")
            return
            
        nombre = self.entry_proveedor_nombre.get().strip()
        
        if not nombre:
            messagebox.showwarning("Advertencia", "Debe ingresar el nombre del proveedor")
            return
        
        categorias_seleccionadas = {}
        
        for categoria, vars_dict in self.proveedor_categorias_vars.items():
            subcats_seleccionadas = []
            
            for subcat, var in vars_dict['subcategorias'].items():
                if var.get():
                    subcats_seleccionadas.append(subcat)
            
            if subcats_seleccionadas:
                categorias_seleccionadas[categoria] = subcats_seleccionadas
        
        if not categorias_seleccionadas:
            messagebox.showwarning("Advertencia", 
                "Debe seleccionar al menos una categoría/subcategoría")
            return
        
        proveedor_id = None
        for pid, prov in self.proveedores.items():
            if prov['nombre'].lower() == nombre.lower():
                proveedor_id = pid
                break
        
        if proveedor_id is None:
            proveedor_id = str(len(self.proveedores) + 1)
        
        self.proveedores[proveedor_id] = {
            'nombre': nombre,
            'telefono': self.entry_proveedor_telefono.get().strip(),
            'direccion': self.entry_proveedor_direccion.get().strip(),
            'notas': self.text_proveedor_notas.get('1.0', 'end').strip(),
            'categorias': categorias_seleccionadas,
            'fecha_registro': datetime.now().strftime('%Y-%m-%d')
        }
        
        self.guardar_datos()
        self.actualizar_lista_proveedores()
        self.limpiar_form_proveedor()
        
        self.registrar_actividad("Guardar proveedor", f"Proveedor: {nombre}")
        messagebox.showinfo("Éxito", f"Proveedor '{nombre}' guardado correctamente")

    def cargar_proveedor_seleccionado(self, event):
        if not self.puede_modificar():
            return
            
        seleccion = self.tree_proveedores.selection()
        if not seleccion:
            return
        
        item = self.tree_proveedores.item(seleccion[0])
        prov_id = str(item['values'][0])
        
        if prov_id not in self.proveedores:
            return
        
        prov = self.proveedores[prov_id]
        
        self.limpiar_form_proveedor()
        
        self.entry_proveedor_nombre.insert(0, prov['nombre'])
        self.entry_proveedor_telefono.insert(0, prov.get('telefono', ''))
        self.entry_proveedor_direccion.insert(0, prov.get('direccion', ''))
        self.text_proveedor_notas.insert('1.0', prov.get('notas', ''))
        
        categorias = prov.get('categorias', {})
        
        for categoria, subcats in categorias.items():
            if categoria in self.proveedor_categorias_vars:
                for subcat in subcats:
                    if subcat in self.proveedor_categorias_vars[categoria]['subcategorias']:
                        self.proveedor_categorias_vars[categoria]['subcategorias'][subcat].set(True)

    def limpiar_form_proveedor(self):
        if not self.puede_modificar():
            return
            
        self.entry_proveedor_nombre.delete(0, 'end')
        self.entry_proveedor_telefono.delete(0, 'end')
        self.entry_proveedor_direccion.delete(0, 'end')
        self.text_proveedor_notas.delete('1.0', 'end')
        
        for vars_dict in self.proveedor_categorias_vars.values():
            vars_dict['principal'].set(False)
            for var in vars_dict['subcategorias'].values():
                var.set(False)

    def actualizar_lista_proveedores(self):
        for item in self.tree_proveedores.get_children():
            self.tree_proveedores.delete(item)
        
        for prov_id, prov in self.proveedores.items():
            cats_str = []
            for cat, subcats in prov.get('categorias', {}).items():
                cats_str.append(f"{cat}: {', '.join(subcats[:3])}")
                if len(subcats) > 3:
                    cats_str[-1] += "..."
            
            self.tree_proveedores.insert('', 'end', values=(
                prov_id,
                prov['nombre'],  
                prov.get('telefono', ''),
                ' | '.join(cats_str),
                prov.get('direccion', '')[:50]
            ))
    
    def eliminar_proveedor(self):
        if not self.puede_modificar():
            messagebox.showerror("Error", "No tiene permisos para eliminar proveedores")
            return
            
        seleccion = self.tree_proveedores.selection()
        
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un proveedor para eliminar")
            return
        
        item = self.tree_proveedores.item(seleccion[0])
        prov_id = str(item['values'][0])
        prov_nombre = item['values'][1]
        
        if not messagebox.askyesno("Confirmar Eliminación",
            f"¿Está seguro de eliminar el proveedor?\n\n" +
            f"Nombre: {prov_nombre}\n\n" +
            "Esta acción no se puede deshacer."):
            return
        
        if prov_id in self.proveedores:
            del self.proveedores[prov_id]
            self.guardar_datos()
            self.actualizar_lista_proveedores()
            self.limpiar_form_proveedor()
            self.registrar_actividad("Eliminar proveedor", f"Proveedor: {prov_nombre}")
            messagebox.showinfo("Éxito", f"Proveedor '{prov_nombre}' eliminado correctamente")
        else:
            messagebox.showerror("Error", "Proveedor no encontrado")

    def crear_tab_registro(self):
        frame_superior = ttk.LabelFrame(self.tab_registro, text=" Registrar Nuevo Gasto", padding=15)
        frame_superior.pack(fill='x', padx=10, pady=10)
        
        fila1 = tk.Frame(frame_superior, bg='white')
        fila1.pack(fill='x', pady=5)
        
        tk.Label(fila1, text="Fecha:", bg='white').pack(side='left', padx=5)
        self.entry_fecha = ttk.Entry(fila1, width=12)
        self.entry_fecha.pack(side='left', padx=5)
        self.entry_fecha.insert(0, datetime.now().strftime('%Y-%m-%d'))
        
        tk.Label(fila1, text="Categoría:", bg='white').pack(side='left', padx=15)
        todas_cats_gasto = sorted(list({**self.categorias_agricolas, **self.categorias_personalizadas}.keys()))
        self.combo_categoria = ttk.Combobox(fila1, values=todas_cats_gasto, state='readonly', width=25)
        self.combo_categoria.pack(side='left', padx=5)
        self.combo_categoria.bind('<<ComboboxSelected>>', self.actualizar_subcategorias)
        
        tk.Label(fila1, text="Subcategoría:", bg='white').pack(side='left', padx=15)
        self.combo_subcategoria = ttk.Combobox(fila1, state='readonly', width=20)
        self.combo_subcategoria.pack(side='left', padx=5)
        
        fila2 = tk.Frame(frame_superior, bg='white')
        fila2.pack(fill='x', pady=5)
        
        tk.Label(fila2, text="Monto $:", bg='white').pack(side='left', padx=5)
        self.entry_monto = ttk.Entry(fila2, width=15)
        self.entry_monto.pack(side='left', padx=5)
        
        tk.Label(fila2, text="Proveedor:", bg='white').pack(side='left', padx=15)
        nombres_proveedores = [p['nombre'] for p in self.proveedores.values()]
        self.combo_proveedor = ttk.Combobox(fila2, values=nombres_proveedores, width=25)
        self.combo_proveedor.pack(side='left', padx=5)
        
        tk.Label(fila2, text="Descripción:", bg='white').pack(side='left', padx=15)
        self.entry_descripcion = ttk.Entry(fila2, width=35)
        self.entry_descripcion.pack(side='left', padx=5)
        
        self.frame_advertencia = tk.Frame(frame_superior, bg='#ffebee', relief='ridge', bd=2)
        self.label_advertencia = tk.Label(self.frame_advertencia, text="", font=('Arial', 10, 'bold'), bg='#ffebee', fg='#c62828')
        self.label_advertencia.pack(pady=5, padx=10)
        
        frame_botones = tk.Frame(frame_superior, bg='white')
        frame_botones.pack(fill='x', pady=10)
        
        if self.puede_modificar():
            ttk.Button(frame_botones, text=" Registrar Gasto", command=self.registrar_gasto).pack(side='left', padx=5)
            ttk.Button(frame_botones, text=" Limpiar", command=self.limpiar_campos_gasto).pack(side='left', padx=5)
            ttk.Button(frame_botones, text=" Eliminar Seleccionado", command=self.eliminar_gasto).pack(side='left', padx=5)
        
        ttk.Button(frame_botones, text="🔄 Refrescar Categorías", command=self.refrescar_categorias_gasto).pack(side='left', padx=10)
        
        frame_tabla = ttk.LabelFrame(self.tab_registro, text=" Gastos Registrados", padding=10)
        frame_tabla.pack(fill='both', expand=True, padx=10, pady=10)
        
        scroll_y, scroll_x = ttk.Scrollbar(frame_tabla, orient='vertical'), ttk.Scrollbar(frame_tabla, orient='horizontal')
        self.tree_gastos = ttk.Treeview(frame_tabla, columns=('fecha', 'categoria', 'subcategoria', 'monto', 'proveedor', 'descripcion'), show='headings', yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        scroll_y.config(command=self.tree_gastos.yview)
        scroll_x.config(command=self.tree_gastos.xview)
        
        for col, width in zip(('fecha', 'categoria', 'subcategoria', 'monto', 'proveedor', 'descripcion'), (100, 180, 150, 120, 180, 250)):
            self.tree_gastos.heading(col, text=col.capitalize())
            self.tree_gastos.column(col, width=width)
            
        self.tree_gastos.grid(row=0, column=0, sticky='nsew')
        scroll_y.grid(row=0, column=1, sticky='ns')
        scroll_x.grid(row=1, column=0, sticky='ew')
        frame_tabla.grid_rowconfigure(0, weight=1)
        frame_tabla.grid_columnconfigure(0, weight=1)
        
        self.actualizar_tabla_gastos()

    def actualizar_subcategorias(self, event=None):
        categoria = self.combo_categoria.get()
        todas_cats = {cat: list(subcats) for cat, subcats in self.categorias_agricolas.items()}
        for cat, subcats in self.categorias_personalizadas.items():
            if cat in todas_cats:
                todas_cats[cat] = list(set(todas_cats[cat] + list(subcats)))
            else:
                todas_cats[cat] = list(subcats)
                
        if categoria in todas_cats:
            self.combo_subcategoria['values'] = sorted(todas_cats[categoria])
            self.combo_subcategoria.set('')
            nombres_proveedores = [p['nombre'] for p in self.proveedores.values() if categoria in p.get('categorias', {})]
            self.combo_proveedor['values'] = nombres_proveedores

    def refrescar_categorias_gasto(self):
        self.actualizar_todas_categorias_combos()
        self.actualizar_subcategorias()
        messagebox.showinfo("Actualizado", "✅ Categorías y subcategorías actualizadas correctamente.")
        
    def registrar_gasto(self):
        if not self.puede_modificar():
            messagebox.showerror("Error", "No tiene permisos para registrar gastos")
            return
            
        try:
            fecha = self.entry_fecha.get()
            categoria = self.combo_categoria.get()
            subcategoria = self.combo_subcategoria.get()
            monto_str = self.entry_monto.get()
            proveedor_nombre = self.combo_proveedor.get()
            descripcion = self.entry_descripcion.get()

            if not all([fecha, categoria, subcategoria, monto_str]):
                return messagebox.showwarning("Advertencia", "Complete campos obligatorios")

            try:
                monto = float(monto_str)
            except ValueError:
                return messagebox.showerror("Error", "Monto inválido")

            fecha_obj = datetime.strptime(fecha, '%Y-%m-%d')
            mes = self.meses[fecha_obj.month - 1]

            if mes in self.presupuesto_mensual_por_mes:
                presupuesto_categoria = self.presupuesto_mensual_por_mes[mes].get(categoria, 0)
                gastos_categoria_mes = sum(
                    t['monto'] for t in self.transacciones
                    if t['categoria'] == categoria and datetime.strptime(t['fecha'], '%Y-%m-%d').month == fecha_obj.month and datetime.strptime(t['fecha'], '%Y-%m-%d').year == fecha_obj.year
                )
                disponible = presupuesto_categoria - gastos_categoria_mes
                if monto > disponible:
                    diferencia = monto - disponible
                    mensaje = (
                        f" ADVERTENCIA: Presupuesto insuficiente\n"
                        f"Categoría: {categoria}\n"
                        f"Mes: {mes}\n"
                        f"Presupuesto: ${presupuesto_categoria:,.2f}\n"
                        f"Ya gastado: ${gastos_categoria_mes:,.2f}\n"
                        f"Disponible: ${disponible:,.2f}\n"
                        f"Necesitas: ${diferencia:,.2f} adicionales"
                    )
                    respuesta = messagebox.askyesnocancel(
                        "Presupuesto Insuficiente",
                        mensaje + "\n\n¿Desea agregar presupuesto adicional?"
                    )
                    if respuesta is None:
                        return
                    elif respuesta:
                        self.ventana_origen_presupuesto(mes, categoria, diferencia)
                        return

            año_gasto = fecha_obj.year
            if año_gasto != self.año_actual:
                respuesta = messagebox.askyesnocancel(
                    "⚠️ Año Diferente Detectado",
                    (f"La fecha del gasto es del año {año_gasto}\n"
                     f"El sistema está trabajando en el año {self.año_actual}\n\n"
                     "¿Qué desea hacer?\n\n"
                     f"• SÍ: Cambiar automáticamente al año {año_gasto}\n"
                     f"• NO: Cambiar la fecha del gasto al año actual ({self.año_actual})\n"
                     "• CANCELAR: No registrar el gasto")
                )
                if respuesta is None:
                    return
                elif respuesta:
                    self.año_actual = año_gasto
                    if str(año_gasto) in self.presupuestos_por_año:
                        self.presupuesto_mensual_por_mes = dict(self.presupuestos_por_año[str(año_gasto)])
                    else:
                        if messagebox.askyesno("Crear Año", f"No existe presupuesto para {año_gasto}.\n¿Desea crearlo ahora?"):
                            self.presupuestos_por_año[str(año_gasto)] = {}
                            self.presupuesto_mensual_por_mes = {}
                        else:
                            return
                    if hasattr(self, 'label_año_actual'):
                        self.label_año_actual.config(text=f"📅 Año: {self.año_actual}")
                    if hasattr(self, 'combo_año_trabajo'):
                        años_disponibles = sorted([int(y) for y in self.presupuestos_por_año.keys()], reverse=True)
                        self.combo_año_trabajo['values'] = años_disponibles
                        if año_gasto in años_disponibles:
                            self.combo_año_trabajo.current(años_disponibles.index(año_gasto))
                    self.actualizar_info_año()
                    self.registrar_actividad("Cambio automático de año", f"Cambio a {año_gasto} por registro de gasto")
                    messagebox.showinfo("Año Cambiado", f"Sistema cambiado al año {año_gasto}\nAhora puede registrar el gasto.")
                else:
                    try:
                        nueva_fecha = datetime(self.año_actual, fecha_obj.month, fecha_obj.day)
                    except ValueError:
                        nueva_fecha = datetime(self.año_actual, fecha_obj.month, 1)
                    self.entry_fecha.delete(0, tk.END)
                    self.entry_fecha.insert(0, nueva_fecha.strftime('%Y-%m-%d'))
                    messagebox.showinfo("Fecha Ajustada", f"Fecha cambiada a: {nueva_fecha.strftime('%Y-%m-%d')}\nPor favor registre el gasto nuevamente.")
                    return

            self.transacciones.append({
                'fecha': fecha,
                'categoria': categoria,
                'subcategoria': subcategoria,
                'monto': monto,
                'proveedor': proveedor_nombre,
                'descripcion': descripcion
            })
            self.guardar_datos()
            self.registrar_actividad("Registro de gasto", f"${monto:,.2f} en {categoria}")
            self.actualizar_tabla_gastos()
            self.limpiar_campos_gasto()
            messagebox.showinfo("Éxito", "Gasto registrado correctamente")

        except ValueError:
            messagebox.showerror("Error", "Fecha inválida. Use formato YYYY-MM-DD")
        except Exception as e:
            messagebox.showerror("Error", f"Error al registrar: {str(e)}")
            
    def ventana_origen_presupuesto(self, mes_destino, categoria_destino, monto_necesario):
        ventana = tk.Toplevel(self.root)
        ventana.title("💰 Origen del Presupuesto Adicional")
        ventana.geometry("700x600")
        ventana.transient(self.root)
        ventana.grab_set()
        
        ventana.update_idletasks()
        x = (ventana.winfo_screenwidth() // 2) - 350
        y = (ventana.winfo_screenheight() // 2) - 300
        ventana.geometry(f'700x600+{x}+{y}')
        
        frame = tk.Frame(ventana, bg='white')
        frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        tk.Label(
            frame,
            text="💰 Seleccione el Origen del Presupuesto",
            font=('Arial', 14, 'bold'),
            fg='#2d5016',
            bg='white'
        ).pack(pady=(0, 10))
        
        info_frame = tk.Frame(frame, bg='#fff3cd', relief='solid', bd=1)
        info_frame.pack(fill='x', pady=10, padx=5)
        
        tk.Label(
            info_frame,
            text=f"📊 Necesita: ${monto_necesario:,.2f} para {categoria_destino} en {mes_destino}",
            font=('Arial', 11, 'bold'),
            bg='#fff3cd'
        ).pack(pady=10)
        
        opcion_var = tk.StringVar(value="otro_mes")
        
        frame_opcion1 = tk.LabelFrame(
            frame,
            text="Opción 1: Transferir de Otro Mes",
            font=('Arial', 11, 'bold'),
            bg='white',
            padx=10,
            pady=10
        ).pack(fill='x', pady=10)
        
        ttk.Radiobutton(
            frame_opcion1,
            text="📅 Tomar dinero de otro mes del año actual",
            variable=opcion_var,
            value="otro_mes"
        ).pack(anchor='w', pady=5)
        
        frame_selectores = tk.Frame(frame_opcion1)
        frame_selectores.pack(fill='x', padx=20, pady=5)
        
        tk.Label(frame_selectores, text="Mes origen:", font=('Arial', 10, 'bold')).grid(
            row=0, column=0, sticky='w', padx=5, pady=5)
        
        meses_disponibles = [m for m in self.meses if m != mes_destino]
        combo_mes_origen = ttk.Combobox(
            frame_selectores,
            values=meses_disponibles,
            state='readonly',
            width=15
        )
        combo_mes_origen.grid(row=0, column=1, padx=5, pady=5)
        if meses_disponibles:
            combo_mes_origen.current(0)
        
        tk.Label(frame_selectores, text="Categoría origen:", font=('Arial', 10, 'bold')).grid(
            row=0, column=2, sticky='w', padx=5, pady=5)
        
        combo_cat_origen = ttk.Combobox(frame_selectores, state='readonly', width=25)
        combo_cat_origen.grid(row=0, column=3, padx=5, pady=5)
        
        label_disponible = tk.Label(
            frame_selectores,
            text="Disponible: $0.00",
            font=('Arial', 9),
            fg='#666'
        )
        label_disponible.grid(row=1, column=1, columnspan=3, sticky='w', padx=5)
        
        def actualizar_categorias_origen():
            mes_sel = combo_mes_origen.get()
            if mes_sel and mes_sel in self.presupuesto_mensual_por_mes:
                categorias = list(self.presupuesto_mensual_por_mes[mes_sel].keys())
                combo_cat_origen['values'] = categorias
                if categorias:
                    combo_cat_origen.current(0)
                    actualizar_disponible()
        
        def actualizar_disponible():
            mes_sel = combo_mes_origen.get()
            cat_sel = combo_cat_origen.get()
            
            if mes_sel and cat_sel:
                presupuesto = self.presupuesto_mensual_por_mes.get(mes_sel, {}).get(cat_sel, 0)
                
                gastado = sum(
                    t['monto'] for t in self.transacciones
                    if t.get('categoria') == cat_sel and 
                    datetime.strptime(t['fecha'], '%Y-%m-%d').strftime('%Y-%m') == 
                    f"{self.año_actual}-{str(self.meses.index(mes_sel) + 1).zfill(2)}"
                )
                
                disponible = presupuesto - gastado
                
                if disponible >= monto_necesario:
                    label_disponible.config(
                        text=f"✅ Disponible: ${disponible:,.2f}",
                        fg='#4CAF50'
                    )
                else:
                    label_disponible.config(
                        text=f"❌ Disponible: ${disponible:,.2f} (Insuficiente)",
                        fg='#f44336'
                    )
        
        combo_mes_origen.bind('<<ComboboxSelected>>', lambda e: actualizar_categorias_origen())
        combo_cat_origen.bind('<<ComboboxSelected>>', lambda e: actualizar_disponible())
        
        actualizar_categorias_origen()
        
        frame_opcion2 = tk.LabelFrame(
            frame,
            text="Opción 2: Usar Sobrantes del Año Anterior",
            font=('Arial', 11, 'bold'),
            bg='white',
            padx=10,
            pady=10
        )
        frame_opcion2.pack(fill='x', pady=10)
        
        ttk.Radiobutton(
            frame_opcion2,
            text="💰 Usar sobrantes acumulados",
            variable=opcion_var,
            value="sobrantes"
        ).pack(anchor='w', pady=5)
        
        año_anterior = self.año_actual - 1
        sobrante_total = self.calcular_sobrante_año(año_anterior)
        sobrante_usado = self.sobrantes_anuales.get(str(año_anterior), {}).get('usado', 0)
        sobrante_disponible = sobrante_total - sobrante_usado
        
        if sobrante_disponible >= monto_necesario:
            color = '#4CAF50'
            icono = "✅"
        else:
            color = '#f44336'
            icono = "❌"
        
        tk.Label(
            frame_opcion2,
            text=f"{icono} Sobrante disponible: ${sobrante_disponible:,.2f}",
            font=('Arial', 10),
            fg=color,
            bg='white'
        ).pack(anchor='w', padx=20)
        
        frame_opcion3 = tk.LabelFrame(
            frame,
            text="Opción 3: Agregar sin Origen Específico",
            font=('Arial', 11, 'bold'),
            bg='white',
            padx=10,
            pady=10
        )
        frame_opcion3.pack(fill='x', pady=10)
        
        ttk.Radiobutton(
            frame_opcion3,
            text="➕ Simplemente agregar al presupuesto (no recomendado)",
            variable=opcion_var,
            value="sin_origen"
        ).pack(anchor='w', pady=5)
        
        tk.Label(
            frame_opcion3,
            text="⚠️ Esta opción aumenta el presupuesto sin control de origen",
            font=('Arial', 9, 'italic'),
            fg='#666',
            bg='white'
        ).pack(anchor='w', padx=20)
        
        frame_botones = tk.Frame(frame, bg='white')
        frame_botones.pack(pady=20)
        
        def aplicar_origen():
            opcion = opcion_var.get()
            
            if opcion == "otro_mes":
                mes_origen = combo_mes_origen.get()
                cat_origen = combo_cat_origen.get()
                
                if not mes_origen or not cat_origen:
                    messagebox.showwarning("Advertencia", 
                        "Debe seleccionar mes y categoría de origen")
                    return
                
                presupuesto = self.presupuesto_mensual_por_mes.get(mes_origen, {}).get(cat_origen, 0)
                
                mes_idx_origen = self.meses.index(mes_origen) + 1
                gastado = sum(
                    t['monto'] for t in self.transacciones
                    if t.get('categoria') == cat_origen and 
                    datetime.strptime(t['fecha'], '%Y-%m-%d').strftime('%Y-%m') == 
                    f"{self.año_actual}-{str(mes_idx_origen).zfill(2)}"
                )
                
                disponible = presupuesto - gastado
                
                if disponible < monto_necesario:
                    messagebox.showerror("Error",
                        f"Dinero insuficiente en {cat_origen} de {mes_origen}\n\n" +
                        f"Disponible: ${disponible:,.2f}\n" +
                        f"Necesario: ${monto_necesario:,.2f}")
                    return
                
                if messagebox.askyesno("Confirmar Transferencia",
                    f"¿Transferir ${monto_necesario:,.2f}?\n\n" +
                    f"DE: {mes_origen} / {cat_origen}\n" +
                    f"HACIA: {mes_destino} / {categoria_destino}"):
                    
                    self.presupuesto_mensual_por_mes[mes_origen][cat_origen] -= monto_necesario
                    
                    if mes_destino not in self.presupuesto_mensual_por_mes:
                        self.presupuesto_mensual_por_mes[mes_destino] = {}
                    
                    if categoria_destino not in self.presupuesto_mensual_por_mes[mes_destino]:
                        self.presupuesto_mensual_por_mes[mes_destino][categoria_destino] = 0
                    
                    self.presupuesto_mensual_por_mes[mes_destino][categoria_destino] += monto_necesario
                    
                    if mes_destino not in self.presupuesto_modificado:
                        self.presupuesto_modificado[mes_destino] = {}
                    self.presupuesto_modificado[mes_destino][categoria_destino] = True
                    
                    if mes_origen not in self.presupuesto_modificado:
                        self.presupuesto_modificado[mes_origen] = {}
                    self.presupuesto_modificado[mes_origen][cat_origen] = True
                    
                    self.guardar_datos()
                    self.registrar_actividad(
                        "Transferir presupuesto",
                        f"${monto_necesario:,.2f} de {mes_origen}/{cat_origen} a {mes_destino}/{categoria_destino}"
                    )
                    
                    messagebox.showinfo("Éxito", 
                        f"Presupuesto transferido exitosamente\n\n" +
                        f"${monto_necesario:,.2f} disponibles ahora en {categoria_destino}")
                    
                    ventana.destroy()
                    self.registrar_gasto()
            
            elif opcion == "sobrantes":
                if sobrante_disponible < monto_necesario:
                    messagebox.showerror("Error",
                        f"Sobrante insuficiente\n\n" +
                        f"Disponible: ${sobrante_disponible:,.2f}\n" +
                        f"Necesario: ${monto_necesario:,.2f}")
                    return
                
                if messagebox.askyesno("Confirmar",
                    f"¿Usar ${monto_necesario:,.2f} de sobrantes?\n\n" +
                    f"Año anterior: {año_anterior}\n" +
                    f"Destino: {mes_destino} / {categoria_destino}"):
                    
                    if mes_destino not in self.presupuesto_mensual_por_mes:
                        self.presupuesto_mensual_por_mes[mes_destino] = {}
                    
                    if categoria_destino not in self.presupuesto_mensual_por_mes[mes_destino]:
                        self.presupuesto_mensual_por_mes[mes_destino][categoria_destino] = 0
                    
                    self.presupuesto_mensual_por_mes[mes_destino][categoria_destino] += monto_necesario
                    
                    if str(año_anterior) not in self.sobrantes_anuales:
                        self.sobrantes_anuales[str(año_anterior)] = {
                            'monto': sobrante_total,
                            'usado': 0
                        }
                    
                    self.sobrantes_anuales[str(año_anterior)]['usado'] = \
                        self.sobrantes_anuales[str(año_anterior)].get('usado', 0) + monto_necesario
                    
                    if mes_destino not in self.presupuesto_modificado:
                        self.presupuesto_modificado[mes_destino] = {}
                    self.presupuesto_modificado[mes_destino][categoria_destino] = True
                    
                    self.guardar_datos()
                    self.guardar_sobrantes_anuales()
                    self.registrar_actividad(
                        "Usar sobrante",
                        f"${monto_necesario:,.2f} de sobrantes {año_anterior} a {mes_destino}/{categoria_destino}"
                    )
                    
                    messagebox.showinfo("Éxito",
                        f"Sobrante aplicado exitosamente\n\n" +
                        f"${monto_necesario:,.2f} disponibles ahora en {categoria_destino}")
                    
                    ventana.destroy()
                    self.registrar_gasto()
            
            else:
                if messagebox.askyesno("Confirmar",
                    f"¿Agregar ${monto_necesario:,.2f} sin origen?\n\n" +
                    f"Destino: {mes_destino} / {categoria_destino}\n\n" +
                    "⚠️ Esto aumentará el presupuesto sin control"):
                    
                    if mes_destino not in self.presupuesto_mensual_por_mes:
                        self.presupuesto_mensual_por_mes[mes_destino] = {}
                    
                    if categoria_destino not in self.presupuesto_mensual_por_mes[mes_destino]:
                        self.presupuesto_mensual_por_mes[mes_destino][categoria_destino] = 0
                    
                    self.presupuesto_mensual_por_mes[mes_destino][categoria_destino] += monto_necesario
                    
                    if mes_destino not in self.presupuesto_modificado:
                        self.presupuesto_modificado[mes_destino] = {}
                    self.presupuesto_modificado[mes_destino][categoria_destino] = True
                    
                    self.guardar_datos()
                    self.registrar_actividad(
                        "Agregar presupuesto",
                        f"${monto_necesario:,.2f} agregados a {mes_destino}/{categoria_destino}"
                    )
                    
                    messagebox.showinfo("Éxito",
                        f"Presupuesto agregado\n\n" +
                        f"${monto_necesario:,.2f} disponibles ahora en {categoria_destino}")
                    
                    ventana.destroy()
                    self.registrar_gasto()
        
        ttk.Button(
            frame_botones,
            text="✅ Aplicar",
            command=aplicar_origen,
            width=15
        ).pack(side='left', padx=5)
        
        ttk.Button(
            frame_botones,
            text="❌ Cancelar",
            command=ventana.destroy,
            width=15
        ).pack(side='left', padx=5)
        
        actualizar_categorias_origen()

    def limpiar_campos_gasto(self):
        self.entry_fecha.delete(0, tk.END)
        self.entry_fecha.insert(0, datetime.now().strftime('%Y-%m-%d'))
        self.combo_categoria.set('')
        self.combo_subcategoria.set('')
        self.entry_monto.delete(0, tk.END)
        self.combo_proveedor.set('')
        self.entry_descripcion.delete(0, tk.END)

    def eliminar_gasto(self):
        if not self.puede_modificar():
            messagebox.showerror("Error", "No tiene permisos para eliminar gastos")
            return
            
        seleccion = self.tree_gastos.selection()
        if not seleccion: return
        if messagebox.askyesno("Confirmar", "¿Eliminar este gasto?"):
            valores = self.tree_gastos.item(seleccion[0])['values']
            for i, t in enumerate(self.transacciones):
                if t['fecha'] == valores[0] and t['categoria'] == valores[1] and f"${t['monto']:,.2f}" == valores[3]:
                    del self.transacciones[i]
                    break
            self.guardar_datos()
            self.actualizar_tabla_gastos()

    def actualizar_tabla_gastos(self):
        for item in self.tree_gastos.get_children(): self.tree_gastos.delete(item)
        for t in sorted(self.transacciones, key=lambda x: x['fecha'], reverse=True):
            self.tree_gastos.insert('', 'end', values=(t['fecha'], t['categoria'], t.get('subcategoria', ''), f"${t['monto']:,.2f}", t.get('proveedor', ''), t.get('descripcion', '')))

    def crear_tab_control(self):
        frame_seleccion = ttk.Frame(self.tab_control)
        frame_seleccion.pack(fill='x', padx=10, pady=10)
        tk.Label(frame_seleccion, text="Seleccionar Mes:", font=('Arial', 12, 'bold')).pack(side='left', padx=5)
        self.combo_mes_control = ttk.Combobox(frame_seleccion, values=self.meses, state='readonly', width=15, font=('Arial', 11))
        self.combo_mes_control.pack(side='left', padx=5)
        self.combo_mes_control.current(datetime.now().month - 1)
        ttk.Button(frame_seleccion, text=" Actualizar Datos", command=self.actualizar_control_mensual).pack(side='left', padx=15)
        
        frame_resumen = ttk.LabelFrame(self.tab_control, text=" Resumen del Mes", padding=15)
        frame_resumen.pack(fill='x', padx=10, pady=10)
        
        frame_cards = tk.Frame(frame_resumen, bg='white')
        frame_cards.pack(fill='x', pady=10)
        
        card1 = tk.Frame(frame_cards, bg='#4CAF50', relief='raised', bd=3)
        card1.pack(side='left', fill='both', expand=True, padx=10)
        tk.Label(card1, text=" PRESUPUESTADO", font=('Arial', 11, 'bold'), bg='#4CAF50', fg='white').pack(pady=8)
        self.label_presupuestado_mes = tk.Label(card1, text="$0.00", font=('Arial', 18, 'bold'), bg='#4CAF50', fg='white')
        self.label_presupuestado_mes.pack(pady=8)
        
        card2 = tk.Frame(frame_cards, bg='#FF9800', relief='raised', bd=3)
        card2.pack(side='left', fill='both', expand=True, padx=10)
        tk.Label(card2, text=" GASTADO", font=('Arial', 11, 'bold'), bg='#FF9800', fg='white').pack(pady=8)
        self.label_gastado_mes = tk.Label(card2, text="$0.00", font=('Arial', 18, 'bold'), bg='#FF9800', fg='white')
        self.label_gastado_mes.pack(pady=8)
        
        card3 = tk.Frame(frame_cards, bg='#2196F3', relief='raised', bd=3)
        card3.pack(side='left', fill='both', expand=True, padx=10)
        tk.Label(card3, text=" DISPONIBLE", font=('Arial', 11, 'bold'), bg='#2196F3', fg='white').pack(pady=8)
        self.label_disponible_mes = tk.Label(card3, text="$0.00", font=('Arial', 18, 'bold'), bg='#2196F3', fg='white')
        self.label_disponible_mes.pack(pady=8)
        
        frame_detalle = ttk.LabelFrame(self.tab_control, text=" Detalle por Categoría", padding=10)
        frame_detalle.pack(fill='both', expand=True, padx=10, pady=10)
        
        scroll_y = ttk.Scrollbar(frame_detalle, orient='vertical')
        self.tree_control = ttk.Treeview(frame_detalle, columns=('categoria', 'presupuesto', 'gastado', 'disponible', 'porcentaje', 'estado'), show='headings', yscrollcommand=scroll_y.set)
        scroll_y.config(command=self.tree_control.yview)
        
        for col, w in zip(('categoria', 'presupuesto', 'gastado', 'disponible', 'porcentaje', 'estado'), (250, 150, 150, 150, 100, 120)):
            self.tree_control.heading(col, text=col.capitalize())
            self.tree_control.column(col, width=w)
            
        self.tree_control.pack(side='left', fill='both', expand=True)
        scroll_y.pack(side='right', fill='y')
        
        self.tree_control.tag_configure('ok', background='#c8e6c9')
        self.tree_control.tag_configure('warning', background='#fff9c4')
        self.tree_control.tag_configure('danger', background='#ffccbc')
        self.tree_control.tag_configure('modified', background='#e1bee7')
        
        self.actualizar_control_mensual()

    def actualizar_control_mensual(self):
        mes_seleccionado, mes_numero = self.combo_mes_control.get(), self.meses.index(self.combo_mes_control.get()) + 1
        año_actual = datetime.now().year
        
        for item in self.tree_control.get_children(): self.tree_control.delete(item)
        
        total_presupuestado, total_gastado = 0, 0
        
        if mes_seleccionado in self.presupuesto_mensual_por_mes:
            for categoria, presupuesto in self.presupuesto_mensual_por_mes[mes_seleccionado].items():
                gastos = sum(t['monto'] for t in self.transacciones if t['categoria'] == categoria and datetime.strptime(t['fecha'], '%Y-%m-%d').month == mes_numero and datetime.strptime(t['fecha'], '%Y-%m-%d').year == año_actual)
                disponible = presupuesto - gastos
                porcentaje = (gastos / presupuesto * 100) if presupuesto > 0 else 0
                estado, tag = (" OK", 'ok') if porcentaje <= 75 else (" ALERTA", 'warning') if porcentaje <= 90 else (" CRÍTICO", 'warning') if porcentaje <= 100 else (" EXCEDIDO", 'danger')
                
                if mes_seleccionado in self.presupuesto_modificado and categoria in self.presupuesto_modificado[mes_seleccionado] and self.presupuesto_modificado[mes_seleccionado][categoria]:
                    estado += " (MOD)"
                    tag = 'modified'
                    
                self.tree_control.insert('', 'end', values=(categoria, f"${presupuesto:,.2f}", f"${gastos:,.2f}", f"${disponible:,.2f}", f"{porcentaje:.1f}%", estado), tags=(tag,))
                total_presupuestado += presupuesto
                total_gastado += gastos
                
        self.label_presupuestado_mes.config(text=f"${total_presupuestado:,.2f}")
        self.label_gastado_mes.config(text=f"${total_gastado:,.2f}")
        disp = total_presupuestado - total_gastado
        self.label_disponible_mes.config(text=f"${abs(disp):,.2f} EXCEDIDO" if disp < 0 else f"${disp:,.2f}")
        self.label_disponible_mes.master.config(bg='#f44336' if disp < 0 else '#2196F3')

    def crear_tab_sobrantes(self):
        frame_sobrantes = ttk.LabelFrame(self.tab_sobrantes, text=" Sobrantes Disponibles", padding=15)
        frame_sobrantes.pack(fill='x', padx=10, pady=10)
        
        frame_mes_origen = tk.Frame(frame_sobrantes)
        frame_mes_origen.pack(fill='x', pady=5)
        tk.Label(frame_mes_origen, text="Mes de Origen:", font=('Arial', 11, 'bold')).pack(side='left', padx=5)
        self.combo_mes_sobrante_origen = ttk.Combobox(frame_mes_origen, values=self.meses, state='readonly', width=15)
        self.combo_mes_sobrante_origen.pack(side='left', padx=5)
        self.combo_mes_sobrante_origen.current(datetime.now().month - 1)
        self.combo_mes_sobrante_origen.bind('<<ComboboxSelected>>', self.actualizar_sobrantes_disponibles)
        
        if self.puede_modificar():
            ttk.Button(frame_mes_origen, text=" Calcular Sobrantes", command=self.calcular_sobrantes).pack(side='left', padx=15)
        
        ttk.Button(frame_mes_origen, text="🔄 Refrescar Categorías", command=self.refrescar_categorias_sobrantes).pack(side='left', padx=5)
        
        frame_tabla_sobrantes = ttk.Frame(frame_sobrantes)
        frame_tabla_sobrantes.pack(fill='both', expand=True, pady=10)
        
        scroll_sobrantes = ttk.Scrollbar(frame_tabla_sobrantes, orient='vertical')
        self.tree_sobrantes = ttk.Treeview(frame_tabla_sobrantes, columns=('categoria', 'presupuesto', 'gastado', 'sobrante'), show='headings', yscrollcommand=scroll_sobrantes.set, height=8)
        scroll_sobrantes.config(command=self.tree_sobrantes.yview)
        
        for col, w in zip(('categoria', 'presupuesto', 'gastado', 'sobrante'), (300, 150, 150, 150)):
            self.tree_sobrantes.heading(col, text=col.capitalize())
            self.tree_sobrantes.column(col, width=w)
            
        self.tree_sobrantes.pack(side='left', fill='both', expand=True)
        scroll_sobrantes.pack(side='right', fill='y')
        
        if self.puede_modificar():
            frame_transferencia = ttk.LabelFrame(self.tab_sobrantes, text=" Transferir Sobrante", padding=15)
            frame_transferencia.pack(fill='x', padx=10, pady=10)
            
            tk.Label(frame_transferencia, text="Tipo de Transferencia:", font=('Arial', 11, 'bold')).grid(row=0, column=0, sticky='w', padx=5, pady=5)
            self.tipo_transferencia = tk.StringVar(value="mes")
            tk.Radiobutton(frame_transferencia, text="A otro mes", variable=self.tipo_transferencia, value="mes").grid(row=0, column=1, sticky='w', padx=5)
            tk.Radiobutton(frame_transferencia, text="A otra categoría (mismo mes)", variable=self.tipo_transferencia, value="categoria").grid(row=0, column=2, sticky='w', padx=5)
            
            tk.Label(frame_transferencia, text="Categoría Origen:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
            todas_cats_sob = sorted({**self.categorias_agricolas, **self.categorias_personalizadas}.keys())
            self.combo_categoria_origen_sobrante = ttk.Combobox(frame_transferencia, values=todas_cats_sob, state='readonly', width=25)
            self.combo_categoria_origen_sobrante.grid(row=1, column=1, padx=5, pady=5)
            
            tk.Label(frame_transferencia, text="Monto:").grid(row=1, column=2, sticky='w', padx=5, pady=5)
            self.entry_monto_transferir = ttk.Entry(frame_transferencia, width=15)
            self.entry_monto_transferir.grid(row=1, column=3, padx=5, pady=5)
            
            tk.Label(frame_transferencia, text="Destino (Mes):").grid(row=2, column=0, sticky='w', padx=5, pady=5)
            self.combo_mes_destino = ttk.Combobox(frame_transferencia, values=self.meses, state='readonly', width=15)
            self.combo_mes_destino.grid(row=2, column=1, padx=5, pady=5)
            
            tk.Label(frame_transferencia, text="Destino (Categoría):").grid(row=2, column=2, sticky='w', padx=5, pady=5)
            todas_cats_sob2 = sorted({**self.categorias_agricolas, **self.categorias_personalizadas}.keys())
            self.combo_categoria_destino = ttk.Combobox(frame_transferencia, values=todas_cats_sob2, state='readonly', width=25)
            self.combo_categoria_destino.grid(row=2, column=3, padx=5, pady=5)
            
            ttk.Button(frame_transferencia, text="Realizar Transferencia", command=self.realizar_transferencia).grid(row=3, column=0, columnspan=4, pady=15)
        
        frame_historial = ttk.LabelFrame(self.tab_sobrantes, text="Historial de Transferencias", padding=10)
        frame_historial.pack(fill='both', expand=True, padx=10, pady=10)
        self.text_historial = scrolledtext.ScrolledText(frame_historial, height=8, font=('Courier', 9))
        self.text_historial.pack(fill='both', expand=True)
        
        self.actualizar_sobrantes_disponibles()

    def refrescar_categorias_sobrantes(self):
        todas_cats = sorted({**self.categorias_agricolas, **self.categorias_personalizadas}.keys())
        if hasattr(self, 'combo_categoria_origen_sobrante'):
            val = self.combo_categoria_origen_sobrante.get()
            self.combo_categoria_origen_sobrante['values'] = todas_cats
            if val in todas_cats:
                self.combo_categoria_origen_sobrante.set(val)
        if hasattr(self, 'combo_categoria_destino'):
            val = self.combo_categoria_destino.get()
            self.combo_categoria_destino['values'] = todas_cats
            if val in todas_cats:
                self.combo_categoria_destino.set(val)
        messagebox.showinfo("Actualizado", "✅ Categorías de sobrantes actualizadas correctamente.")

    def calcular_sobrantes(self):
        if not self.puede_modificar():
            messagebox.showerror("Error", "No tiene permisos para calcular sobrantes")
            return
            
        self.actualizar_sobrantes_disponibles()
        messagebox.showinfo("Sobrantes Calculados", "Los sobrantes han sido actualizados")

    def actualizar_sobrantes_disponibles(self, event=None):
        mes_seleccionado, mes_numero = self.combo_mes_sobrante_origen.get(), self.meses.index(self.combo_mes_sobrante_origen.get()) + 1
        año_actual = datetime.now().year
        
        for item in self.tree_sobrantes.get_children(): self.tree_sobrantes.delete(item)
        
        if mes_seleccionado in self.presupuesto_mensual_por_mes:
            for categoria, presupuesto in self.presupuesto_mensual_por_mes[mes_seleccionado].items():
                gastos = sum(t['monto'] for t in self.transacciones if t['categoria'] == categoria and datetime.strptime(t['fecha'], '%Y-%m-%d').month == mes_numero and datetime.strptime(t['fecha'], '%Y-%m-%d').year == año_actual)
                if presupuesto - gastos > 0:
                    self.tree_sobrantes.insert('', 'end', values=(categoria, f"${presupuesto:,.2f}", f"${gastos:,.2f}", f"${presupuesto - gastos:,.2f}"))

    def realizar_transferencia(self):
        if not self.puede_modificar():
            messagebox.showerror("Error", "No tiene permisos para realizar transferencias")
            return
            
        try:
            mes_origen, categoria_origen = self.combo_mes_sobrante_origen.get(), self.combo_categoria_origen_sobrante.get()
            monto, tipo = float(self.entry_monto_transferir.get()), self.tipo_transferencia.get()
            
            if not all([mes_origen, categoria_origen, monto]): return messagebox.showwarning("Advertencia", "Complete todos los campos")
            
            mes_numero = self.meses.index(mes_origen) + 1
            año_actual = datetime.now().year
            
            presupuesto = self.presupuesto_mensual_por_mes[mes_origen][categoria_origen]
            gastos = sum(t['monto'] for t in self.transacciones if t['categoria'] == categoria_origen and datetime.strptime(t['fecha'], '%Y-%m-%d').month == mes_numero and datetime.strptime(t['fecha'], '%Y-%m-%d').year == año_actual)
            
            if monto > (presupuesto - gastos): return messagebox.showerror("Error", f"No hay suficiente sobrante. Disponible: ${presupuesto - gastos:,.2f}")
            
            self.presupuesto_mensual_por_mes[mes_origen][categoria_origen] -= monto
            
            if tipo == "mes":
                mes_destino, categoria_destino = self.combo_mes_destino.get(), categoria_origen
                if not mes_destino: return messagebox.showwarning("Advertencia", "Seleccione el mes destino")
                if mes_destino not in self.presupuesto_mensual_por_mes: self.presupuesto_mensual_por_mes[mes_destino] = {}
                self.presupuesto_mensual_por_mes[mes_destino][categoria_destino] = self.presupuesto_mensual_por_mes[mes_destino].get(categoria_destino, 0) + monto
                if mes_destino not in self.presupuesto_modificado: self.presupuesto_modificado[mes_destino] = {}
                self.presupuesto_modificado[mes_destino][categoria_destino] = True
                mensaje = f"Transferencia: ${monto:,.2f} de {categoria_origen} De {mes_origen} → A {mes_destino}"
            else:
                categoria_destino = self.combo_categoria_destino.get()
                if not categoria_destino: return messagebox.showwarning("Advertencia", "Seleccione la categoría destino")
                self.presupuesto_mensual_por_mes[mes_origen][categoria_destino] = self.presupuesto_mensual_por_mes[mes_origen].get(categoria_destino, 0) + monto
                if mes_origen not in self.presupuesto_modificado: self.presupuesto_modificado[mes_origen] = {}
                self.presupuesto_modificado[mes_origen][categoria_destino] = True
                mensaje = f"Transferencia en {mes_origen}: ${monto:,.2f} De {categoria_origen} → A {categoria_destino}"
                
            self.guardar_datos()
            self.registrar_actividad("Transferencia", mensaje)
            self.text_historial.insert('1.0', f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {mensaje}\n")
            self.actualizar_sobrantes_disponibles()
            messagebox.showinfo("Éxito", mensaje)
            self.entry_monto_transferir.delete(0, tk.END)
            self.combo_categoria_origen_sobrante.set('')
            self.combo_mes_destino.set('')
            self.combo_categoria_destino.set('')
            
        except ValueError: messagebox.showerror("Error", "Monto válido requerido")
        except Exception as e: messagebox.showerror("Error", f"Error: {str(e)}")
        
        if hasattr(self, 'presupuesto_mensual_entries'):
            self.cargar_presupuesto_mes()

    def crear_tab_graficos(self):
        frame_controles = ttk.Frame(self.tab_graficos)
        frame_controles.pack(fill='x', padx=10, pady=10)
        tk.Label(frame_controles, text="Seleccionar Mes:", font=('Arial', 11, 'bold')).pack(side='left', padx=5)
        self.combo_mes_grafico = ttk.Combobox(frame_controles, values=self.meses, state='readonly', width=15)
        self.combo_mes_grafico.pack(side='left', padx=5)
        self.combo_mes_grafico.current(datetime.now().month - 1)
        ttk.Button(frame_controles, text=" Generar Gráficos", command=self.generar_graficos).pack(side='left', padx=15)
        
        self.frame_graficos = ttk.Frame(self.tab_graficos)
        self.frame_graficos.pack(fill='both', expand=True, padx=10, pady=10)

    def generar_graficos(self):
        for widget in self.frame_graficos.winfo_children(): widget.destroy()
        
        mes_seleccionado, mes_numero = self.combo_mes_grafico.get(), self.meses.index(self.combo_mes_grafico.get()) + 1
        año_actual = datetime.now().year
        
        if mes_seleccionado not in self.presupuesto_mensual_por_mes: 
            return messagebox.showinfo("Sin Datos", "No hay presupuesto configurado para este mes")
        
        fig = Figure(figsize=(14, 10))
        ax1 = fig.add_subplot(2, 2, 1)
        categorias, presupuestos, gastos = [], [], []
        
        for categoria, presupuesto in self.presupuesto_mensual_por_mes[mes_seleccionado].items():
            gasto = sum(t['monto'] for t in self.transacciones if t['categoria'] == categoria and datetime.strptime(t['fecha'], '%Y-%m-%d').month == mes_numero and datetime.strptime(t['fecha'], '%Y-%m-%d').year == año_actual)
            categorias.append(categoria[:12] + '..' if len(categoria) > 12 else categoria)
            presupuestos.append(presupuesto)
            gastos.append(gasto)
        
        x, width = range(len(categorias)), 0.35
        ax1.bar([i - width/2 for i in x], presupuestos, width, label='Presupuesto', color='#4CAF50')
        ax1.bar([i + width/2 for i in x], gastos, width, label='Gastado', color='#FF9800')
        ax1.set_xlabel('Categorías')
        ax1.set_ylabel('Monto ($)')
        ax1.set_title(f'Presupuesto vs Gastado - {mes_seleccionado}')
        ax1.set_xticks(x)
        ax1.set_xticklabels(categorias, rotation=45, ha='right', fontsize=8)
        ax1.legend()
        ax1.grid(axis='y', alpha=0.3)
        
        ax2 = fig.add_subplot(2, 2, 2)
        porcentajes = [(g/p*100 if p > 0 else 0) for g, p in zip(gastos, presupuestos)]
        colors = ['#f44336' if p > 100 else '#FF9800' if p > 90 else '#4CAF50' for p in porcentajes]
        ax2.barh(categorias, porcentajes, color=colors)
        ax2.set_xlabel('% Utilizado')
        ax2.set_title('Porcentaje de Uso del Presupuesto')
        ax2.axvline(x=100, color='red', linestyle='--', linewidth=2, label='Límite')
        ax2.legend()
        ax2.grid(axis='x', alpha=0.3)
        ax2.tick_params(axis='y', labelsize=8)
        
        ax3 = fig.add_subplot(2, 2, 3)
        gastos_no_cero = [(cat, gasto) for cat, gasto in zip(categorias, gastos) if gasto > 0]
        if gastos_no_cero:
            labels, values = zip(*gastos_no_cero)
            ax3.pie(values, labels=labels, autopct='%1.1f%%', startangle=90, textprops={'fontsize': 8})
            ax3.set_title('Distribución del Gasto por Categoría')
        else: 
            ax3.text(0.5, 0.5, 'Sin gastos registrados', ha='center', va='center', transform=ax3.transAxes)
        
        ax4 = fig.add_subplot(2, 2, 4)
        meses_anteriores, totales_gastados = [], []
        for i in range(6, 0, -1):
            mes_idx = (mes_numero - i) % 12
            if mes_idx == 0: mes_idx = 12
            mes_nombre = self.meses[mes_idx - 1]
            total = sum(t['monto'] for t in self.transacciones if datetime.strptime(t['fecha'], '%Y-%m-%d').month == mes_idx)
            meses_anteriores.append(mes_nombre[:3])
            totales_gastados.append(total)

        ax4.plot(meses_anteriores, totales_gastados, marker='o', linewidth=2, markersize=8)
        ax4.set_xlabel('Mes')
        ax4.set_ylabel('Total Gastado ($)')
        ax4.set_title('Tendencia de Gasto (Últimos 6 Meses)')
        ax4.grid(True, alpha=0.3)
        
        fig.tight_layout()
        fig.subplots_adjust(hspace=0.6, bottom=0.15) 
        
        canvas = FigureCanvasTkAgg(fig, master=self.frame_graficos)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

    def cargar_datos(self):
        self.cargar_log_actividades()
        
        if os.path.exists(self.archivo_datos):
            try:
                with open(self.archivo_datos, 'r', encoding='utf-8') as f:
                    self.transacciones = json.load(f)
                    self.migrar_transacciones_antiguas()
            except: 
                self.transacciones = []
                
        if os.path.exists(self.archivo_presupuesto_mensual):
            try:
                with open(self.archivo_presupuesto_mensual, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.presupuesto_mensual_por_mes = data.get('presupuesto', {})
                    self.presupuesto_modificado = data.get('modificado', {})
            except: 
                self.presupuesto_mensual_por_mes, self.presupuesto_modificado = {}, {}
                
        if os.path.exists(self.archivo_proveedores):
            try:
                with open(self.archivo_proveedores, 'r', encoding='utf-8') as f: 
                    self.proveedores = json.load(f)
            except: 
                self.proveedores = {}
                
        if os.path.exists(self.archivo_presupuestos_anuales):
            try:
                with open(self.archivo_presupuestos_anuales, 'r', encoding='utf-8') as f: 
                    self.presupuestos_por_año = json.load(f)
            except: 
                self.presupuestos_por_año = {}
                
        if os.path.exists(self.archivo_sobrantes_anuales):
            try:
                with open(self.archivo_sobrantes_anuales, 'r', encoding='utf-8') as f: 
                    self.sobrantes_anuales = json.load(f)
            except: 
                self.sobrantes_anuales = {}
                
        if os.path.exists(self.archivo_categorias_personalizadas):
            try:
                with open(self.archivo_categorias_personalizadas, 'r', encoding='utf-8') as f: 
                    self.categorias_personalizadas = json.load(f)
            except: 
                self.categorias_personalizadas = {}
                
        if str(self.año_actual) not in self.presupuestos_por_año and self.presupuesto_mensual_por_mes:
            self.presupuestos_por_año[str(self.año_actual)] = dict(self.presupuesto_mensual_por_mes)
            self.guardar_presupuestos_anuales()

    def migrar_transacciones_antiguas(self):
        modificado = False
        for t in self.transacciones:
            if 'proveedor' not in t: 
                t['proveedor'] = ''
                modificado = True
            if 'descripcion' not in t: 
                t['descripcion'] = ''
                modificado = True
            if 'subcategoria' not in t: 
                t['subcategoria'] = ''
                modificado = True
        if modificado: 
            self.guardar_datos()

    def guardar_datos(self):
        self.guardar_log_actividades()
        
        with open(self.archivo_datos, 'w', encoding='utf-8') as f:
            json.dump(self.transacciones, f, ensure_ascii=False, indent=2)
            
        with open(self.archivo_presupuesto_mensual, 'w', encoding='utf-8') as f:
            json.dump({'presupuesto': self.presupuesto_mensual_por_mes, 'modificado': self.presupuesto_modificado}, f, ensure_ascii=False, indent=2)
            
        with open(self.archivo_proveedores, 'w', encoding='utf-8') as f:
            json.dump(self.proveedores, f, ensure_ascii=False, indent=2)
            
        if self.presupuesto_mensual_por_mes:
            self.presupuestos_por_año[str(self.año_actual)] = dict(self.presupuesto_mensual_por_mes)
            self.guardar_presupuestos_anuales()

    def guardar_presupuestos_anuales(self):
        with open(self.archivo_presupuestos_anuales, 'w', encoding='utf-8') as f:
            json.dump(self.presupuestos_por_año, f, ensure_ascii=False, indent=2)

    def guardar_sobrantes_anuales(self):
        with open(self.archivo_sobrantes_anuales, 'w', encoding='utf-8') as f:
            json.dump(self.sobrantes_anuales, f, ensure_ascii=False, indent=2)

    def guardar_categorias_personalizadas(self):
        with open(self.archivo_categorias_personalizadas, 'w', encoding='utf-8') as f:
            json.dump(self.categorias_personalizadas, f, ensure_ascii=False, indent=2)
    
    def actualizar_todas_categorias_combos(self):
        todas_categorias = list(self.categorias_agricolas.keys())
    
        for cat in self.categorias_personalizadas.keys():
            if cat not in todas_categorias:
                todas_categorias.append(cat)
    
        todas_categorias.sort()
    
        if hasattr(self, 'combo_categoria'):
            valor_actual = self.combo_categoria.get()
            self.combo_categoria['values'] = todas_categorias
            if valor_actual in todas_categorias:
                self.combo_categoria.set(valor_actual)
            elif todas_categorias:
                self.combo_categoria.current(0)
                if hasattr(self, 'actualizar_subcategorias'):
                    try:
                        self.actualizar_subcategorias()
                    except:
                        pass
    
        if hasattr(self, 'combo_categoria_proveedor'):
            valor_actual = self.combo_categoria_proveedor.get()
            self.combo_categoria_proveedor['values'] = todas_categorias
            if valor_actual in todas_categorias:
                self.combo_categoria_proveedor.set(valor_actual)
            elif todas_categorias:
                self.combo_categoria_proveedor.current(0)
    
        if hasattr(self, 'combo_cat_para_subcat'):
            valor_actual = self.combo_cat_para_subcat.get()
            self.combo_cat_para_subcat['values'] = todas_categorias
            if valor_actual in todas_categorias:
                self.combo_cat_para_subcat.set(valor_actual)
    
        if hasattr(self, 'combo_cat_eliminar'):
            valor_actual = self.combo_cat_eliminar.get()
            self.combo_cat_eliminar['values'] = todas_categorias
            if valor_actual in todas_categorias:
                self.combo_cat_eliminar.set(valor_actual)
        
        if hasattr(self, 'combo_categoria_origen_sobrante'):
            valor_actual = self.combo_categoria_origen_sobrante.get()
            self.combo_categoria_origen_sobrante['values'] = todas_categorias
            if valor_actual in todas_categorias:
                self.combo_categoria_origen_sobrante.set(valor_actual)
                
        if hasattr(self, 'combo_categoria_destino'):
            valor_actual = self.combo_categoria_destino.get()
            self.combo_categoria_destino['values'] = todas_categorias
            if valor_actual in todas_categorias:
                self.combo_categoria_destino.set(valor_actual)

        if hasattr(self, 'regenerar_presupuesto_categorias'):
            try:
                self.regenerar_presupuesto_categorias()
            except:
                pass

def main():
    seguridad = SistemaSeguridad()
    root_login = tk.Tk()
    ventana_login = VentanaLogin(root_login, seguridad)
    root_login.mainloop()
    
    if not ventana_login.login_exitoso:
        return
        
    root = tk.Tk()
    app = SistemaFinancieroAgricolaSeguro(
        root, 
        ventana_login.usuario_actual, 
        seguridad
    )
    root.mainloop()

if __name__ == "__main__":
    main()