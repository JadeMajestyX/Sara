import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

from core import horarios_db as db

DIAS_SEMANA = [
    "Lunes",
    "Martes",
    "Miercoles",
    "Jueves",
    "Viernes",
    "Sabado"
]


class AdminPanel:

    def __init__(self):

        self.conn = db.conectar()
        db.crear_tablas(self.conn)

        self.root = tk.Tk()
        self.root.title("Admin horarios")
        self.root.geometry("1100x700")
        self.root.protocol("WM_DELETE_WINDOW", self.cerrar)

        self._catalogos = {
            "grupos": {},
            "salones": {},
            "profesores": {},
            "materias": {}
        }

        self._crear_ui()
        self._refrescar_todo()

    def _crear_ui(self):

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        self.tab_grupos = ttk.Frame(self.notebook, padding=12)
        self.tab_salones = ttk.Frame(self.notebook, padding=12)
        self.tab_profesores = ttk.Frame(self.notebook, padding=12)
        self.tab_materias = ttk.Frame(self.notebook, padding=12)
        self.tab_horarios = ttk.Frame(self.notebook, padding=12)
        self.tab_consultas = ttk.Frame(self.notebook, padding=12)

        self.notebook.add(self.tab_grupos, text="Grupos")
        self.notebook.add(self.tab_salones, text="Salones")
        self.notebook.add(self.tab_profesores, text="Profesores")
        self.notebook.add(self.tab_materias, text="Materias")
        self.notebook.add(self.tab_horarios, text="Horarios")
        self.notebook.add(self.tab_consultas, text="Consultas")

        self._crear_tab_grupos()
        self._crear_tab_salones()
        self._crear_tab_profesores()
        self._crear_tab_materias()
        self._crear_tab_horarios()
        self._crear_tab_consultas()

    def _crear_tab_grupos(self):

        form = ttk.Frame(self.tab_grupos)
        form.pack(fill="x", pady=(0, 10))

        ttk.Label(form, text="Nombre").grid(row=0, column=0, sticky="w")
        self.grupo_nombre = ttk.Entry(form, width=30)
        self.grupo_nombre.grid(row=0, column=1, padx=8)
        ttk.Button(form, text="Agregar", command=self._agregar_grupo).grid(row=0, column=2, padx=8)
        ttk.Button(form, text="Eliminar", command=self._eliminar_grupo).grid(row=0, column=3)

        self.tree_grupos = ttk.Treeview(self.tab_grupos, columns=("id", "nombre"), show="headings")
        self.tree_grupos.heading("id", text="ID")
        self.tree_grupos.heading("nombre", text="Grupo")
        self.tree_grupos.column("id", width=60, anchor="center")
        self.tree_grupos.column("nombre", width=200, anchor="w")
        self.tree_grupos.pack(fill="both", expand=True)

    def _crear_tab_salones(self):

        form = ttk.Frame(self.tab_salones)
        form.pack(fill="x", pady=(0, 10))

        ttk.Label(form, text="Nombre").grid(row=0, column=0, sticky="w")
        self.salon_nombre = ttk.Entry(form, width=30)
        self.salon_nombre.grid(row=0, column=1, padx=8)

        ttk.Label(form, text="Capacidad").grid(row=0, column=2, sticky="w")
        self.salon_capacidad = ttk.Entry(form, width=10)
        self.salon_capacidad.grid(row=0, column=3, padx=8)

        ttk.Button(form, text="Agregar", command=self._agregar_salon).grid(row=0, column=4, padx=8)
        ttk.Button(form, text="Eliminar", command=self._eliminar_salon).grid(row=0, column=5)

        self.tree_salones = ttk.Treeview(self.tab_salones, columns=("id", "nombre", "capacidad"), show="headings")
        self.tree_salones.heading("id", text="ID")
        self.tree_salones.heading("nombre", text="Salon")
        self.tree_salones.heading("capacidad", text="Capacidad")
        self.tree_salones.column("id", width=60, anchor="center")
        self.tree_salones.column("nombre", width=200, anchor="w")
        self.tree_salones.column("capacidad", width=120, anchor="center")
        self.tree_salones.pack(fill="both", expand=True)

    def _crear_tab_profesores(self):

        form = ttk.Frame(self.tab_profesores)
        form.pack(fill="x", pady=(0, 10))

        ttk.Label(form, text="Nombre").grid(row=0, column=0, sticky="w")
        self.profesor_nombre = ttk.Entry(form, width=40)
        self.profesor_nombre.grid(row=0, column=1, padx=8)
        ttk.Button(form, text="Agregar", command=self._agregar_profesor).grid(row=0, column=2, padx=8)
        ttk.Button(form, text="Eliminar", command=self._eliminar_profesor).grid(row=0, column=3)

        self.tree_profesores = ttk.Treeview(self.tab_profesores, columns=("id", "nombre"), show="headings")
        self.tree_profesores.heading("id", text="ID")
        self.tree_profesores.heading("nombre", text="Profesor")
        self.tree_profesores.column("id", width=60, anchor="center")
        self.tree_profesores.column("nombre", width=280, anchor="w")
        self.tree_profesores.pack(fill="both", expand=True)

    def _crear_tab_materias(self):

        form = ttk.Frame(self.tab_materias)
        form.pack(fill="x", pady=(0, 10))

        ttk.Label(form, text="Nombre").grid(row=0, column=0, sticky="w")
        self.materia_nombre = ttk.Entry(form, width=40)
        self.materia_nombre.grid(row=0, column=1, padx=8)
        ttk.Button(form, text="Agregar", command=self._agregar_materia).grid(row=0, column=2, padx=8)
        ttk.Button(form, text="Eliminar", command=self._eliminar_materia).grid(row=0, column=3)

        self.tree_materias = ttk.Treeview(self.tab_materias, columns=("id", "nombre"), show="headings")
        self.tree_materias.heading("id", text="ID")
        self.tree_materias.heading("nombre", text="Materia")
        self.tree_materias.column("id", width=60, anchor="center")
        self.tree_materias.column("nombre", width=280, anchor="w")
        self.tree_materias.pack(fill="both", expand=True)

    def _crear_tab_horarios(self):

        form = ttk.Frame(self.tab_horarios)
        form.pack(fill="x", pady=(0, 10))

        ttk.Label(form, text="Grupo").grid(row=0, column=0, sticky="w")
        self.horario_grupo = ttk.Combobox(form, state="readonly", width=16)
        self.horario_grupo.grid(row=0, column=1, padx=6)

        ttk.Label(form, text="Materia").grid(row=0, column=2, sticky="w")
        self.horario_materia = ttk.Combobox(form, state="readonly", width=22)
        self.horario_materia.grid(row=0, column=3, padx=6)

        ttk.Label(form, text="Profesor").grid(row=0, column=4, sticky="w")
        self.horario_profesor = ttk.Combobox(form, state="readonly", width=22)
        self.horario_profesor.grid(row=0, column=5, padx=6)

        ttk.Label(form, text="Salon").grid(row=1, column=0, sticky="w", pady=6)
        self.horario_salon = ttk.Combobox(form, state="readonly", width=16)
        self.horario_salon.grid(row=1, column=1, padx=6, pady=6)

        ttk.Label(form, text="Dia").grid(row=1, column=2, sticky="w", pady=6)
        self.horario_dia = ttk.Combobox(form, state="readonly", width=16, values=DIAS_SEMANA)
        self.horario_dia.grid(row=1, column=3, padx=6, pady=6)

        ttk.Label(form, text="Inicio (HH:MM)").grid(row=1, column=4, sticky="w", pady=6)
        self.horario_inicio = ttk.Entry(form, width=10)
        self.horario_inicio.grid(row=1, column=5, padx=6, pady=6, sticky="w")

        ttk.Label(form, text="Fin (HH:MM)").grid(row=2, column=4, sticky="w", pady=6)
        self.horario_fin = ttk.Entry(form, width=10)
        self.horario_fin.grid(row=2, column=5, padx=6, pady=6, sticky="w")

        ttk.Button(form, text="Agregar", command=self._agregar_horario).grid(row=2, column=3, padx=6, pady=6, sticky="e")
        ttk.Button(form, text="Eliminar", command=self._eliminar_horario).grid(row=2, column=2, padx=6, pady=6, sticky="w")

        self.tree_horarios = ttk.Treeview(
            self.tab_horarios,
            columns=("id", "grupo", "materia", "profesor", "salon", "dia", "inicio", "fin"),
            show="headings"
        )
        for col, texto, ancho in [
            ("id", "ID", 60),
            ("grupo", "Grupo", 90),
            ("materia", "Materia", 160),
            ("profesor", "Profesor", 160),
            ("salon", "Salon", 100),
            ("dia", "Dia", 90),
            ("inicio", "Inicio", 80),
            ("fin", "Fin", 80)
        ]:
            self.tree_horarios.heading(col, text=texto)
            self.tree_horarios.column(col, width=ancho, anchor="center")
        self.tree_horarios.pack(fill="both", expand=True)

    def _crear_tab_consultas(self):

        grupo_box = ttk.Labelframe(self.tab_consultas, text="Horarios por grupo", padding=10)
        grupo_box.pack(fill="x", pady=(0, 10))

        ttk.Label(grupo_box, text="Grupo").grid(row=0, column=0, sticky="w")
        self.consulta_grupo = ttk.Combobox(grupo_box, state="readonly", width=16)
        self.consulta_grupo.grid(row=0, column=1, padx=6)
        ttk.Button(grupo_box, text="Buscar", command=self._consultar_grupo).grid(row=0, column=2, padx=6)

        self.tree_consulta = ttk.Treeview(
            grupo_box,
            columns=("grupo", "materia", "profesor", "salon", "dia", "inicio", "fin"),
            show="headings",
            height=6
        )
        for col, texto, ancho in [
            ("grupo", "Grupo", 90),
            ("materia", "Materia", 160),
            ("profesor", "Profesor", 160),
            ("salon", "Salon", 100),
            ("dia", "Dia", 90),
            ("inicio", "Inicio", 80),
            ("fin", "Fin", 80)
        ]:
            self.tree_consulta.heading(col, text=texto)
            self.tree_consulta.column(col, width=ancho, anchor="center")
        self.tree_consulta.grid(row=1, column=0, columnspan=3, pady=10, sticky="nsew")

        libres_box = ttk.Labelframe(self.tab_consultas, text="Salones libres", padding=10)
        libres_box.pack(fill="x")

        ttk.Label(libres_box, text="Dia").grid(row=0, column=0, sticky="w")
        self.libre_dia = ttk.Combobox(libres_box, state="readonly", width=16, values=DIAS_SEMANA)
        self.libre_dia.grid(row=0, column=1, padx=6)

        ttk.Label(libres_box, text="Hora (HH:MM)").grid(row=0, column=2, sticky="w")
        self.libre_hora = ttk.Entry(libres_box, width=10)
        self.libre_hora.grid(row=0, column=3, padx=6)

        ttk.Button(libres_box, text="Buscar", command=self._consultar_libres).grid(row=0, column=4, padx=6)

        self.list_libres = tk.Listbox(libres_box, height=6)
        self.list_libres.grid(row=1, column=0, columnspan=5, sticky="nsew", pady=10)

    def _parse_hora(self, valor):

        try:
            return datetime.strptime(valor.strip(), "%H:%M").time()
        except ValueError:
            return None

    def _refrescar_catalogos(self):

        self._catalogos["grupos"] = {nombre: gid for gid, nombre in db.listar_grupos(self.conn)}
        self._catalogos["salones"] = {nombre: sid for sid, nombre, _ in db.listar_salones(self.conn)}
        self._catalogos["profesores"] = {nombre: pid for pid, nombre in db.listar_profesores(self.conn)}
        self._catalogos["materias"] = {nombre: mid for mid, nombre in db.listar_materias(self.conn)}

        self.horario_grupo["values"] = list(self._catalogos["grupos"].keys())
        self.horario_salon["values"] = list(self._catalogos["salones"].keys())
        self.horario_profesor["values"] = list(self._catalogos["profesores"].keys())
        self.horario_materia["values"] = list(self._catalogos["materias"].keys())
        self.consulta_grupo["values"] = list(self._catalogos["grupos"].keys())

    def _refrescar_todo(self):

        self._refrescar_catalogos()
        self._cargar_grupos()
        self._cargar_salones()
        self._cargar_profesores()
        self._cargar_materias()
        self._cargar_horarios()

    def _limpiar_tree(self, tree):

        for item in tree.get_children():
            tree.delete(item)

    def _cargar_grupos(self):

        self._limpiar_tree(self.tree_grupos)
        for gid, nombre in db.listar_grupos(self.conn):
            self.tree_grupos.insert("", "end", values=(gid, nombre))

    def _cargar_salones(self):

        self._limpiar_tree(self.tree_salones)
        for sid, nombre, capacidad in db.listar_salones(self.conn):
            self.tree_salones.insert("", "end", values=(sid, nombre, capacidad))

    def _cargar_profesores(self):

        self._limpiar_tree(self.tree_profesores)
        for pid, nombre in db.listar_profesores(self.conn):
            self.tree_profesores.insert("", "end", values=(pid, nombre))

    def _cargar_materias(self):

        self._limpiar_tree(self.tree_materias)
        for mid, nombre in db.listar_materias(self.conn):
            self.tree_materias.insert("", "end", values=(mid, nombre))

    def _cargar_horarios(self):

        self._limpiar_tree(self.tree_horarios)
        for fila in db.listar_horarios(self.conn):
            self.tree_horarios.insert("", "end", values=fila)

    def _seleccion_id(self, tree):

        seleccion = tree.selection()
        if not seleccion:
            return None
        valores = tree.item(seleccion[0], "values")
        if not valores:
            return None
        return valores[0]

    def _agregar_grupo(self):

        nombre = self.grupo_nombre.get().strip()
        if not nombre:
            messagebox.showerror("Error", "Ingresa el nombre del grupo")
            return
        try:
            db.crear_grupo(self.conn, nombre)
        except Exception as exc:
            messagebox.showerror("Error", str(exc))
            return
        self.grupo_nombre.delete(0, "end")
        self._refrescar_todo()

    def _eliminar_grupo(self):

        grupo_id = self._seleccion_id(self.tree_grupos)
        if not grupo_id:
            messagebox.showerror("Error", "Selecciona un grupo")
            return
        try:
            db.eliminar_grupo(self.conn, grupo_id)
        except Exception as exc:
            messagebox.showerror("Error", str(exc))
            return
        self._refrescar_todo()

    def _agregar_salon(self):

        nombre = self.salon_nombre.get().strip()
        capacidad_txt = self.salon_capacidad.get().strip()
        if not nombre:
            messagebox.showerror("Error", "Ingresa el nombre del salon")
            return
        capacidad = None
        if capacidad_txt:
            if not capacidad_txt.isdigit():
                messagebox.showerror("Error", "Capacidad debe ser un numero")
                return
            capacidad = int(capacidad_txt)
        try:
            db.crear_salon(self.conn, nombre, capacidad)
        except Exception as exc:
            messagebox.showerror("Error", str(exc))
            return
        self.salon_nombre.delete(0, "end")
        self.salon_capacidad.delete(0, "end")
        self._refrescar_todo()

    def _eliminar_salon(self):

        salon_id = self._seleccion_id(self.tree_salones)
        if not salon_id:
            messagebox.showerror("Error", "Selecciona un salon")
            return
        try:
            db.eliminar_salon(self.conn, salon_id)
        except Exception as exc:
            messagebox.showerror("Error", str(exc))
            return
        self._refrescar_todo()

    def _agregar_profesor(self):

        nombre = self.profesor_nombre.get().strip()
        if not nombre:
            messagebox.showerror("Error", "Ingresa el nombre del profesor")
            return
        try:
            db.crear_profesor(self.conn, nombre)
        except Exception as exc:
            messagebox.showerror("Error", str(exc))
            return
        self.profesor_nombre.delete(0, "end")
        self._refrescar_todo()

    def _eliminar_profesor(self):

        profesor_id = self._seleccion_id(self.tree_profesores)
        if not profesor_id:
            messagebox.showerror("Error", "Selecciona un profesor")
            return
        try:
            db.eliminar_profesor(self.conn, profesor_id)
        except Exception as exc:
            messagebox.showerror("Error", str(exc))
            return
        self._refrescar_todo()

    def _agregar_materia(self):

        nombre = self.materia_nombre.get().strip()
        if not nombre:
            messagebox.showerror("Error", "Ingresa el nombre de la materia")
            return
        try:
            db.crear_materia(self.conn, nombre)
        except Exception as exc:
            messagebox.showerror("Error", str(exc))
            return
        self.materia_nombre.delete(0, "end")
        self._refrescar_todo()

    def _eliminar_materia(self):

        materia_id = self._seleccion_id(self.tree_materias)
        if not materia_id:
            messagebox.showerror("Error", "Selecciona una materia")
            return
        try:
            db.eliminar_materia(self.conn, materia_id)
        except Exception as exc:
            messagebox.showerror("Error", str(exc))
            return
        self._refrescar_todo()

    def _agregar_horario(self):

        grupo = self.horario_grupo.get().strip()
        materia = self.horario_materia.get().strip()
        profesor = self.horario_profesor.get().strip()
        salon = self.horario_salon.get().strip()
        dia = self.horario_dia.get().strip()
        inicio = self._parse_hora(self.horario_inicio.get())
        fin = self._parse_hora(self.horario_fin.get())

        if not all([grupo, materia, profesor, salon, dia]):
            messagebox.showerror("Error", "Completa todos los campos")
            return
        if not inicio or not fin:
            messagebox.showerror("Error", "Hora invalida, usa HH:MM")
            return
        if fin <= inicio:
            messagebox.showerror("Error", "Hora fin debe ser mayor a inicio")
            return

        grupo_id = self._catalogos["grupos"].get(grupo)
        materia_id = self._catalogos["materias"].get(materia)
        profesor_id = self._catalogos["profesores"].get(profesor)
        salon_id = self._catalogos["salones"].get(salon)

        if not all([grupo_id, materia_id, profesor_id, salon_id]):
            messagebox.showerror("Error", "Catalogos incompletos")
            return

        try:
            if db.hay_conflicto(self.conn, grupo_id, salon_id, dia, inicio, fin):
                messagebox.showerror("Error", "Conflicto con salon o grupo")
                return
            db.crear_horario(self.conn, grupo_id, materia_id, profesor_id, salon_id, dia, inicio, fin)
        except Exception as exc:
            messagebox.showerror("Error", str(exc))
            return

        self.horario_inicio.delete(0, "end")
        self.horario_fin.delete(0, "end")
        self._cargar_horarios()

    def _eliminar_horario(self):

        horario_id = self._seleccion_id(self.tree_horarios)
        if not horario_id:
            messagebox.showerror("Error", "Selecciona un horario")
            return
        try:
            db.eliminar_horario(self.conn, horario_id)
        except Exception as exc:
            messagebox.showerror("Error", str(exc))
            return
        self._cargar_horarios()

    def _consultar_grupo(self):

        grupo = self.consulta_grupo.get().strip()
        if not grupo:
            messagebox.showerror("Error", "Selecciona un grupo")
            return
        grupo_id = self._catalogos["grupos"].get(grupo)
        if not grupo_id:
            messagebox.showerror("Error", "Grupo invalido")
            return

        self._limpiar_tree(self.tree_consulta)
        for fila in db.consultar_horarios_por_grupo(self.conn, grupo_id):
            self.tree_consulta.insert("", "end", values=fila)

    def _consultar_libres(self):

        dia = self.libre_dia.get().strip()
        hora = self._parse_hora(self.libre_hora.get())
        if not dia:
            messagebox.showerror("Error", "Selecciona un dia")
            return
        if not hora:
            messagebox.showerror("Error", "Hora invalida, usa HH:MM")
            return

        self.list_libres.delete(0, "end")
        for nombre, in db.salones_libres(self.conn, dia, hora):
            self.list_libres.insert("end", nombre)

    def cerrar(self):

        try:
            if self.conn:
                self.conn.close()
        finally:
            self.root.destroy()

    def ejecutar(self):

        self.root.mainloop()
