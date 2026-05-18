import os
import tkinter as tk

from PIL import Image, ImageDraw, ImageOps, ImageTk


class AvatarWindow:

    def __init__(self, imagen_cerrada, imagen_hablando, width=881, height=1785, animation_ms=180):

        self.width = width
        self.height = height
        self.animation_ms = animation_ms
        self._animando = False
        self._mostrando_hablando = False
        self._job_animacion = None

        self.root = tk.Tk()
        self.root.title("Avatar")
        self.root.configure(bg="#11151c")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.cerrar)
        self.root.attributes("-fullscreen", True)
        self.root.bind("<Escape>", lambda event: self.cerrar())

        self.display_width = self.root.winfo_screenwidth()
        self.display_height = self.root.winfo_screenheight()

        self.imagen_cerrada = self._cargar_imagen(
            imagen_cerrada,
            "cerrado"
        )
        self.imagen_hablando = self._cargar_imagen(
            imagen_hablando,
            "hablando"
        )

        self.canvas = tk.Canvas(
            self.root,
            width=self.display_width,
            height=self.display_height,
            bg="#11151c",
            bd=0,
            highlightthickness=0,
            relief="flat"
        )
        self.canvas.pack(fill="both", expand=True)

        self._imagen_canvas = self.canvas.create_image(
            self.display_width // 2,
            self.display_height // 2,
            image=self.imagen_cerrada,
            anchor="center"
        )

        self._aplicar_imagen(self.imagen_cerrada)

    def _crear_placeholder(self, tipo):

        imagen = Image.new("RGBA", (self.width, self.height), "#1a2130")
        dibujo = ImageDraw.Draw(imagen)

        dibujo.ellipse((self.width * 0.20, self.height * 0.04, self.width * 0.80, self.height * 0.46), fill="#f2c9a0")
        dibujo.ellipse((self.width * 0.34, self.height * 0.14, self.width * 0.39, self.height * 0.17), fill="#1b1b1b")
        dibujo.ellipse((self.width * 0.61, self.height * 0.14, self.width * 0.66, self.height * 0.17), fill="#1b1b1b")
        dibujo.arc((self.width * 0.37, self.height * 0.18, self.width * 0.63, self.height * 0.28), start=10, end=170, fill="#8a4b2a", width=max(4, self.width // 110))

        if tipo == "hablando":
            dibujo.ellipse((self.width * 0.44, self.height * 0.24, self.width * 0.56, self.height * 0.30), fill="#7b2d2d")
        else:
            dibujo.line((self.width * 0.43, self.height * 0.27, self.width * 0.57, self.height * 0.27), fill="#7b2d2d", width=max(4, self.width // 110))

        return imagen

    def _cargar_imagen(self, ruta, tipo):

        if ruta and os.path.exists(ruta):

            imagen = Image.open(ruta).convert("RGBA")
        else:

            imagen = self._crear_placeholder(tipo)

        imagen = ImageOps.contain(
            imagen,
            (self.display_width, self.display_height),
            method=Image.LANCZOS
        )

        fondo = Image.new("RGBA", (self.display_width, self.display_height), "#11151c")
        x = (self.display_width - imagen.width) // 2
        y = (self.display_height - imagen.height) // 2
        fondo.paste(imagen, (x, y), imagen)

        return ImageTk.PhotoImage(fondo)

    def _aplicar_imagen(self, imagen):

        self.canvas.itemconfigure(self._imagen_canvas, image=imagen)
        self.canvas.image = imagen

    def mostrar_cerrado(self):

        self._animando = False

        if self._job_animacion is not None:

            try:
                self.root.after_cancel(self._job_animacion)
            except:
                pass

            self._job_animacion = None

        self.root.after(0, self._aplicar_imagen, self.imagen_cerrada)

    def mostrar_hablando(self):

        if self._animando:

            return

        self._animando = True
        self._mostrando_hablando = False
        self.root.after(0, self._animar)

    def _animar(self):

        if not self._animando or not self.root.winfo_exists():

            return

        self._mostrando_hablando = not self._mostrando_hablando

        imagen = self.imagen_hablando if self._mostrando_hablando else self.imagen_cerrada

        self._aplicar_imagen(imagen)

        self._job_animacion = self.root.after(self.animation_ms, self._animar)

    def cerrar(self):

        self._animando = False

        if self._job_animacion is not None:

            try:
                self.root.after_cancel(self._job_animacion)
            except:
                pass

            self._job_animacion = None

        if self.root.winfo_exists():

            self.root.after(0, self.root.destroy)

    def ejecutar(self):

        self.root.update_idletasks()

        self.root.mainloop()