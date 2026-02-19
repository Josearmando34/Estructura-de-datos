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

class SistemaFinancieroAgricola:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Gestión Financiera - Empresa Agrícola")
        self.root.geometry("1400x800")
        self.root.configure(bg='#2d5016')
        
        self.archivo_datos = "agricultura_finanzas.json"
        self.archivo_presupuesto = "agricultura_presupuesto.json"
        self.archivo_proveedores = "agricultura_proveedores.json"
        self.archivo_presupuesto_mensual = "agricultura_presupuesto_mensual.json"
        self.archivo_presupuestos_anuales = "agricultura_presupuestos_anuales.json"
        self.archivo_sobrantes_anuales = "agricultura_sobrantes_anuales.json"
        self.archivo_categorias_personalizadas = "agricultura_categorias_personalizadas.json"
        
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
        
    def configurar_estilos(self):
        style = ttk.Style()
        style.theme_use('clam')
        

        style.configure('Title.TLabel', font=('Arial', 18, 'bold'), 
                       background='#2d5016', foreground='white')
        style.configure('Header.TLabel', font=('Arial', 13, 'bold'), 
                       background='#f0f0f0')
        style.configure('TButton', font=('Arial', 10, 'bold'))
        style.configure('Treeview', rowheight=28)
        style.configure('Treeview.Heading', font=('Arial', 10, 'bold'))
        
    def crear_widgets(self):

        header = tk.Frame(self.root, bg='#2d5016', height=80)
        header.pack(fill='x')
        
        tk.Label(header, text="SISTEMA DE GESTIÓN FINANCIERA AGRÍCOLA", 
                font=('Arial', 20, 'bold'), bg='#2d5016', fg='white').pack(pady=20)
        

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        

        self.tab_gestion_año = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_gestion_año, text='Gestión de Años')
        self.crear_tab_gestion_año()
        
        self.tab_categorias_custom = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_categorias_custom, text='Gestionar Categorías')
        self.crear_tab_categorias_custom()
        
        self.tab_presupuesto_mensual = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_presupuesto_mensual, text='Presupuesto Mensual')
        self.crear_tab_presupuesto_mensual()
        
        self.tab_proveedores = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_proveedores, text='Catálogo de Proveedores')
        self.crear_tab_proveedores()
        
        self.tab_registro = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_registro, text='Registro de Gastos')
        self.crear_tab_registro()
        
        self.tab_control = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_control, text='Control Mensual')
        self.crear_tab_control()
        
        self.tab_sobrantes = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_sobrantes, text='Gestión de Sobrantes')
        self.crear_tab_sobrantes()
        
        self.tab_graficos = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_graficos, text='Gráficos y Análisis')
        self.crear_tab_graficos()
    

    def crear_tab_gestion_año(self):
        """"""
        

        frame_info = ttk.LabelFrame(self.tab_gestion_año, 
                                    text=f"Información del Año {self.año_actual}", 
                                    padding=15)
        frame_info.pack(fill='x', padx=10, pady=10)
        

        frame_cards = tk.Frame(frame_info, bg='white')
        frame_cards.pack(fill='x', pady=10)
        

        card1 = tk.Frame(frame_cards, bg='#2196F3', relief='raised', bd=3)
        card1.pack(side='left', fill='both', expand=True, padx=10)
        tk.Label(card1, text="AÑO ACTUAL", 
                font=('Arial', 11, 'bold'), bg='#2196F3', fg='white').pack(pady=8)
        tk.Label(card1, text=str(self.año_actual), 
                font=('Arial', 20, 'bold'), bg='#2196F3', fg='white').pack(pady=8)
        

        card2 = tk.Frame(frame_cards, bg='#4CAF50', relief='raised', bd=3)
        card2.pack(side='left', fill='both', expand=True, padx=10)
        tk.Label(card2, text="SOBRANTE AÑO ANTERIOR", 
                font=('Arial', 11, 'bold'), bg='#4CAF50', fg='white').pack(pady=8)
        self.label_sobrante_anterior = tk.Label(card2, text="$0.00", 
                                               font=('Arial', 20, 'bold'), 
                                               bg='#4CAF50', fg='white')
        self.label_sobrante_anterior.pack(pady=8)
        

        card3 = tk.Frame(frame_cards, bg='#FF9800', relief='raised', bd=3)
        card3.pack(side='left', fill='both', expand=True, padx=10)
        tk.Label(card3, text="PRESUPUESTO ESTE AÑO", 
                font=('Arial', 11, 'bold'), bg='#FF9800', fg='white').pack(pady=8)
        self.label_presupuesto_año_actual = tk.Label(card3, text="$0.00", 
                                                     font=('Arial', 20, 'bold'), 
                                                     bg='#FF9800', fg='white')
        self.label_presupuesto_año_actual.pack(pady=8)
        

        frame_acciones = ttk.LabelFrame(self.tab_gestion_año, 
                                       text="Gestión de Años y Presupuestos", 
                                       padding=15)
        frame_acciones.pack(fill='x', padx=10, pady=10)
        

        frame_botones = tk.Frame(frame_acciones, bg='white')
        frame_botones.pack(fill='x', pady=10)
        
        ttk.Button(frame_botones, text="Crear Presupuesto Nuevo Año", 
                  command=self.crear_presupuesto_nuevo_año,
                  width=30).pack(side='left', padx=5)
        
        ttk.Button(frame_botones, text="Ver Presupuestos Anteriores", 
                  command=self.ver_presupuestos_anteriores,
                  width=30).pack(side='left', padx=5)
        
        ttk.Button(frame_botones, text="Actualizar Información", 
                  command=self.actualizar_info_año,
                  width=30).pack(side='left', padx=5)
        

        frame_sobrantes = ttk.LabelFrame(self.tab_gestion_año, 
                                        text="Gestión del Sobrante del Año Anterior", 
                                        padding=15)
        frame_sobrantes.pack(fill='both', expand=True, padx=10, pady=10)
        
        tk.Label(frame_sobrantes, 
                text="Indique qué hacer con el sobrante del año anterior:",
                font=('Arial', 11, 'bold')).pack(pady=10)
        

        self.opcion_sobrante_var = tk.StringVar(value="fondo_emergencia")
        
        opciones_frame = tk.Frame(frame_sobrantes, bg='white')
        opciones_frame.pack(fill='both', expand=True, pady=10)
        
        opciones = [
            ("Añadir al Fondo de Emergencias", "fondo_emergencia", 
             "Guardar el dinero para situaciones imprevistas"),
            (" Distribuir en el Presupuesto del Nuevo Año", "distribuir", 
             "Repartir proporcionalmente entre categorías"),
            ("Inversión en Infraestructura", "infraestructura", 
             "Destinar a mejoras de la finca"),
            (" Capacitación y Tecnología", "capacitacion", 
             "Invertir en formación y nuevas tecnologías"),
            (" Dividir según Porcentajes Personalizados", "personalizado", 
             "Tú decides cómo repartir el dinero")
        ]
        
        row = 0
        for texto, valor, descripcion in opciones:
            frame_opcion = tk.Frame(opciones_frame, bg='#f5f5f5', relief='raised', bd=1)
            frame_opcion.pack(fill='x', padx=10, pady=5)
            
            ttk.Radiobutton(frame_opcion, text=texto, variable=self.opcion_sobrante_var, 
                          value=valor).pack(side='left', padx=10, pady=5)
            
            tk.Label(frame_opcion, text=descripcion, font=('Arial', 9), 
                    bg='#f5f5f5', fg='#666').pack(side='left', padx=10)
        

        ttk.Button(frame_sobrantes, text="Aplicar Decisión sobre Sobrante", 
                  command=self.aplicar_decision_sobrante,
                  width=40).pack(pady=15)
        

        frame_historial = ttk.LabelFrame(self.tab_gestion_año, 
                                        text="Historial de Años", 
                                        padding=10)
        frame_historial.pack(fill='both', expand=True, padx=10, pady=10)
        
        scroll_y = ttk.Scrollbar(frame_historial, orient='vertical')
        scroll_y.pack(side='right', fill='y')
        
        columnas = ('Año', 'Presupuesto Total', 'Gastado', 'Sobrante', 'Decisión Sobrante')
        self.tree_historial_años = ttk.Treeview(frame_historial, columns=columnas, 
                                               show='headings', yscrollcommand=scroll_y.set)
        scroll_y.config(command=self.tree_historial_años.yview)
        
        for col in columnas:
            self.tree_historial_años.heading(col, text=col)
            self.tree_historial_años.column(col, width=150, anchor='center')
        
        self.tree_historial_años.pack(fill='both', expand=True)
        
        self.actualizar_info_año()
    
    def crear_presupuesto_nuevo_año(self):
        """"""
        

        if str(self.año_actual) in self.presupuestos_por_año:
            if not messagebox.askyesno("Confirmar", 
                f"Ya existe un presupuesto para {self.año_actual}.\n¿Desea crear uno nuevo desde cero?"):
                return
        

        año_nuevo = simpledialog.askinteger("Nuevo Año", 
                                            f"Ingrese el año para el nuevo presupuesto\n(Actual: {self.año_actual})",
                                            minvalue=self.año_actual,
                                            maxvalue=self.año_actual + 10)
        
        if not año_nuevo:
            return
        

        opciones = messagebox.askquestion("Método de Creación",
                                         "¿Desea copiar el presupuesto del año anterior?\n\n" +
                                         "SÍ: Copiar presupuesto del año anterior\n" +
                                         "NO: Crear presupuesto vacío desde cero",
                                         icon='question')
        
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
        

        if messagebox.askyesno("Cambiar Año", 
                              f"¿Desea cambiar al año {año_nuevo} ahora?"):
            self.año_actual = año_nuevo
            self.presupuesto_mensual_por_mes = self.presupuestos_por_año.get(str(año_nuevo), {})
            self.actualizar_info_año()
            messagebox.showinfo("Éxito", f"Ahora está trabajando con el año {año_nuevo}")
    
    def ver_presupuestos_anteriores(self):
        """"""
        
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
        if años_disponibles:
            combo_año.current(0)
        
        ttk.Button(frame_sel, text="Ver Detalles", 
                  command=lambda: self.mostrar_detalle_año(combo_año.get(), text_detalle)).pack(side='left', padx=10)
        

        frame_texto = ttk.Frame(ventana, padding=10)
        frame_texto.pack(fill='both', expand=True)
        
        scroll_y = ttk.Scrollbar(frame_texto, orient='vertical')
        scroll_y.pack(side='right', fill='y')
        
        text_detalle = tk.Text(frame_texto, height=30, width=90, 
                              font=('Courier', 10), yscrollcommand=scroll_y.set)
        text_detalle.pack(fill='both', expand=True)
        scroll_y.config(command=text_detalle.yview)
        

        if años_disponibles:
            self.mostrar_detalle_año(años_disponibles[0], text_detalle)
    
    def mostrar_detalle_año(self, año, text_widget):
        """"""
        text_widget.delete('1.0', 'end')
        
        if not año or año not in self.presupuestos_por_año:
            text_widget.insert('1.0', "Seleccione un año válido")
            return
        
        presupuesto = self.presupuestos_por_año[año]
        
        texto = f"{'=' * 80}\n"
        texto += f"PRESUPUESTO DEL AÑO {año}\n"
        texto += f"{'=' * 80}\n\n"
        
        if not presupuesto:
            texto += "No hay presupuesto configurado para este año\n"
            text_widget.insert('1.0', texto)
            return
        

        total_año = 0
        for mes in self.meses:
            if mes in presupuesto:
                total_mes = sum(presupuesto[mes].values())
                total_año += total_mes
                texto += f"\n{mes.upper()}: ${total_mes:,.2f}\n"
                texto += f"{'-' * 80}\n"
                
                for categoria, monto in sorted(presupuesto[mes].items()):
                    texto += f"  {categoria:<40} ${monto:>12,.2f}\n"
        
        texto += f"\n{'=' * 80}\n"
        texto += f"TOTAL PRESUPUESTADO EN {año}: ${total_año:,.2f}\n"
        texto += f"{'=' * 80}\n"
        
        text_widget.insert('1.0', texto)
    
    def aplicar_decision_sobrante(self):
        """"""
        

        año_anterior = self.año_actual - 1
        sobrante = self.calcular_sobrante_año(año_anterior)
        
        if sobrante <= 0:
            messagebox.showinfo("Sin Sobrante", 
                              f"No hay sobrante del año {año_anterior} para gestionar")
            return
        
        opcion = self.opcion_sobrante_var.get()
        
        if opcion == "fondo_emergencia":
            self.sobrantes_anuales[str(año_anterior)] = {
                'monto': sobrante,
                'decision': 'Fondo de Emergencias',
                'fecha': datetime.now().strftime('%Y-%m-%d')
            }
            messagebox.showinfo("Éxito", 
                              f"${sobrante:,.2f} guardado en Fondo de Emergencias\n\n" +
                              "Este dinero está disponible para situaciones imprevistas.")
        
        elif opcion == "distribuir":

            if not self.presupuesto_mensual_por_mes:
                messagebox.showwarning("Advertencia", 
                                     "Primero debe configurar el presupuesto del año actual")
                return
            
            self.distribuir_sobrante_en_presupuesto(sobrante)
            self.sobrantes_anuales[str(año_anterior)] = {
                'monto': sobrante,
                'decision': 'Distribuido en Presupuesto',
                'fecha': datetime.now().strftime('%Y-%m-%d')
            }
            messagebox.showinfo("Éxito", 
                              f"${sobrante:,.2f} distribuido proporcionalmente\nen el presupuesto del año {self.año_actual}")
        
        elif opcion == "infraestructura":

            if "Enero" not in self.presupuesto_mensual_por_mes:
                self.presupuesto_mensual_por_mes["Enero"] = {}
            
            if "Infraestructura" not in self.presupuesto_mensual_por_mes["Enero"]:
                self.presupuesto_mensual_por_mes["Enero"]["Infraestructura"] = 0
            
            self.presupuesto_mensual_por_mes["Enero"]["Infraestructura"] += sobrante
            self.sobrantes_anuales[str(año_anterior)] = {
                'monto': sobrante,
                'decision': 'Inversión en Infraestructura',
                'fecha': datetime.now().strftime('%Y-%m-%d')
            }
            messagebox.showinfo("Éxito", 
                              f"${sobrante:,.2f} añadido a Infraestructura\nen el presupuesto de Enero {self.año_actual}")
        
        elif opcion == "capacitacion":

            if "Enero" not in self.presupuesto_mensual_por_mes:
                self.presupuesto_mensual_por_mes["Enero"] = {}
            
            self.presupuesto_mensual_por_mes["Enero"]["Capacitación y Tecnología"] = sobrante
            self.sobrantes_anuales[str(año_anterior)] = {
                'monto': sobrante,
                'decision': 'Capacitación y Tecnología',
                'fecha': datetime.now().strftime('%Y-%m-%d')
            }
            messagebox.showinfo("Éxito", 
                              f"${sobrante:,.2f} asignado a Capacitación y Tecnología\nen el presupuesto de Enero {self.año_actual}")
        
        elif opcion == "personalizado":
            self.distribuir_sobrante_personalizado(sobrante, año_anterior)
            return
        
        self.guardar_sobrantes_anuales()
        self.guardar_datos()
        self.actualizar_info_año()
    
    def calcular_sobrante_año(self, año):
        """"""

        presupuesto_año = self.presupuestos_por_año.get(str(año), {})
        
        if not presupuesto_año:
            return 0
        
        total_presupuestado = 0
        for mes_data in presupuesto_año.values():
            total_presupuestado += sum(mes_data.values())
        

        total_gastado = sum(
            t['monto'] for t in self.transacciones
            if datetime.strptime(t['fecha'], '%Y-%m-%d').year == año
        )
        
        return total_presupuestado - total_gastado
    
    def distribuir_sobrante_en_presupuesto(self, sobrante):
        """"""
        
        if not self.presupuesto_mensual_por_mes:
            return
        

        total_presupuesto_actual = 0
        for mes_data in self.presupuesto_mensual_por_mes.values():
            total_presupuesto_actual += sum(mes_data.values())
        
        if total_presupuesto_actual == 0:
            return
        

        for mes in self.presupuesto_mensual_por_mes:
            for categoria in self.presupuesto_mensual_por_mes[mes]:
                monto_actual = self.presupuesto_mensual_por_mes[mes][categoria]
                proporcion = monto_actual / total_presupuesto_actual
                incremento = sobrante * proporcion
                self.presupuesto_mensual_por_mes[mes][categoria] += incremento
        
        self.guardar_datos()
    
    def distribuir_sobrante_personalizado(self, sobrante, año_anterior):
        """"""
        

        ventana = tk.Toplevel(self.root)
        ventana.title(" Distribución Personalizada del Sobrante")
        ventana.geometry("700x600")
        
        tk.Label(ventana, text=f"Sobrante a Distribuir: ${sobrante:,.2f}", 
                font=('Arial', 14, 'bold'), fg='#4CAF50').pack(pady=10)
        
        tk.Label(ventana, text="Asigne porcentajes a cada categoría (debe sumar 100%)", 
                font=('Arial', 10)).pack(pady=5)
        

        frame_container = ttk.Frame(ventana, padding=10)
        frame_container.pack(fill='both', expand=True)
        
        canvas = tk.Canvas(frame_container)
        scrollbar = ttk.Scrollbar(frame_container, orient="vertical", command=canvas.yview)
        frame_categorias = tk.Frame(canvas)
        
        frame_categorias.bind("<Configure>", 
                             lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=frame_categorias, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        

        porcentaje_entries = {}
        monto_labels = {}
        
        todas_categorias = list(self.categorias_agricolas.keys()) + list(self.categorias_personalizadas.keys())
        
        for i, categoria in enumerate(todas_categorias):
            frame = tk.Frame(frame_categorias, bg='#f5f5f5', relief='raised', bd=1)
            frame.pack(fill='x', padx=5, pady=3)
            
            tk.Label(frame, text=categoria, width=30, anchor='w', bg='#f5f5f5').pack(side='left', padx=5)
            
            tk.Label(frame, text="%:", bg='#f5f5f5').pack(side='left')
            entry = ttk.Entry(frame, width=10)
            entry.pack(side='left', padx=5)
            entry.insert(0, "0")
            porcentaje_entries[categoria] = entry
            
            label_monto = tk.Label(frame, text="$0.00", width=15, anchor='e', 
                                  bg='#f5f5f5', fg='#666')
            label_monto.pack(side='left', padx=10)
            monto_labels[categoria] = label_monto
            

            entry.bind('<KeyRelease>', 
                      lambda e, cat=categoria: self.actualizar_monto_distribucion(
                          porcentaje_entries[cat], monto_labels[cat], sobrante))
        

        frame_total = tk.Frame(ventana, bg='#e3f2fd', relief='raised', bd=2)
        frame_total.pack(fill='x', padx=10, pady=10)
        
        label_total_porcentaje = tk.Label(frame_total, text="Total: 0%", 
                                         font=('Arial', 12, 'bold'), bg='#e3f2fd')
        label_total_porcentaje.pack(pady=5)
        
        def actualizar_total():
            total = 0
            for entry in porcentaje_entries.values():
                try:
                    total += float(entry.get())
                except:
                    pass
            
            label_total_porcentaje.config(text=f"Total: {total:.1f}%")
            
            if abs(total - 100) < 0.01:
                label_total_porcentaje.config(fg='#4CAF50')
            else:
                label_total_porcentaje.config(fg='#f44336')
            
            return total
        

        for entry in porcentaje_entries.values():
            entry.bind('<KeyRelease>', lambda e: actualizar_total())
        

        def aplicar_distribucion():
            total = actualizar_total()
            
            if abs(total - 100) > 0.01:
                messagebox.showerror("Error", 
                                   f"Los porcentajes deben sumar 100%\nActual: {total:.1f}%")
                return
            

            for categoria, entry in porcentaje_entries.items():
                try:
                    porcentaje = float(entry.get())
                    if porcentaje > 0:
                        monto = sobrante * (porcentaje / 100)
                        

                        if "Enero" not in self.presupuesto_mensual_por_mes:
                            self.presupuesto_mensual_por_mes["Enero"] = {}
                        
                        if categoria not in self.presupuesto_mensual_por_mes["Enero"]:
                            self.presupuesto_mensual_por_mes["Enero"][categoria] = 0
                        
                        self.presupuesto_mensual_por_mes["Enero"][categoria] += monto
                except:
                    pass
            
            self.sobrantes_anuales[str(año_anterior)] = {
                'monto': sobrante,
                'decision': 'Distribución Personalizada',
                'fecha': datetime.now().strftime('%Y-%m-%d')
            }
            
            self.guardar_sobrantes_anuales()
            self.guardar_datos()
            self.actualizar_info_año()
            
            messagebox.showinfo("Éxito", "Distribución aplicada correctamente")
            ventana.destroy()
        
        ttk.Button(ventana, text=" Aplicar Distribución", 
                  command=aplicar_distribucion).pack(pady=10)
        
        actualizar_total()
    
    def actualizar_monto_distribucion(self, entry, label, sobrante_total):
        """"""
        try:
            porcentaje = float(entry.get())
            monto = sobrante_total * (porcentaje / 100)
            label.config(text=f"${monto:,.2f}")
        except:
            label.config(text="$0.00")
    
    def actualizar_info_año(self):
        """"""
        

        año_anterior = self.año_actual - 1
        sobrante_anterior = self.calcular_sobrante_año(año_anterior)
        self.label_sobrante_anterior.config(text=f"${sobrante_anterior:,.2f}")
        

        presupuesto_actual = 0
        if str(self.año_actual) in self.presupuestos_por_año:
            for mes_data in self.presupuestos_por_año[str(self.año_actual)].values():
                presupuesto_actual += sum(mes_data.values())
        
        self.label_presupuesto_año_actual.config(text=f"${presupuesto_actual:,.2f}")
        

        for item in self.tree_historial_años.get_children():
            self.tree_historial_años.delete(item)
        
        for año in sorted(self.presupuestos_por_año.keys(), reverse=True):
            presupuesto_total = 0
            for mes_data in self.presupuestos_por_año[año].values():
                presupuesto_total += sum(mes_data.values())
            
            gastado = sum(
                t['monto'] for t in self.transacciones
                if datetime.strptime(t['fecha'], '%Y-%m-%d').year == int(año)
            )
            
            sobrante = presupuesto_total - gastado
            
            decision = "N/A"
            if año in self.sobrantes_anuales:
                decision = self.sobrantes_anuales[año].get('decision', 'N/A')
            
            self.tree_historial_años.insert('', 'end', values=(
                año,
                f"${presupuesto_total:,.2f}",
                f"${gastado:,.2f}",
                f"${sobrante:,.2f}",
                decision
            ))
    

    def crear_tab_categorias_custom(self):
        """"""
        
        frame_instrucciones = ttk.LabelFrame(self.tab_categorias_custom, 
                                            text="Información", padding=10)
        frame_instrucciones.pack(fill='x', padx=10, pady=10)
        
        tk.Label(frame_instrucciones, 
                text="Aquí puede agregar nuevas categorías y subcategorías personalizadas para su empresa.\n" +
                     "Las categorías predefinidas no pueden eliminarse, pero puede agregar subcategorías a ellas.",
                font=('Arial', 10), wraplength=1300, justify='left').pack()
        

        frame_acciones = ttk.LabelFrame(self.tab_categorias_custom, 
                                       text=" Agregar Nueva Categoría", padding=15)
        frame_acciones.pack(fill='x', padx=10, pady=10)
        

        frame_nueva_cat = tk.Frame(frame_acciones)
        frame_nueva_cat.pack(fill='x', pady=5)
        
        tk.Label(frame_nueva_cat, text="Nombre de la categoría:", 
                font=('Arial', 10, 'bold')).pack(side='left', padx=5)
        self.entry_nueva_categoria = ttk.Entry(frame_nueva_cat, width=40)
        self.entry_nueva_categoria.pack(side='left', padx=5)
        
        ttk.Button(frame_nueva_cat, text=" Crear Categoría", 
                  command=self.agregar_nueva_categoria).pack(side='left', padx=10)
        

        frame_nueva_subcat = ttk.LabelFrame(self.tab_categorias_custom, 
                                           text=" Agregar Subcategoría", padding=15)
        frame_nueva_subcat.pack(fill='x', padx=10, pady=10)
        
        frame_sub = tk.Frame(frame_nueva_subcat)
        frame_sub.pack(fill='x', pady=5)
        
        tk.Label(frame_sub, text="Categoría:", font=('Arial', 10, 'bold')).pack(side='left', padx=5)
        
        self.combo_cat_para_subcat = ttk.Combobox(frame_sub, state='readonly', width=30)
        self.combo_cat_para_subcat.pack(side='left', padx=5)
        
        tk.Label(frame_sub, text="Subcategoría:", font=('Arial', 10, 'bold')).pack(side='left', padx=10)
        self.entry_nueva_subcategoria = ttk.Entry(frame_sub, width=30)
        self.entry_nueva_subcategoria.pack(side='left', padx=5)
        
        ttk.Button(frame_sub, text=" Agregar Subcategoría", 
                  command=self.agregar_nueva_subcategoria).pack(side='left', padx=10)
        

        frame_lista = ttk.LabelFrame(self.tab_categorias_custom, 
                                    text=" Categorías y Subcategorías Actuales", 
                                    padding=10)
        frame_lista.pack(fill='both', expand=True, padx=10, pady=10)
        

        frame_scroll = ttk.Frame(frame_lista)
        frame_scroll.pack(fill='both', expand=True)
        
        scroll_y = ttk.Scrollbar(frame_scroll, orient='vertical')
        scroll_y.pack(side='right', fill='y')
        
        self.text_categorias = tk.Text(frame_scroll, height=20, width=100, 
                                      font=('Courier', 10), yscrollcommand=scroll_y.set)
        self.text_categorias.pack(fill='both', expand=True)
        scroll_y.config(command=self.text_categorias.yview)
        

        frame_eliminar = ttk.LabelFrame(self.tab_categorias_custom, 
                                       text=" Eliminar Categoría o Subcategoría", 
                                       padding=15)
        frame_eliminar.pack(fill='x', padx=10, pady=10)
        
        frame_elim = tk.Frame(frame_eliminar)
        frame_elim.pack(fill='x', pady=5)
        
        tk.Label(frame_elim, text="Categoría:", font=('Arial', 10, 'bold')).pack(side='left', padx=5)
        self.combo_cat_eliminar = ttk.Combobox(frame_elim, state='readonly', width=30)
        self.combo_cat_eliminar.pack(side='left', padx=5)
        self.combo_cat_eliminar.bind('<<ComboboxSelected>>', self.actualizar_subcats_eliminar)
        
        tk.Label(frame_elim, text="Subcategoría:", font=('Arial', 10, 'bold')).pack(side='left', padx=10)
        self.combo_subcat_eliminar = ttk.Combobox(frame_elim, state='readonly', width=30)
        self.combo_subcat_eliminar.pack(side='left', padx=5)
        
        ttk.Button(frame_elim, text=" Eliminar Categoría Completa", 
                  command=self.eliminar_categoria).pack(side='left', padx=10)
        ttk.Button(frame_elim, text=" Eliminar Solo Subcategoría", 
                  command=self.eliminar_subcategoria).pack(side='left', padx=5)
        

        ttk.Button(self.tab_categorias_custom, text=" Actualizar Vista", 
                  command=self.actualizar_vista_categorias).pack(pady=10)
        
        self.actualizar_vista_categorias()
    
    def agregar_nueva_categoria(self):
        """"""
        nombre = self.entry_nueva_categoria.get().strip()
        
        if not nombre:
            messagebox.showwarning("Advertencia", "Debe ingresar un nombre para la categoría")
            return
        

        todas_categorias = {**self.categorias_agricolas, **self.categorias_personalizadas}
        
        if nombre in todas_categorias:
            messagebox.showwarning("Advertencia", "Esta categoría ya existe")
            return
        

        self.categorias_personalizadas[nombre] = []
        self.guardar_categorias_personalizadas()
        
        self.entry_nueva_categoria.delete(0, 'end')
        self.actualizar_vista_categorias()
        
        messagebox.showinfo("Éxito", f"Categoría '{nombre}' creada correctamente")
    
    def agregar_nueva_subcategoria(self):
        """"""
        categoria = self.combo_cat_para_subcat.get()
        subcategoria = self.entry_nueva_subcategoria.get().strip()
        
        if not categoria:
            messagebox.showwarning("Advertencia", "Debe seleccionar una categoría")
            return
        
        if not subcategoria:
            messagebox.showwarning("Advertencia", "Debe ingresar un nombre para la subcategoría")
            return
        

        if categoria in self.categorias_personalizadas:
            if subcategoria in self.categorias_personalizadas[categoria]:
                messagebox.showwarning("Advertencia", "Esta subcategoría ya existe")
                return
            self.categorias_personalizadas[categoria].append(subcategoria)
        elif categoria in self.categorias_agricolas:

            if categoria not in self.categorias_personalizadas:
                self.categorias_personalizadas[categoria] = list(self.categorias_agricolas[categoria])
            if subcategoria in self.categorias_personalizadas[categoria]:
                messagebox.showwarning("Advertencia", "Esta subcategoría ya existe")
                return
            self.categorias_personalizadas[categoria].append(subcategoria)
        
        self.guardar_categorias_personalizadas()
        self.entry_nueva_subcategoria.delete(0, 'end')
        self.actualizar_vista_categorias()
        
        messagebox.showinfo("Éxito", f"Subcategoría '{subcategoria}' agregada a '{categoria}'")
    
    def eliminar_categoria(self):
        """"""
        categoria = self.combo_cat_eliminar.get()
        
        if not categoria:
            messagebox.showwarning("Advertencia", "Debe seleccionar una categoría")
            return
        
        if categoria in self.categorias_agricolas and categoria not in self.categorias_personalizadas:
            messagebox.showwarning("Advertencia", 
                                 "No se pueden eliminar las categorías predefinidas del sistema")
            return
        
        if not messagebox.askyesno("Confirmar", 
                                   f"¿Está seguro de eliminar la categoría '{categoria}'?"):
            return
        
        if categoria in self.categorias_personalizadas:
            del self.categorias_personalizadas[categoria]
            self.guardar_categorias_personalizadas()
            self.actualizar_vista_categorias()
            messagebox.showinfo("Éxito", f"Categoría '{categoria}' eliminada")
    
    def eliminar_subcategoria(self):
        """"""
        categoria = self.combo_cat_eliminar.get()
        subcategoria = self.combo_subcat_eliminar.get()
        
        if not categoria or not subcategoria:
            messagebox.showwarning("Advertencia", "Debe seleccionar categoría y subcategoría")
            return
        
        if not messagebox.askyesno("Confirmar", 
                                   f"¿Está seguro de eliminar '{subcategoria}' de '{categoria}'?"):
            return
        

        if categoria in self.categorias_agricolas and categoria not in self.categorias_personalizadas:
            self.categorias_personalizadas[categoria] = list(self.categorias_agricolas[categoria])
        
        if categoria in self.categorias_personalizadas:
            if subcategoria in self.categorias_personalizadas[categoria]:
                self.categorias_personalizadas[categoria].remove(subcategoria)
                self.guardar_categorias_personalizadas()
                self.actualizar_vista_categorias()
                messagebox.showinfo("Éxito", f"Subcategoría '{subcategoria}' eliminada")
    
    def actualizar_subcats_eliminar(self, event=None):
        """"""
        categoria = self.combo_cat_eliminar.get()
        
        if not categoria:
            self.combo_subcat_eliminar['values'] = []
            return
        

        if categoria in self.categorias_personalizadas:
            subcats = self.categorias_personalizadas[categoria]
        elif categoria in self.categorias_agricolas:
            subcats = self.categorias_agricolas[categoria]
        else:
            subcats = []
        
        self.combo_subcat_eliminar['values'] = subcats
        if subcats:
            self.combo_subcat_eliminar.current(0)
    
    def actualizar_vista_categorias(self):
        """"""
        self.text_categorias.delete('1.0', 'end')
        

        todas_categorias = {}
        

        for cat, subcats in self.categorias_agricolas.items():
            todas_categorias[cat] = list(subcats)
        

        for cat, subcats in self.categorias_personalizadas.items():
            if cat in todas_categorias:

                todas_categorias[cat] = list(set(todas_categorias[cat] + subcats))
            else:
                todas_categorias[cat] = list(subcats)
        
        texto = "=" * 100 + "\n"
        texto += "CATEGORÍAS Y SUBCATEGORÍAS ACTUALES\n"
        texto += "=" * 100 + "\n\n"
        
        for categoria in sorted(todas_categorias.keys()):
            subcats = todas_categorias[categoria]
            

            tipo = ""
            if categoria in self.categorias_agricolas and categoria not in self.categorias_personalizadas:
                tipo = " [PREDEFINIDA]"
            elif categoria not in self.categorias_agricolas:
                tipo = " [PERSONALIZADA]"
            else:
                tipo = " [MIXTA]"
            
            texto += f"\n {categoria}{tipo}\n"
            texto += f"{'' * 100}\n"
            
            if subcats:
                for i, subcat in enumerate(sorted(subcats), 1):
                    texto += f"  {i}. {subcat}\n"
            else:
                texto += "  (Sin subcategorías)\n"
            
            texto += "\n"
        
        self.text_categorias.insert('1.0', texto)
        

        lista_categorias = sorted(todas_categorias.keys())
        self.combo_cat_para_subcat['values'] = lista_categorias
        self.combo_cat_eliminar['values'] = lista_categorias
        
        if lista_categorias:
            self.combo_cat_para_subcat.current(0)
            self.combo_cat_eliminar.current(0)
            self.actualizar_subcats_eliminar()
    

    def crear_tab_presupuesto_mensual(self):
        """"""
        

        frame_instrucciones = ttk.LabelFrame(self.tab_presupuesto_mensual, 
                                            text=" Instrucciones", padding=10)
        frame_instrucciones.pack(fill='x', padx=10, pady=10)
        
        tk.Label(frame_instrucciones, 
                text="Configure el presupuesto para cada mes y categoría. Puede asignar montos diferentes según sus necesidades.",
                font=('Arial', 10), wraplength=1300, justify='left').pack()
        

        frame_mes = ttk.Frame(self.tab_presupuesto_mensual)
        frame_mes.pack(fill='x', padx=10, pady=5)
        
        tk.Label(frame_mes, text="Seleccionar Mes:", font=('Arial', 12, 'bold')).pack(side='left', padx=5)
        self.combo_mes_presupuesto = ttk.Combobox(frame_mes, values=self.meses, 
                                                  state='readonly', width=15, font=('Arial', 11))
        self.combo_mes_presupuesto.pack(side='left', padx=5)
        self.combo_mes_presupuesto.current(0)
        self.combo_mes_presupuesto.bind('<<ComboboxSelected>>', self.cargar_presupuesto_mes)
        
        ttk.Button(frame_mes, text=" Copiar de Otro Mes", 
                  command=self.copiar_presupuesto_mes).pack(side='left', padx=5)
        ttk.Button(frame_mes, text=" Aplicar a Todos los Meses", 
                  command=self.aplicar_a_todos_meses).pack(side='left', padx=5)
        

        frame_categorias_container = ttk.LabelFrame(self.tab_presupuesto_mensual, 
                                                    text=" Presupuesto por Categoría", 
                                                    padding=10)
        frame_categorias_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        canvas = tk.Canvas(frame_categorias_container, bg='white')
        scrollbar = ttk.Scrollbar(frame_categorias_container, orient="vertical", command=canvas.yview)
        self.frame_categorias_presupuesto = tk.Frame(canvas, bg='white')
        
        self.frame_categorias_presupuesto.bind("<Configure>", 
                                              lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=self.frame_categorias_presupuesto, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        

        self.presupuesto_mensual_entries = {}
        self.presupuesto_mensual_labels_modificado = {}
        
        row = 0
        for categoria in self.categorias_agricolas.keys():

            frame_cat = tk.Frame(self.frame_categorias_presupuesto, bg='#e8f5e9', 
                                relief='raised', bd=2)
            frame_cat.grid(row=row, column=0, sticky='ew', padx=5, pady=5)
            self.frame_categorias_presupuesto.grid_columnconfigure(0, weight=1)
            

            tk.Label(frame_cat, text=categoria, font=('Arial', 11, 'bold'), 
                    bg='#e8f5e9', anchor='w').grid(row=0, column=0, sticky='w', padx=10, pady=5)
            

            tk.Label(frame_cat, text="Monto $:", bg='#e8f5e9').grid(row=0, column=1, padx=5)
            entry = ttk.Entry(frame_cat, width=15, font=('Arial', 10))
            entry.grid(row=0, column=2, padx=5)
            entry.insert(0, "0.00")
            self.presupuesto_mensual_entries[categoria] = entry
            

            label_mod = tk.Label(frame_cat, text="", bg='#e8f5e9', 
                                font=('Arial', 9, 'italic'), fg='red')
            label_mod.grid(row=0, column=3, padx=10)
            self.presupuesto_mensual_labels_modificado[categoria] = label_mod
            

            ttk.Button(frame_cat, text=" Modificar", 
                      command=lambda c=categoria: self.modificar_presupuesto_categoria(c)).grid(
                          row=0, column=4, padx=5)
            
            row += 1
        

        frame_botones = ttk.Frame(self.tab_presupuesto_mensual)
        frame_botones.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(frame_botones, text=" Guardar Presupuesto del Mes", 
                  command=self.guardar_presupuesto_mes, 
                  style='Accent.TButton').pack(side='left', padx=5)
        
        ttk.Button(frame_botones, text=" Ver Resumen Anual", 
                  command=self.mostrar_resumen_anual).pack(side='left', padx=5)
        

        self.cargar_presupuesto_mes()
    
    def cargar_presupuesto_mes(self, event=None):
        """"""
        mes = self.combo_mes_presupuesto.get()
        
        if mes in self.presupuesto_mensual_por_mes:
            presupuesto_mes = self.presupuesto_mensual_por_mes[mes]
            for categoria, entry in self.presupuesto_mensual_entries.items():
                entry.delete(0, tk.END)
                entry.insert(0, f"{presupuesto_mes.get(categoria, 0.00):.2f}")
                

                if mes in self.presupuesto_modificado and \
                   categoria in self.presupuesto_modificado[mes] and \
                   self.presupuesto_modificado[mes][categoria]:
                    self.presupuesto_mensual_labels_modificado[categoria].config(
                        text=" Modificado")
                else:
                    self.presupuesto_mensual_labels_modificado[categoria].config(text="")
        else:

            for entry in self.presupuesto_mensual_entries.values():
                entry.delete(0, tk.END)
                entry.insert(0, "0.00")
            for label in self.presupuesto_mensual_labels_modificado.values():
                label.config(text="")
    
    def guardar_presupuesto_mes(self):
        """"""
        mes = self.combo_mes_presupuesto.get()
        
        if mes not in self.presupuesto_mensual_por_mes:
            self.presupuesto_mensual_por_mes[mes] = {}
        
        for categoria, entry in self.presupuesto_mensual_entries.items():
            try:
                monto = float(entry.get())
                self.presupuesto_mensual_por_mes[mes][categoria] = monto
            except ValueError:
                messagebox.showerror("Error", 
                    f"Monto inválido en la categoría '{categoria}'")
                return
        
        self.guardar_datos()
        messagebox.showinfo("Éxito", f"Presupuesto de {mes} guardado correctamente")
    
    def modificar_presupuesto_categoria(self, categoria):
        """"""
        mes = self.combo_mes_presupuesto.get()
        entry = self.presupuesto_mensual_entries[categoria]
        
        nuevo_monto = simpledialog.askfloat(
            "Modificar Presupuesto",
            f"Ingrese el nuevo presupuesto para '{categoria}' en {mes}:",
            initialvalue=float(entry.get()),
            minvalue=0.0
        )
        
        if nuevo_monto is not None:
            entry.delete(0, tk.END)
            entry.insert(0, f"{nuevo_monto:.2f}")
            

            if mes not in self.presupuesto_modificado:
                self.presupuesto_modificado[mes] = {}
            self.presupuesto_modificado[mes][categoria] = True
            
            self.presupuesto_mensual_labels_modificado[categoria].config(
                text=" Modificado")
            
            messagebox.showinfo("Presupuesto Modificado", 
                f"El presupuesto de '{categoria}' para {mes} ha sido modificado a ${nuevo_monto:,.2f}")
    
    def copiar_presupuesto_mes(self):
        """"""
        mes_destino = self.combo_mes_presupuesto.get()
        

        ventana = tk.Toplevel(self.root)
        ventana.title("Copiar Presupuesto")
        ventana.geometry("300x150")
        
        tk.Label(ventana, text=f"Copiar presupuesto a {mes_destino} desde:", 
                font=('Arial', 11, 'bold')).pack(pady=10)
        
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
                messagebox.showinfo("Éxito", f"Presupuesto copiado de {mes_origen}")
                ventana.destroy()
            else:
                messagebox.showwarning("Advertencia", 
                    f"No hay presupuesto configurado para {mes_origen}")
        
        ttk.Button(ventana, text="Copiar", command=copiar).pack(pady=10)
    
    def aplicar_a_todos_meses(self):
        """"""
        if messagebox.askyesno("Confirmar", 
            "¿Desea aplicar este presupuesto a todos los meses del año?"):
            
            presupuesto_actual = {}
            for categoria, entry in self.presupuesto_mensual_entries.items():
                try:
                    presupuesto_actual[categoria] = float(entry.get())
                except ValueError:
                    messagebox.showerror("Error", "Hay montos inválidos")
                    return
            
            for mes in self.meses:
                self.presupuesto_mensual_por_mes[mes] = presupuesto_actual.copy()
            
            self.guardar_datos()
            messagebox.showinfo("Éxito", "Presupuesto aplicado a todos los meses")
    
    def mostrar_resumen_anual(self):
        """"""
        ventana = tk.Toplevel(self.root)
        ventana.title("Resumen Presupuesto Anual")
        ventana.geometry("800x600")
        
        text = scrolledtext.ScrolledText(ventana, font=('Courier', 10), wrap=tk.WORD)
        text.pack(fill='both', expand=True, padx=10, pady=10)
        
        text.insert('end', "=" * 80 + "\n")
        text.insert('end', "RESUMEN DE PRESUPUESTO ANUAL\n".center(80))
        text.insert('end', "=" * 80 + "\n\n")
        
        total_anual_por_categoria = defaultdict(float)
        
        for mes in self.meses:
            if mes in self.presupuesto_mensual_por_mes:
                text.insert('end', f"\n{mes.upper()}\n")
                text.insert('end', "-" * 80 + "\n")
                
                total_mes = 0
                for categoria, monto in self.presupuesto_mensual_por_mes[mes].items():
                    modificado = ""
                    if mes in self.presupuesto_modificado and \
                       categoria in self.presupuesto_modificado[mes] and \
                       self.presupuesto_modificado[mes][categoria]:
                        modificado = " "
                    
                    text.insert('end', f"  {categoria:40s} ${monto:>12,.2f}{modificado}\n")
                    total_mes += monto
                    total_anual_por_categoria[categoria] += monto
                
                text.insert('end', f"\n  {'TOTAL MES':40s} ${total_mes:>12,.2f}\n")
        
        text.insert('end', "\n" + "=" * 80 + "\n")
        text.insert('end', "TOTAL POR CATEGORÍA (AÑO COMPLETO)\n".center(80))
        text.insert('end', "=" * 80 + "\n\n")
        
        total_general = 0
        for categoria, total in sorted(total_anual_por_categoria.items()):
            text.insert('end', f"  {categoria:40s} ${total:>12,.2f}\n")
            total_general += total
        
        text.insert('end', "\n" + "=" * 80 + "\n")
        text.insert('end', f"  {'PRESUPUESTO TOTAL ANUAL':40s} ${total_general:>12,.2f}\n")
        text.insert('end', "=" * 80 + "\n")
        
        text.config(state='disabled')
    

    def crear_tab_proveedores(self):
        """"""
        

        frame_superior = ttk.Frame(self.tab_proveedores)
        frame_superior.pack(fill='x', padx=10, pady=10)
        
        tk.Label(frame_superior, text=" CATÁLOGO DE PROVEEDORES", 
                font=('Arial', 14, 'bold')).pack()
        

        frame_entrada = ttk.LabelFrame(self.tab_proveedores, text=" Agregar/Editar Proveedor", 
                                       padding=15)
        frame_entrada.pack(fill='x', padx=10, pady=10)
        

        tk.Label(frame_entrada, text="Nombre del Proveedor:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.entry_nombre_proveedor = ttk.Entry(frame_entrada, width=30)
        self.entry_nombre_proveedor.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(frame_entrada, text="Categoría:").grid(row=0, column=2, sticky='w', padx=5, pady=5)
        self.combo_categoria_proveedor = ttk.Combobox(frame_entrada, 
                                                      values=list(self.categorias_agricolas.keys()),
                                                      state='readonly', width=25)
        self.combo_categoria_proveedor.grid(row=0, column=3, padx=5, pady=5)
        
        tk.Label(frame_entrada, text="Teléfono:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.entry_telefono_proveedor = ttk.Entry(frame_entrada, width=30)
        self.entry_telefono_proveedor.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(frame_entrada, text="Email:").grid(row=1, column=2, sticky='w', padx=5, pady=5)
        self.entry_email_proveedor = ttk.Entry(frame_entrada, width=25)
        self.entry_email_proveedor.grid(row=1, column=3, padx=5, pady=5)
        
        tk.Label(frame_entrada, text="Dirección:").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.entry_direccion_proveedor = ttk.Entry(frame_entrada, width=30)
        self.entry_direccion_proveedor.grid(row=2, column=1, padx=5, pady=5)
        
        tk.Label(frame_entrada, text="Notas:").grid(row=2, column=2, sticky='w', padx=5, pady=5)
        self.entry_notas_proveedor = ttk.Entry(frame_entrada, width=25)
        self.entry_notas_proveedor.grid(row=2, column=3, padx=5, pady=5)
        

        frame_botones_prov = ttk.Frame(frame_entrada)
        frame_botones_prov.grid(row=3, column=0, columnspan=4, pady=10)
        
        ttk.Button(frame_botones_prov, text=" Agregar Proveedor", 
                  command=self.agregar_proveedor).pack(side='left', padx=5)
        ttk.Button(frame_botones_prov, text=" Actualizar Proveedor", 
                  command=self.actualizar_proveedor).pack(side='left', padx=5)
        ttk.Button(frame_botones_prov, text=" Eliminar Proveedor", 
                  command=self.eliminar_proveedor).pack(side='left', padx=5)
        ttk.Button(frame_botones_prov, text=" Limpiar Campos", 
                  command=self.limpiar_campos_proveedor).pack(side='left', padx=5)
        

        frame_busqueda = ttk.Frame(self.tab_proveedores)
        frame_busqueda.pack(fill='x', padx=10, pady=5)
        
        tk.Label(frame_busqueda, text="Buscar:").pack(side='left', padx=5)
        self.entry_buscar_proveedor = ttk.Entry(frame_busqueda, width=30)
        self.entry_buscar_proveedor.pack(side='left', padx=5)
        ttk.Button(frame_busqueda, text=" Buscar", 
                  command=self.buscar_proveedor).pack(side='left', padx=5)
        
        tk.Label(frame_busqueda, text="Filtrar por categoría:").pack(side='left', padx=15)
        self.combo_filtro_categoria = ttk.Combobox(frame_busqueda, 
                                                   values=["Todas"] + list(self.categorias_agricolas.keys()),
                                                   state='readonly', width=25)
        self.combo_filtro_categoria.pack(side='left', padx=5)
        self.combo_filtro_categoria.current(0)
        self.combo_filtro_categoria.bind('<<ComboboxSelected>>', self.filtrar_proveedores)
        

        frame_tabla = ttk.LabelFrame(self.tab_proveedores, text=" Lista de Proveedores", 
                                     padding=10)
        frame_tabla.pack(fill='both', expand=True, padx=10, pady=10)
        

        scroll_y = ttk.Scrollbar(frame_tabla, orient='vertical')
        scroll_x = ttk.Scrollbar(frame_tabla, orient='horizontal')
        
        self.tree_proveedores = ttk.Treeview(frame_tabla, 
                                             columns=('nombre', 'categoria', 'telefono', 'email', 'direccion', 'notas'),
                                             show='headings',
                                             yscrollcommand=scroll_y.set,
                                             xscrollcommand=scroll_x.set)
        
        scroll_y.config(command=self.tree_proveedores.yview)
        scroll_x.config(command=self.tree_proveedores.xview)
        

        self.tree_proveedores.heading('nombre', text='Nombre')
        self.tree_proveedores.heading('categoria', text='Categoría')
        self.tree_proveedores.heading('telefono', text='Teléfono')
        self.tree_proveedores.heading('email', text='Email')
        self.tree_proveedores.heading('direccion', text='Dirección')
        self.tree_proveedores.heading('notas', text='Notas')
        
        self.tree_proveedores.column('nombre', width=200)
        self.tree_proveedores.column('categoria', width=180)
        self.tree_proveedores.column('telefono', width=120)
        self.tree_proveedores.column('email', width=180)
        self.tree_proveedores.column('direccion', width=200)
        self.tree_proveedores.column('notas', width=200)
        
        self.tree_proveedores.grid(row=0, column=0, sticky='nsew')
        scroll_y.grid(row=0, column=1, sticky='ns')
        scroll_x.grid(row=1, column=0, sticky='ew')
        
        frame_tabla.grid_rowconfigure(0, weight=1)
        frame_tabla.grid_columnconfigure(0, weight=1)
        

        self.tree_proveedores.bind('<<TreeviewSelect>>', self.seleccionar_proveedor)
        

        self.actualizar_tabla_proveedores()
    
    def agregar_proveedor(self):
        """"""
        nombre = self.entry_nombre_proveedor.get().strip()
        categoria = self.combo_categoria_proveedor.get()
        telefono = self.entry_telefono_proveedor.get().strip()
        email = self.entry_email_proveedor.get().strip()
        direccion = self.entry_direccion_proveedor.get().strip()
        notas = self.entry_notas_proveedor.get().strip()
        
        if not nombre or not categoria:
            messagebox.showwarning("Advertencia", "El nombre y la categoría son obligatorios")
            return
        
        if nombre in self.proveedores:
            messagebox.showwarning("Advertencia", "Ya existe un proveedor con ese nombre")
            return
        
        self.proveedores[nombre] = {
            'categoria': categoria,
            'telefono': telefono,
            'email': email,
            'direccion': direccion,
            'notas': notas
        }
        
        self.guardar_datos()
        self.actualizar_tabla_proveedores()
        self.limpiar_campos_proveedor()
        messagebox.showinfo("Éxito", f"Proveedor '{nombre}' agregado correctamente")
    
    def actualizar_proveedor(self):
        """"""
        nombre = self.entry_nombre_proveedor.get().strip()
        
        if not nombre or nombre not in self.proveedores:
            messagebox.showwarning("Advertencia", "Seleccione un proveedor de la lista")
            return
        
        categoria = self.combo_categoria_proveedor.get()
        if not categoria:
            messagebox.showwarning("Advertencia", "La categoría es obligatoria")
            return
        
        self.proveedores[nombre] = {
            'categoria': categoria,
            'telefono': self.entry_telefono_proveedor.get().strip(),
            'email': self.entry_email_proveedor.get().strip(),
            'direccion': self.entry_direccion_proveedor.get().strip(),
            'notas': self.entry_notas_proveedor.get().strip()
        }
        
        self.guardar_datos()
        self.actualizar_tabla_proveedores()
        messagebox.showinfo("Éxito", f"Proveedor '{nombre}' actualizado correctamente")
    
    def eliminar_proveedor(self):
        """"""
        nombre = self.entry_nombre_proveedor.get().strip()
        
        if not nombre or nombre not in self.proveedores:
            messagebox.showwarning("Advertencia", "Seleccione un proveedor de la lista")
            return
        
        if messagebox.askyesno("Confirmar", f"¿Está seguro de eliminar al proveedor '{nombre}'?"):
            del self.proveedores[nombre]
            self.guardar_datos()
            self.actualizar_tabla_proveedores()
            self.limpiar_campos_proveedor()
            messagebox.showinfo("Éxito", "Proveedor eliminado correctamente")
    
    def limpiar_campos_proveedor(self):
        """"""
        self.entry_nombre_proveedor.delete(0, tk.END)
        self.combo_categoria_proveedor.set('')
        self.entry_telefono_proveedor.delete(0, tk.END)
        self.entry_email_proveedor.delete(0, tk.END)
        self.entry_direccion_proveedor.delete(0, tk.END)
        self.entry_notas_proveedor.delete(0, tk.END)
    
    def seleccionar_proveedor(self, event):
        """"""
        seleccion = self.tree_proveedores.selection()
        if seleccion:
            item = self.tree_proveedores.item(seleccion[0])
            valores = item['values']
            
            self.limpiar_campos_proveedor()
            self.entry_nombre_proveedor.insert(0, valores[0])
            self.combo_categoria_proveedor.set(valores[1])
            self.entry_telefono_proveedor.insert(0, valores[2])
            self.entry_email_proveedor.insert(0, valores[3])
            self.entry_direccion_proveedor.insert(0, valores[4])
            self.entry_notas_proveedor.insert(0, valores[5])
    
    def buscar_proveedor(self):
        """"""
        termino = self.entry_buscar_proveedor.get().strip().lower()
        
        for item in self.tree_proveedores.get_children():
            self.tree_proveedores.delete(item)
        
        for nombre, datos in self.proveedores.items():
            if termino in nombre.lower():
                self.tree_proveedores.insert('', 'end', values=(
                    nombre,
                    datos['categoria'],
                    datos['telefono'],
                    datos['email'],
                    datos['direccion'],
                    datos['notas']
                ))
    
    def filtrar_proveedores(self, event=None):
        """"""
        categoria_filtro = self.combo_filtro_categoria.get()
        
        for item in self.tree_proveedores.get_children():
            self.tree_proveedores.delete(item)
        
        for nombre, datos in self.proveedores.items():
            if categoria_filtro == "Todas" or datos['categoria'] == categoria_filtro:
                self.tree_proveedores.insert('', 'end', values=(
                    nombre,
                    datos['categoria'],
                    datos['telefono'],
                    datos['email'],
                    datos['direccion'],
                    datos['notas']
                ))
    
    def actualizar_tabla_proveedores(self):
        """"""
        for item in self.tree_proveedores.get_children():
            self.tree_proveedores.delete(item)
        
        for nombre, datos in sorted(self.proveedores.items()):
            self.tree_proveedores.insert('', 'end', values=(
                nombre,
                datos['categoria'],
                datos['telefono'],
                datos['email'],
                datos['direccion'],
                datos['notas']
            ))
    

    def crear_tab_registro(self):
        """"""
        

        frame_superior = ttk.LabelFrame(self.tab_registro, text=" Registrar Nuevo Gasto", 
                                        padding=15)
        frame_superior.pack(fill='x', padx=10, pady=10)
        

        fila1 = tk.Frame(frame_superior, bg='white')
        fila1.pack(fill='x', pady=5)
        
        tk.Label(fila1, text="Fecha:", bg='white').pack(side='left', padx=5)
        self.entry_fecha = ttk.Entry(fila1, width=12)
        self.entry_fecha.pack(side='left', padx=5)
        self.entry_fecha.insert(0, datetime.now().strftime('%Y-%m-%d'))
        
        tk.Label(fila1, text="Categoría:", bg='white').pack(side='left', padx=15)
        self.combo_categoria = ttk.Combobox(fila1, 
                                            values=list(self.categorias_agricolas.keys()),
                                            state='readonly', width=25)
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
        self.combo_proveedor = ttk.Combobox(fila2, values=list(self.proveedores.keys()),
                                            width=25)
        self.combo_proveedor.pack(side='left', padx=5)
        
        tk.Label(fila2, text="Descripción:", bg='white').pack(side='left', padx=15)
        self.entry_descripcion = ttk.Entry(fila2, width=35)
        self.entry_descripcion.pack(side='left', padx=5)
        

        self.frame_advertencia = tk.Frame(frame_superior, bg='#ffebee', relief='ridge', bd=2)
        self.label_advertencia = tk.Label(self.frame_advertencia, text="", 
                                         font=('Arial', 10, 'bold'), 
                                         bg='#ffebee', fg='#c62828')
        self.label_advertencia.pack(pady=5, padx=10)
        

        frame_botones = tk.Frame(frame_superior, bg='white')
        frame_botones.pack(fill='x', pady=10)
        
        ttk.Button(frame_botones, text=" Registrar Gasto", 
                  command=self.registrar_gasto).pack(side='left', padx=5)
        ttk.Button(frame_botones, text=" Limpiar", 
                  command=self.limpiar_campos_gasto).pack(side='left', padx=5)
        ttk.Button(frame_botones, text=" Eliminar Seleccionado", 
                  command=self.eliminar_gasto).pack(side='left', padx=5)
        

        frame_tabla = ttk.LabelFrame(self.tab_registro, text=" Gastos Registrados", 
                                     padding=10)
        frame_tabla.pack(fill='both', expand=True, padx=10, pady=10)
        
        scroll_y = ttk.Scrollbar(frame_tabla, orient='vertical')
        scroll_x = ttk.Scrollbar(frame_tabla, orient='horizontal')
        
        self.tree_gastos = ttk.Treeview(frame_tabla,
                                        columns=('fecha', 'categoria', 'subcategoria', 
                                                'monto', 'proveedor', 'descripcion'),
                                        show='headings',
                                        yscrollcommand=scroll_y.set,
                                        xscrollcommand=scroll_x.set)
        
        scroll_y.config(command=self.tree_gastos.yview)
        scroll_x.config(command=self.tree_gastos.xview)
        
        self.tree_gastos.heading('fecha', text='Fecha')
        self.tree_gastos.heading('categoria', text='Categoría')
        self.tree_gastos.heading('subcategoria', text='Subcategoría')
        self.tree_gastos.heading('monto', text='Monto')
        self.tree_gastos.heading('proveedor', text='Proveedor')
        self.tree_gastos.heading('descripcion', text='Descripción')
        
        self.tree_gastos.column('fecha', width=100)
        self.tree_gastos.column('categoria', width=180)
        self.tree_gastos.column('subcategoria', width=150)
        self.tree_gastos.column('monto', width=120)
        self.tree_gastos.column('proveedor', width=180)
        self.tree_gastos.column('descripcion', width=250)
        
        self.tree_gastos.grid(row=0, column=0, sticky='nsew')
        scroll_y.grid(row=0, column=1, sticky='ns')
        scroll_x.grid(row=1, column=0, sticky='ew')
        
        frame_tabla.grid_rowconfigure(0, weight=1)
        frame_tabla.grid_columnconfigure(0, weight=1)
        
        self.actualizar_tabla_gastos()
    
    def actualizar_subcategorias(self, event=None):
        """"""
        categoria = self.combo_categoria.get()
        if categoria in self.categorias_agricolas:
            self.combo_subcategoria['values'] = self.categorias_agricolas[categoria]
            self.combo_subcategoria.set('')
            

            proveedores_filtrados = [nombre for nombre, datos in self.proveedores.items()
                                    if datos['categoria'] == categoria]
            self.combo_proveedor['values'] = proveedores_filtrados
    
    def registrar_gasto(self):
        """"""
        try:
            fecha = self.entry_fecha.get()
            categoria = self.combo_categoria.get()
            subcategoria = self.combo_subcategoria.get()
            monto = float(self.entry_monto.get())
            proveedor = self.combo_proveedor.get()
            descripcion = self.entry_descripcion.get()
            
            if not all([fecha, categoria, subcategoria, monto]):
                messagebox.showwarning("Advertencia", "Complete todos los campos obligatorios")
                return
            

            fecha_obj = datetime.strptime(fecha, '%Y-%m-%d')
            mes = self.meses[fecha_obj.month - 1]
            

            if mes in self.presupuesto_mensual_por_mes:
                presupuesto_categoria = self.presupuesto_mensual_por_mes[mes].get(categoria, 0)
                

                gastos_categoria_mes = sum(
                    t['monto'] for t in self.transacciones
                    if t['categoria'] == categoria and 
                    datetime.strptime(t['fecha'], '%Y-%m-%d').month == fecha_obj.month and
                    datetime.strptime(t['fecha'], '%Y-%m-%d').year == fecha_obj.year
                )
                
                disponible = presupuesto_categoria - gastos_categoria_mes
                

                if monto > disponible:
                    mensaje = f" ADVERTENCIA: Presupuesto insuficiente\n\n"
                    mensaje += f"Categoría: {categoria}\n"
                    mensaje += f"Mes: {mes}\n"
                    mensaje += f"Presupuesto: ${presupuesto_categoria:,.2f}\n"
                    mensaje += f"Ya gastado: ${gastos_categoria_mes:,.2f}\n"
                    mensaje += f"Disponible: ${disponible:,.2f}\n"
                    mensaje += f"Gasto a registrar: ${monto:,.2f}\n"
                    mensaje += f"Excedente: ${monto - disponible:,.2f}\n\n"
                    mensaje += "¿Desea modificar el presupuesto de esta categoría?"
                    
                    respuesta = messagebox.askyesnocancel("Presupuesto Insuficiente", mensaje)
                    
                    if respuesta is None:
                        return
                    elif respuesta:
                        nuevo_presupuesto = simpledialog.askfloat(
                            "Modificar Presupuesto",
                            f"Ingrese el nuevo presupuesto para '{categoria}' en {mes}:",
                            initialvalue=presupuesto_categoria + (monto - disponible),
                            minvalue=gastos_categoria_mes + monto
                        )
                        
                        if nuevo_presupuesto:
                            self.presupuesto_mensual_por_mes[mes][categoria] = nuevo_presupuesto
                            

                            if mes not in self.presupuesto_modificado:
                                self.presupuesto_modificado[mes] = {}
                            self.presupuesto_modificado[mes][categoria] = True
                            
                            messagebox.showinfo("Presupuesto Modificado",
                                f"Presupuesto actualizado a ${nuevo_presupuesto:,.2f}\n" +
                                "El gasto será registrado.")
                        else:
                            return

            

            transaccion = {
                'fecha': fecha,
                'categoria': categoria,
                'subcategoria': subcategoria,
                'monto': monto,
                'proveedor': proveedor,
                'descripcion': descripcion
            }
            
            self.transacciones.append(transaccion)
            self.guardar_datos()
            self.actualizar_tabla_gastos()
            self.limpiar_campos_gasto()
            
            messagebox.showinfo("Éxito", "Gasto registrado correctamente")
            
        except ValueError:
            messagebox.showerror("Error", "El monto debe ser un número válido")
        except Exception as e:
            messagebox.showerror("Error", f"Error al registrar gasto: {str(e)}")
    
    def limpiar_campos_gasto(self):
        """"""
        self.entry_fecha.delete(0, tk.END)
        self.entry_fecha.insert(0, datetime.now().strftime('%Y-%m-%d'))
        self.combo_categoria.set('')
        self.combo_subcategoria.set('')
        self.entry_monto.delete(0, tk.END)
        self.combo_proveedor.set('')
        self.entry_descripcion.delete(0, tk.END)
        self.frame_advertencia.pack_forget()
    
    def eliminar_gasto(self):
        """"""
        seleccion = self.tree_gastos.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un gasto para eliminar")
            return
        
        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este gasto?"):
            item = self.tree_gastos.item(seleccion[0])
            valores = item['values']
            

            for i, t in enumerate(self.transacciones):
                if (t['fecha'] == valores[0] and 
                    t['categoria'] == valores[1] and
                    f"${t['monto']:,.2f}" == valores[3]):
                    del self.transacciones[i]
                    break
            
            self.guardar_datos()
            self.actualizar_tabla_gastos()
            messagebox.showinfo("Éxito", "Gasto eliminado correctamente")
    
    def actualizar_tabla_gastos(self):
        """"""
        for item in self.tree_gastos.get_children():
            self.tree_gastos.delete(item)
        
        for t in sorted(self.transacciones, key=lambda x: x['fecha'], reverse=True):
            self.tree_gastos.insert('', 'end', values=(
                t['fecha'],
                t['categoria'],
                t.get('subcategoria', ''),
                f"${t['monto']:,.2f}",
                t.get('proveedor', ''),
                t.get('descripcion', '')
            ))
    

    def crear_tab_control(self):
        """"""
        

        frame_seleccion = ttk.Frame(self.tab_control)
        frame_seleccion.pack(fill='x', padx=10, pady=10)
        
        tk.Label(frame_seleccion, text="Seleccionar Mes:", 
                font=('Arial', 12, 'bold')).pack(side='left', padx=5)
        
        self.combo_mes_control = ttk.Combobox(frame_seleccion, values=self.meses, 
                                             state='readonly', width=15, font=('Arial', 11))
        self.combo_mes_control.pack(side='left', padx=5)
        self.combo_mes_control.current(datetime.now().month - 1)
        
        ttk.Button(frame_seleccion, text=" Actualizar Datos", 
                  command=self.actualizar_control_mensual).pack(side='left', padx=15)
        

        frame_resumen = ttk.LabelFrame(self.tab_control, text=" Resumen del Mes", 
                                       padding=15)
        frame_resumen.pack(fill='x', padx=10, pady=10)
        

        frame_cards = tk.Frame(frame_resumen, bg='white')
        frame_cards.pack(fill='x', pady=10)
        

        card1 = tk.Frame(frame_cards, bg='#4CAF50', relief='raised', bd=3)
        card1.pack(side='left', fill='both', expand=True, padx=10)
        tk.Label(card1, text=" PRESUPUESTADO", 
                font=('Arial', 11, 'bold'), bg='#4CAF50', fg='white').pack(pady=8)
        self.label_presupuestado_mes = tk.Label(card1, text="$0.00", 
                                               font=('Arial', 18, 'bold'), 
                                               bg='#4CAF50', fg='white')
        self.label_presupuestado_mes.pack(pady=8)
        

        card2 = tk.Frame(frame_cards, bg='#FF9800', relief='raised', bd=3)
        card2.pack(side='left', fill='both', expand=True, padx=10)
        tk.Label(card2, text=" GASTADO", 
                font=('Arial', 11, 'bold'), bg='#FF9800', fg='white').pack(pady=8)
        self.label_gastado_mes = tk.Label(card2, text="$0.00", 
                                         font=('Arial', 18, 'bold'), 
                                         bg='#FF9800', fg='white')
        self.label_gastado_mes.pack(pady=8)
        

        card3 = tk.Frame(frame_cards, bg='#2196F3', relief='raised', bd=3)
        card3.pack(side='left', fill='both', expand=True, padx=10)
        tk.Label(card3, text=" DISPONIBLE", 
                font=('Arial', 11, 'bold'), bg='#2196F3', fg='white').pack(pady=8)
        self.label_disponible_mes = tk.Label(card3, text="$0.00", 
                                            font=('Arial', 18, 'bold'), 
                                            bg='#2196F3', fg='white')
        self.label_disponible_mes.pack(pady=8)
        

        frame_detalle = ttk.LabelFrame(self.tab_control, 
                                       text=" Detalle por Categoría", 
                                       padding=10)
        frame_detalle.pack(fill='both', expand=True, padx=10, pady=10)
        
        scroll_y = ttk.Scrollbar(frame_detalle, orient='vertical')
        
        self.tree_control = ttk.Treeview(frame_detalle,
                                        columns=('categoria', 'presupuesto', 'gastado', 
                                                'disponible', 'porcentaje', 'estado'),
                                        show='headings',
                                        yscrollcommand=scroll_y.set)
        
        scroll_y.config(command=self.tree_control.yview)
        
        self.tree_control.heading('categoria', text='Categoría')
        self.tree_control.heading('presupuesto', text='Presupuesto')
        self.tree_control.heading('gastado', text='Gastado')
        self.tree_control.heading('disponible', text='Disponible')
        self.tree_control.heading('porcentaje', text='% Usado')
        self.tree_control.heading('estado', text='Estado')
        
        self.tree_control.column('categoria', width=250)
        self.tree_control.column('presupuesto', width=150)
        self.tree_control.column('gastado', width=150)
        self.tree_control.column('disponible', width=150)
        self.tree_control.column('porcentaje', width=100)
        self.tree_control.column('estado', width=120)
        
        self.tree_control.pack(side='left', fill='both', expand=True)
        scroll_y.pack(side='right', fill='y')
        

        self.tree_control.tag_configure('ok', background='#c8e6c9')
        self.tree_control.tag_configure('warning', background='#fff9c4')
        self.tree_control.tag_configure('danger', background='#ffccbc')
        self.tree_control.tag_configure('modified', background='#e1bee7')
        
        self.actualizar_control_mensual()
    
    def actualizar_control_mensual(self):
        """"""
        mes_seleccionado = self.combo_mes_control.get()
        mes_numero = self.meses.index(mes_seleccionado) + 1
        año_actual = datetime.now().year
        

        for item in self.tree_control.get_children():
            self.tree_control.delete(item)
        
        total_presupuestado = 0
        total_gastado = 0
        
        if mes_seleccionado in self.presupuesto_mensual_por_mes:
            presupuesto_mes = self.presupuesto_mensual_por_mes[mes_seleccionado]
            
            for categoria, presupuesto in presupuesto_mes.items():

                gastos_categoria = sum(
                    t['monto'] for t in self.transacciones
                    if t['categoria'] == categoria and
                    datetime.strptime(t['fecha'], '%Y-%m-%d').month == mes_numero and
                    datetime.strptime(t['fecha'], '%Y-%m-%d').year == año_actual
                )
                
                disponible = presupuesto - gastos_categoria
                porcentaje = (gastos_categoria / presupuesto * 100) if presupuesto > 0 else 0
                

                if porcentaje > 100:
                    estado = " EXCEDIDO"
                    tag = 'danger'
                elif porcentaje > 90:
                    estado = " CRÍTICO"
                    tag = 'warning'
                elif porcentaje > 75:
                    estado = " ALERTA"
                    tag = 'warning'
                else:
                    estado = " OK"
                    tag = 'ok'
                

                if (mes_seleccionado in self.presupuesto_modificado and
                    categoria in self.presupuesto_modificado[mes_seleccionado] and
                    self.presupuesto_modificado[mes_seleccionado][categoria]):
                    estado += " (MOD)"
                    tag = 'modified'
                
                self.tree_control.insert('', 'end', values=(
                    categoria,
                    f"${presupuesto:,.2f}",
                    f"${gastos_categoria:,.2f}",
                    f"${disponible:,.2f}",
                    f"{porcentaje:.1f}%",
                    estado
                ), tags=(tag,))
                
                total_presupuestado += presupuesto
                total_gastado += gastos_categoria
        

        self.label_presupuestado_mes.config(text=f"${total_presupuestado:,.2f}")
        self.label_gastado_mes.config(text=f"${total_gastado:,.2f}")
        
        disponible_total = total_presupuestado - total_gastado
        self.label_disponible_mes.config(text=f"${disponible_total:,.2f}")
        

        if disponible_total < 0:
            self.label_disponible_mes.config(text=f"${abs(disponible_total):,.2f} EXCEDIDO")
            card3 = self.label_disponible_mes.master
            card3.config(bg='#f44336')
    

    def crear_tab_sobrantes(self):
        """"""
        

        frame_instrucciones = ttk.LabelFrame(self.tab_sobrantes, 
                                            text=" Información", padding=10)
        frame_instrucciones.pack(fill='x', padx=10, pady=10)
        
        tk.Label(frame_instrucciones, 
                text="Aquí puede transferir sobrantes de presupuesto entre meses o entre categorías.",
                font=('Arial', 10), wraplength=1300, justify='left').pack()
        

        frame_sobrantes = ttk.LabelFrame(self.tab_sobrantes, 
                                        text=" Sobrantes Disponibles", 
                                        padding=15)
        frame_sobrantes.pack(fill='x', padx=10, pady=10)
        

        frame_mes_origen = tk.Frame(frame_sobrantes)
        frame_mes_origen.pack(fill='x', pady=5)
        
        tk.Label(frame_mes_origen, text="Mes de Origen:", 
                font=('Arial', 11, 'bold')).pack(side='left', padx=5)
        self.combo_mes_sobrante_origen = ttk.Combobox(frame_mes_origen, 
                                                      values=self.meses,
                                                      state='readonly', width=15)
        self.combo_mes_sobrante_origen.pack(side='left', padx=5)
        self.combo_mes_sobrante_origen.current(datetime.now().month - 1)
        self.combo_mes_sobrante_origen.bind('<<ComboboxSelected>>', 
                                           self.actualizar_sobrantes_disponibles)
        
        ttk.Button(frame_mes_origen, text=" Calcular Sobrantes", 
                  command=self.calcular_sobrantes).pack(side='left', padx=15)
        

        frame_tabla_sobrantes = ttk.Frame(frame_sobrantes)
        frame_tabla_sobrantes.pack(fill='both', expand=True, pady=10)
        
        scroll_sobrantes = ttk.Scrollbar(frame_tabla_sobrantes, orient='vertical')
        
        self.tree_sobrantes = ttk.Treeview(frame_tabla_sobrantes,
                                          columns=('categoria', 'presupuesto', 'gastado', 
                                                  'sobrante'),
                                          show='headings',
                                          yscrollcommand=scroll_sobrantes.set,
                                          height=8)
        
        scroll_sobrantes.config(command=self.tree_sobrantes.yview)
        
        self.tree_sobrantes.heading('categoria', text='Categoría')
        self.tree_sobrantes.heading('presupuesto', text='Presupuesto')
        self.tree_sobrantes.heading('gastado', text='Gastado')
        self.tree_sobrantes.heading('sobrante', text='Sobrante')
        
        self.tree_sobrantes.column('categoria', width=300)
        self.tree_sobrantes.column('presupuesto', width=150)
        self.tree_sobrantes.column('gastado', width=150)
        self.tree_sobrantes.column('sobrante', width=150)
        
        self.tree_sobrantes.pack(side='left', fill='both', expand=True)
        scroll_sobrantes.pack(side='right', fill='y')
        

        frame_transferencia = ttk.LabelFrame(self.tab_sobrantes, 
                                            text=" Transferir Sobrante", 
                                            padding=15)
        frame_transferencia.pack(fill='x', padx=10, pady=10)
        

        tk.Label(frame_transferencia, text="Tipo de Transferencia:", 
                font=('Arial', 11, 'bold')).grid(row=0, column=0, sticky='w', padx=5, pady=5)
        
        self.tipo_transferencia = tk.StringVar(value="mes")
        tk.Radiobutton(frame_transferencia, text="A otro mes", 
                      variable=self.tipo_transferencia, value="mes").grid(
                          row=0, column=1, sticky='w', padx=5)
        tk.Radiobutton(frame_transferencia, text="A otra categoría (mismo mes)", 
                      variable=self.tipo_transferencia, value="categoria").grid(
                          row=0, column=2, sticky='w', padx=5)
        
        tk.Label(frame_transferencia, text="Categoría Origen:").grid(
            row=1, column=0, sticky='w', padx=5, pady=5)
        self.combo_categoria_origen_sobrante = ttk.Combobox(
            frame_transferencia, 
            values=list(self.categorias_agricolas.keys()),
            state='readonly', width=25)
        self.combo_categoria_origen_sobrante.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(frame_transferencia, text="Monto a Transferir:").grid(
            row=1, column=2, sticky='w', padx=5, pady=5)
        self.entry_monto_transferir = ttk.Entry(frame_transferencia, width=15)
        self.entry_monto_transferir.grid(row=1, column=3, padx=5, pady=5)
        
        tk.Label(frame_transferencia, text="Destino (Mes):").grid(
            row=2, column=0, sticky='w', padx=5, pady=5)
        self.combo_mes_destino = ttk.Combobox(frame_transferencia, 
                                              values=self.meses,
                                              state='readonly', width=15)
        self.combo_mes_destino.grid(row=2, column=1, padx=5, pady=5)
        
        tk.Label(frame_transferencia, text="Destino (Categoría):").grid(
            row=2, column=2, sticky='w', padx=5, pady=5)
        self.combo_categoria_destino = ttk.Combobox(
            frame_transferencia,
            values=list(self.categorias_agricolas.keys()),
            state='readonly', width=25)
        self.combo_categoria_destino.grid(row=2, column=3, padx=5, pady=5)
        
        ttk.Button(frame_transferencia, text="Realizar Transferencia", 
                  command=self.realizar_transferencia).grid(
                      row=3, column=0, columnspan=4, pady=15)
        
        frame_historial = ttk.LabelFrame(self.tab_sobrantes, 
                                        text="Historial de Transferencias", 
                                        padding=10)
        frame_historial.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.text_historial = scrolledtext.ScrolledText(frame_historial, 
                                                        height=8, 
                                                        font=('Courier', 9))
        self.text_historial.pack(fill='both', expand=True)
        
        self.actualizar_sobrantes_disponibles()
    
    def calcular_sobrantes(self):
        """"""
        self.actualizar_sobrantes_disponibles()
        messagebox.showinfo("Sobrantes Calculados", "Los sobrantes han sido actualizados")
    
    def actualizar_sobrantes_disponibles(self, event=None):
        """"""
        mes_seleccionado = self.combo_mes_sobrante_origen.get()
        mes_numero = self.meses.index(mes_seleccionado) + 1
        año_actual = datetime.now().year

        for item in self.tree_sobrantes.get_children():
            self.tree_sobrantes.delete(item)
        
        if mes_seleccionado in self.presupuesto_mensual_por_mes:
            presupuesto_mes = self.presupuesto_mensual_por_mes[mes_seleccionado]
            
            for categoria, presupuesto in presupuesto_mes.items():
                gastos = sum(
                    t['monto'] for t in self.transacciones
                    if t['categoria'] == categoria and
                    datetime.strptime(t['fecha'], '%Y-%m-%d').month == mes_numero and
                    datetime.strptime(t['fecha'], '%Y-%m-%d').year == año_actual
                )
                
                sobrante = presupuesto - gastos
                
                if sobrante > 0:
                    self.tree_sobrantes.insert('', 'end', values=(
                        categoria,
                        f"${presupuesto:,.2f}",
                        f"${gastos:,.2f}",
                        f"${sobrante:,.2f}"
                    ))
    
    def realizar_transferencia(self):
        """"""
        try:
            mes_origen = self.combo_mes_sobrante_origen.get()
            categoria_origen = self.combo_categoria_origen_sobrante.get()
            monto = float(self.entry_monto_transferir.get())
            tipo = self.tipo_transferencia.get()
            
            if not all([mes_origen, categoria_origen, monto]):
                messagebox.showwarning("Advertencia", "Complete todos los campos")
                return
            
            mes_numero = self.meses.index(mes_origen) + 1
            año_actual = datetime.now().year
            
            presupuesto = self.presupuesto_mensual_por_mes[mes_origen][categoria_origen]
            gastos = sum(
                t['monto'] for t in self.transacciones
                if t['categoria'] == categoria_origen and
                datetime.strptime(t['fecha'], '%Y-%m-%d').month == mes_numero and
                datetime.strptime(t['fecha'], '%Y-%m-%d').year == año_actual
            )
            
            sobrante_disponible = presupuesto - gastos
            
            if monto > sobrante_disponible:
                messagebox.showerror("Error", 
                    f"No hay suficiente sobrante. Disponible: ${sobrante_disponible:,.2f}")
                return
            
            if tipo == "mes":
                mes_destino = self.combo_mes_destino.get()
                categoria_destino = categoria_origen
                
                if not mes_destino:
                    messagebox.showwarning("Advertencia", "Seleccione el mes destino")
                    return
                
                self.presupuesto_mensual_por_mes[mes_origen][categoria_origen] -= monto
                
                if mes_destino not in self.presupuesto_mensual_por_mes:
                    self.presupuesto_mensual_por_mes[mes_destino] = {}
                
                if categoria_destino not in self.presupuesto_mensual_por_mes[mes_destino]:
                    self.presupuesto_mensual_por_mes[mes_destino][categoria_destino] = 0
                
                self.presupuesto_mensual_por_mes[mes_destino][categoria_destino] += monto
                
                if mes_destino not in self.presupuesto_modificado:
                    self.presupuesto_modificado[mes_destino] = {}
                self.presupuesto_modificado[mes_destino][categoria_destino] = True
                
                mensaje = f"Transferencia realizada:\n"
                mensaje += f"${monto:,.2f} de {categoria_origen}\n"
                mensaje += f"De: {mes_origen} → A: {mes_destino}"
                
            else:  
                categoria_destino = self.combo_categoria_destino.get()
                
                if not categoria_destino:
                    messagebox.showwarning("Advertencia", "Seleccione la categoría destino")
                    return
                
                self.presupuesto_mensual_por_mes[mes_origen][categoria_origen] -= monto
                
                if categoria_destino not in self.presupuesto_mensual_por_mes[mes_origen]:
                    self.presupuesto_mensual_por_mes[mes_origen][categoria_destino] = 0
                
                self.presupuesto_mensual_por_mes[mes_origen][categoria_destino] += monto
                
                if mes_origen not in self.presupuesto_modificado:
                    self.presupuesto_modificado[mes_origen] = {}
                self.presupuesto_modificado[mes_origen][categoria_destino] = True
                
                mensaje = f"Transferencia realizada en {mes_origen}:\n"
                mensaje += f"${monto:,.2f}\n"
                mensaje += f"De: {categoria_origen} → A: {categoria_destino}"
            
            self.guardar_datos()
            
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            historial = f"[{timestamp}] {mensaje}\n"
            self.text_historial.insert('1.0', historial)
            
            self.actualizar_sobrantes_disponibles()
            
            messagebox.showinfo("Éxito", mensaje)
            
            self.entry_monto_transferir.delete(0, tk.END)
            self.combo_categoria_origen_sobrante.set('')
            self.combo_mes_destino.set('')
            self.combo_categoria_destino.set('')
            
        except ValueError:
            messagebox.showerror("Error", "El monto debe ser un número válido")
        except Exception as e:
            messagebox.showerror("Error", f"Error en la transferencia: {str(e)}")
    
    def crear_tab_graficos(self):
        """"""
        
        frame_controles = ttk.Frame(self.tab_graficos)
        frame_controles.pack(fill='x', padx=10, pady=10)
        
        tk.Label(frame_controles, text="Seleccionar Mes:", 
                font=('Arial', 11, 'bold')).pack(side='left', padx=5)
        
        self.combo_mes_grafico = ttk.Combobox(frame_controles, values=self.meses, 
                                             state='readonly', width=15)
        self.combo_mes_grafico.pack(side='left', padx=5)
        self.combo_mes_grafico.current(datetime.now().month - 1)
        
        ttk.Button(frame_controles, text=" Generar Gráficos", 
                  command=self.generar_graficos).pack(side='left', padx=15)
        
        self.frame_graficos = ttk.Frame(self.tab_graficos)
        self.frame_graficos.pack(fill='both', expand=True, padx=10, pady=10)
    
    def generar_graficos(self):
        """"""

        for widget in self.frame_graficos.winfo_children():
            widget.destroy()
        
        mes_seleccionado = self.combo_mes_grafico.get()
        mes_numero = self.meses.index(mes_seleccionado) + 1
        año_actual = datetime.now().year
        
        if mes_seleccionado not in self.presupuesto_mensual_por_mes:
            messagebox.showinfo("Sin Datos", 
                "No hay presupuesto configurado para este mes")
            return
        
        fig = Figure(figsize=(14, 10))
        
        ax1 = fig.add_subplot(2, 2, 1)
        categorias = []
        presupuestos = []
        gastos = []
        
        for categoria, presupuesto in self.presupuesto_mensual_por_mes[mes_seleccionado].items():
            gasto = sum(
                t['monto'] for t in self.transacciones
                if t['categoria'] == categoria and
                datetime.strptime(t['fecha'], '%Y-%m-%d').month == mes_numero and
                datetime.strptime(t['fecha'], '%Y-%m-%d').year == año_actual
            )
            
            categorias.append(categoria[:15] + '...' if len(categoria) > 15 else categoria)
            presupuestos.append(presupuesto)
            gastos.append(gasto)
        
        x = range(len(categorias))
        width = 0.35
        
        ax1.bar([i - width/2 for i in x], presupuestos, width, label='Presupuesto', color='#4CAF50')
        ax1.bar([i + width/2 for i in x], gastos, width, label='Gastado', color='#FF9800')
        
        ax1.set_xlabel('Categorías')
        ax1.set_ylabel('Monto ($)')
        ax1.set_title(f'Presupuesto vs Gastado - {mes_seleccionado}')
        ax1.set_xticks(x)
        ax1.set_xticklabels(categorias, rotation=45, ha='right')
        ax1.legend()
        ax1.grid(axis='y', alpha=0.3)
        
        ax2 = fig.add_subplot(2, 2, 2)
        porcentajes = [(g/p*100 if p > 0 else 0) for g, p in zip(gastos, presupuestos)]
        colors = ['#f44336' if p > 100 else '#FF9800' if p > 90 else '#4CAF50' 
                 for p in porcentajes]
        
        ax2.barh(categorias, porcentajes, color=colors)
        ax2.set_xlabel('% Utilizado')
        ax2.set_title('Porcentaje de Uso del Presupuesto')
        ax2.axvline(x=100, color='red', linestyle='--', linewidth=2, label='Límite')
        ax2.legend()
        ax2.grid(axis='x', alpha=0.3)
        
        ax3 = fig.add_subplot(2, 2, 3)
        gastos_no_cero = [(cat, gasto) for cat, gasto in zip(categorias, gastos) if gasto > 0]
        
        if gastos_no_cero:
            labels, values = zip(*gastos_no_cero)
            ax3.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
            ax3.set_title('Distribución del Gasto por Categoría')
        else:
            ax3.text(0.5, 0.5, 'Sin gastos registrados', 
                    ha='center', va='center', transform=ax3.transAxes)
        
        ax4 = fig.add_subplot(2, 2, 4)
        
        meses_anteriores = []
        totales_gastados = []
        
        for i in range(6, 0, -1):
            mes_idx = (mes_numero - i) % 12
            if mes_idx == 0:
                mes_idx = 12
            mes_nombre = self.meses[mes_idx - 1]
            
            total = sum(
                t['monto'] for t in self.transacciones
                if datetime.strptime(t['fecha'], '%Y-%m-%d').month == mes_idx
            )
            
            meses_anteriores.append(mes_nombre[:3])
            totales_gastados.append(total)
        
        ax4.plot(meses_anteriores, totales_gastados, marker='o', linewidth=2, markersize=8)
        ax4.set_xlabel('Mes')
        ax4.set_ylabel('Total Gastado ($)')
        ax4.set_title('Tendencia de Gasto (Últimos 6 Meses)')
        ax4.grid(True, alpha=0.3)
        
        fig.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=self.frame_graficos)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
    
    def cargar_datos(self):
        """"""
 
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
                self.presupuesto_mensual_por_mes = {}
                self.presupuesto_modificado = {}
        
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
        """"""
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
        """"""
        with open(self.archivo_datos, 'w', encoding='utf-8') as f:
            json.dump(self.transacciones, f, ensure_ascii=False, indent=2)
        
        with open(self.archivo_presupuesto_mensual, 'w', encoding='utf-8') as f:
            json.dump({
                'presupuesto': self.presupuesto_mensual_por_mes,
                'modificado': self.presupuesto_modificado
            }, f, ensure_ascii=False, indent=2)
        
        with open(self.archivo_proveedores, 'w', encoding='utf-8') as f:
            json.dump(self.proveedores, f, ensure_ascii=False, indent=2)
        
        if self.presupuesto_mensual_por_mes:
            self.presupuestos_por_año[str(self.año_actual)] = dict(self.presupuesto_mensual_por_mes)
            self.guardar_presupuestos_anuales()
    
    def guardar_presupuestos_anuales(self):
        """"""
        with open(self.archivo_presupuestos_anuales, 'w', encoding='utf-8') as f:
            json.dump(self.presupuestos_por_año, f, ensure_ascii=False, indent=2)
    
    def guardar_sobrantes_anuales(self):
        """"""
        with open(self.archivo_sobrantes_anuales, 'w', encoding='utf-8') as f:
            json.dump(self.sobrantes_anuales, f, ensure_ascii=False, indent=2)
    
    def guardar_categorias_personalizadas(self):
        """"""
        with open(self.archivo_categorias_personalizadas, 'w', encoding='utf-8') as f:
            json.dump(self.categorias_personalizadas, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    root = tk.Tk()
    app = SistemaFinancieroAgricola(root)
    root.mainloop()