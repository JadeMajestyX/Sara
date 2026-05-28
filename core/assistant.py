# core/assistant.py

import re
import unicodedata
from difflib import SequenceMatcher

from core import horarios_db as db


class VoiceAssistant:

    def __init__(
        self,
        recorder,
        speaker,
        whisper_engine,
        ia_engine,
        rag_engine,
        on_finish=None
    ):
        self.recorder = recorder
        self.speaker = speaker
        self.whisper = whisper_engine
        self.ia = ia_engine
        self.rag = rag_engine
        self.on_finish = on_finish
        self.db_conn = None

        try:
            self.db_conn = db.conectar()
            db.crear_tablas(self.db_conn)
        except Exception as error:
            print(f"Base de datos no disponible para consultas directas: {error}")

        self.historial = [
            {
                "role": "system",
                "content": (
                    "Eres una asistente virtual en español. "
                    "Responde breve, claro y con tono amigable. "
                    "No utilices emojis. "
                    "No inventes información: si no sabes algo, dilo con honestidad. "
                    "Habla de frente, como si estuvieras conversando con el usuario. "
                    "Actúas como una secretaria/asistente administrativa: orientas, informas y apoyas en temas institucionales y de atención. "
                    "No puedes enseñar programación ni responder solicitudes técnicas de código. "
                    "Si te piden código o temas de programación, rechaza la solicitud de forma breve y redirige a temas de orientación académica o administrativa. "
                    "Tus respuestas se escuchan por voz, así que deben ser fáciles de entender. "
                    "Eres una asistente inteligente de la Universidad de Colima, de la Facultad de Ingeniería Electromecánica (FIE). "
                    "Relaciona tus respuestas con la Universidad de Colima y la Facultad de Ingeniería Electromecánica (FIE) cuando sea pertinente. "
                    "Las carreras que se imparten en la Facultad de Ingeniería Electromecánica (FIE) son: Ingeniería de Software, Ingeniería en Mecatrónica, Ingeniería en Tecnologías Electrónicas, Ingeniero Mecánico Electricista y Maestría en Ingeniería Aplicada. "
                    "Si te preguntan por horarios, grupos, profesores o materias, puedes consultar la base de datos institucional para responder con información concreta. "
                    "Tus creadores son los alumnos Jose Angel Alvarez Carranza y Sandra Vannesa Rodriguez Arechiga."
                )
            }
        ]

    def _normalizar(self, texto):

        texto = texto.lower().strip()
        texto = unicodedata.normalize("NFD", texto)
        return "".join(
            caracter for caracter in texto
            if unicodedata.category(caracter) != "Mn"
        )

    def _mejor_coincidencia(self, texto, registros):

        texto_normalizado = self._normalizar(texto)
        candidatos = []

        for identificador, nombre in registros:
            nombre_normalizado = self._normalizar(nombre)
            if not nombre_normalizado:
                continue

            if nombre_normalizado in texto_normalizado:
                candidatos.append((1.0, len(nombre_normalizado), identificador, nombre))
                continue

            similitud = SequenceMatcher(None, texto_normalizado, nombre_normalizado).ratio()
            if similitud >= 0.78:
                candidatos.append((similitud, len(nombre_normalizado), identificador, nombre))

        if not candidatos:
            return None, None

        _, _, identificador, nombre = max(candidatos, key=lambda item: (item[0], item[1]))
        return identificador, nombre

    def _obtener_dia(self, texto):

        texto_normalizado = self._normalizar(texto)
        dias = [
            "lunes",
            "martes",
            "miercoles",
            "jueves",
            "viernes",
            "sabado",
            "domingo"
        ]

        for dia in dias:
            if dia in texto_normalizado:
                return dia

        return None

    def _obtener_hora(self, texto):

        texto_normalizado = self._normalizar(texto)

        coincidencia = re.search(r"\b(\d{1,2})(?::(\d{2}))?\b", texto_normalizado)
        if coincidencia:
            hora = int(coincidencia.group(1))
            minutos = int(coincidencia.group(2) or "0")
            if 0 <= hora <= 23 and 0 <= minutos <= 59:
                return hora, minutos

        romanos = {
            "i": 1,
            "ii": 2,
            "iii": 3,
            "iv": 4,
            "v": 5,
            "vi": 6,
            "vii": 7,
            "viii": 8,
            "ix": 9,
            "x": 10,
            "xi": 11,
            "xii": 12,
        }

        for romano, hora in romanos.items():
            if re.search(rf"\b{romano}\b", texto_normalizado):
                return hora, 0

        return None, None

    def _es_consulta_disponibilidad_profesor(self, texto_normalizado):

        palabras = (
            "libre",
            "ocupado",
            "disponible",
            "tiene clase",
            "tiene clases",
            "tiene horario",
            "imparte",
            "imparten",
            "da clase",
            "da clases",
            "clase",
            "clases",
        )

        return any(palabra in texto_normalizado for palabra in palabras)

    def _formatear_hora(self, hora, minutos):

        return f"{hora:02d}:{minutos:02d}"

    def _consultar_disponibilidad_profesor(self, profesor_nombre, filas, dia_busqueda, hora_consulta, minutos_consulta):

        if not filas:
            if dia_busqueda and hora_consulta is not None:
                return f"El profesor {profesor_nombre} está libre el {dia_busqueda} a las {self._formatear_hora(hora_consulta, minutos_consulta)}."
            if dia_busqueda:
                return f"El profesor {profesor_nombre} no tiene clases registradas el {dia_busqueda}."
            return f"El profesor {profesor_nombre} no tiene clases registradas."

        if hora_consulta is None:
            if dia_busqueda:
                resumen = self._formatear_horarios(filas)
                return f"El profesor {profesor_nombre} tiene estas clases el {dia_busqueda}: {resumen}"
            resumen = self._formatear_horarios(filas)
            return f"El profesor {profesor_nombre} tiene estas clases: {resumen}"

        hora_busqueda = hora_consulta * 60 + minutos_consulta
        conflictos = []

        for grupo, materia, profesor, salon, dia, inicio, fin in filas:
            if not self._dia_coincide(dia_busqueda, dia):
                continue

            inicio_min = inicio.hour * 60 + inicio.minute
            fin_min = fin.hour * 60 + fin.minute

            if inicio_min <= hora_busqueda < fin_min:
                conflictos.append((grupo, materia, profesor, salon, dia, inicio, fin))

        if conflictos:
            linea = self._formatear_horarios(conflictos)
            if dia_busqueda:
                return f"El profesor {profesor_nombre} no está libre el {dia_busqueda} a las {self._formatear_hora(hora_consulta, minutos_consulta)}. Tiene esto: {linea}"
            return f"El profesor {profesor_nombre} no está libre a las {self._formatear_hora(hora_consulta, minutos_consulta)}. Tiene esto: {linea}"

        if dia_busqueda:
            return f"El profesor {profesor_nombre} está libre el {dia_busqueda} a las {self._formatear_hora(hora_consulta, minutos_consulta)}."

        return f"El profesor {profesor_nombre} está libre a las {self._formatear_hora(hora_consulta, minutos_consulta)}."

    def _obtener_grupo_consulta(self, texto, grupos):

        texto_normalizado = self._normalizar(texto)
        texto_compacto = re.sub(r"[^a-z0-9]", "", texto_normalizado)
        grupos_normalizados = {
            self._normalizar(nombre): (identificador, nombre)
            for identificador, nombre in grupos
        }

        alias_grupos = {
            "primero": "1",
            "primer": "1",
            "segundo": "2",
            "segunda": "2",
            "tercero": "3",
            "tercera": "3",
            "cuarto": "4",
            "cuarta": "4",
            "quinto": "5",
            "quinta": "5",
            "sexto": "6",
            "sexta": "6",
            "septimo": "7",
            "septima": "7",
            "octavo": "8",
            "octava": "8",
            "noveno": "9",
            "novena": "9",
            "decimo": "10",
            "decima": "10",
            "onceavo": "11",
            "onceava": "11",
            "doceavo": "12",
            "doceava": "12",
        }

        for palabra, numero in alias_grupos.items():
            texto_normalizado = re.sub(rf"\b{palabra}\b", numero, texto_normalizado)

        texto_compacto = re.sub(r"[^a-z0-9]", "", texto_normalizado)

        patrones = [
            r"\b(\d{1,2})\s*(?:d|de)\b",
            r"\b(\d{1,2})\s*to\s*(?:d|de)\b",
            r"\b(\d{1,2})\s*mo\s*(?:d|de)\b",
        ]

        candidatos = []

        for grupo_normalizado, grupo_info in grupos_normalizados.items():
            grupo_compacto = re.sub(r"[^a-z0-9]", "", grupo_normalizado)
            if grupo_compacto and grupo_compacto in texto_compacto:
                return grupo_info

        for patron in patrones:
            for coincidencia in re.finditer(patron, texto_normalizado):
                numero = coincidencia.group(1)
                for sufijo in ("d", "de"):
                    candidato = f"{numero}{sufijo}"
                    if candidato in grupos_normalizados:
                        return grupos_normalizados[candidato]

        for palabra, numero in alias_grupos.items():
            if palabra in texto_normalizado:
                for sufijo in ("d", "de"):
                    candidato = f"{numero}{sufijo}"
                    if candidato in grupos_normalizados:
                        candidatos.append(grupos_normalizados[candidato])

        if len(candidatos) == 1:
            return candidatos[0]

        grupo_id, grupo_nombre = self._mejor_coincidencia(texto, grupos)
        if grupo_id is not None:
            return grupo_id, grupo_nombre

        return None, None

    def _variantes_sonoras(self, texto):

        texto_normalizado = self._normalizar(texto)
        variantes = {texto_normalizado}
        variantes.add(texto_normalizado.replace("j", "h"))
        variantes.add(texto_normalizado.replace("h", "j"))
        return {variante for variante in variantes if variante}

    def _obtener_profesor_consulta(self, texto, profesores):

        texto_normalizado = self._normalizar(texto)
        texto_variantes = self._variantes_sonoras(texto)

        profesores_normalizados = [
            (identificador, nombre, self._normalizar(nombre))
            for identificador, nombre in profesores
        ]

        for identificador, nombre, nombre_normalizado in profesores_normalizados:
            if not nombre_normalizado:
                continue

            if any(nombre_normalizado in variante for variante in texto_variantes):
                return identificador, nombre

        candidatos = []
        for identificador, nombre, nombre_normalizado in profesores_normalizados:
            if not nombre_normalizado:
                continue

            for variante in texto_variantes:
                similitud = SequenceMatcher(None, variante, nombre_normalizado).ratio()
                if similitud >= 0.68:
                    candidatos.append((similitud, len(nombre_normalizado), identificador, nombre))
                    break

        if candidatos:
            _, _, identificador, nombre = max(candidatos, key=lambda item: (item[0], item[1]))
            return identificador, nombre

        return None, None

    def _dia_coincide(self, dia_busqueda, dia_registro):

        if not dia_busqueda:
            return True

        return self._normalizar(dia_registro).startswith(dia_busqueda)

    def _filtrar_horarios(self, filas, dia_busqueda=None):

        if not filas:
            return []

        resultados = []
        for fila in filas:
            grupo, materia, profesor, salon, dia, inicio, fin = fila
            if not self._dia_coincide(dia_busqueda, dia):
                continue
            resultados.append(fila)

        return resultados

    def _formatear_horarios(self, filas):

        if not filas:
            return None

        lineas = []
        for grupo, materia, profesor, salon, dia, inicio, fin in filas:
            if hasattr(inicio, "strftime"):
                inicio = inicio.strftime("%H:%M")
            if hasattr(fin, "strftime"):
                fin = fin.strftime("%H:%M")
            lineas.append(
                f"{dia} {inicio}-{fin}: {materia} con {profesor} en {salon} para {grupo}."
            )

        return " ".join(lineas)

    def _consultar_base_datos(self, texto):

        if self.db_conn is None:
            return None

        texto_normalizado = self._normalizar(texto)

        palabras_clave = (
            "horario",
            "horarios",
            "clase",
            "clases",
            "libre",
            "libres",
            "ocupado",
            "ocupada",
            "ocupados",
            "ocupadas",
            "disponible",
            "disponibles",
            "imparte",
            "imparten",
            "da",
            "dicta",
            "materia",
            "materias",
            "profesor",
            "profesora",
            "maestro",
            "maestra",
            "docente"
        )

        if not any(palabra in texto_normalizado for palabra in palabras_clave):
            return None

        try:
            grupos = db.listar_grupos(self.db_conn)
            profesores = db.listar_profesores(self.db_conn)
            materias = db.listar_materias(self.db_conn)
            dia_busqueda = self._obtener_dia(texto)
            hora_consulta, minutos_consulta = self._obtener_hora(texto)
            pregunta_profesor = any(
                palabra in texto_normalizado
                for palabra in ("profesor", "profesora", "maestro", "maestra", "docente", "imparte", "imparten", "da", "dicta")
            )
            pregunta_disponibilidad = self._es_consulta_disponibilidad_profesor(texto_normalizado)

            grupo_id, grupo_nombre = self._obtener_grupo_consulta(texto, grupos)
            profesor_id, profesor_nombre = self._obtener_profesor_consulta(texto, profesores)
            materia_id, materia_nombre = self._mejor_coincidencia(texto, materias)

            pregunta_horario = any(
                palabra in texto_normalizado
                for palabra in ("horario", "horarios", "clase", "clases")
            )

            if profesor_id is not None and (pregunta_profesor or pregunta_disponibilidad):
                filas_profesor = self._filtrar_horarios(
                    db.consultar_horarios_por_profesor(self.db_conn, profesor_id),
                    dia_busqueda=dia_busqueda
                )

                if pregunta_disponibilidad:
                    return self._consultar_disponibilidad_profesor(
                        profesor_nombre,
                        filas_profesor,
                        dia_busqueda,
                        hora_consulta,
                        minutos_consulta
                    )

                filas = self._filtrar_horarios(
                    filas_profesor,
                    dia_busqueda=dia_busqueda
                )
                resumen = self._formatear_horarios(filas)
                if resumen:
                    if dia_busqueda:
                        return f"El profesor {profesor_nombre} imparte estas clases el {dia_busqueda}: {resumen}"
                    return f"El profesor {profesor_nombre} imparte estas clases: {resumen}"

            if (pregunta_profesor or pregunta_disponibilidad) and profesor_id is None:
                return (
                    "No identifiqué con certeza al profesor. "
                    "Si te refieres a Haro o Verde, dímelo así y te doy su horario exacto."
                )

            if materia_id is not None and ("materia" in texto_normalizado or "materias" in texto_normalizado or "clase" in texto_normalizado or "clases" in texto_normalizado):
                filas = self._filtrar_horarios(
                    db.consultar_horarios_por_materia(self.db_conn, materia_id),
                    dia_busqueda=dia_busqueda
                )
                resumen = self._formatear_horarios(filas)
                if resumen:
                    if dia_busqueda:
                        return f"La materia {materia_nombre} aparece el {dia_busqueda} en estos horarios: {resumen}"
                    return f"La materia {materia_nombre} aparece en estos horarios: {resumen}"

            if grupo_id is not None and ("grupo" in texto_normalizado or pregunta_horario or dia_busqueda is not None):
                filas = self._filtrar_horarios(
                    db.consultar_horarios_por_grupo(self.db_conn, grupo_id),
                    dia_busqueda=dia_busqueda
                )
                resumen = self._formatear_horarios(filas)
                if resumen:
                    if dia_busqueda:
                        return f"Estas son las clases del grupo {grupo_nombre} el {dia_busqueda}: {resumen}"
                    return f"Este es el horario del grupo {grupo_nombre}: {resumen}"

            if (pregunta_horario or pregunta_disponibilidad) and grupo_id is None and dia_busqueda is not None and not pregunta_profesor:
                return (
                    "No identifiqué el grupo con claridad. "
                    "Dímelo en formato como 6D, 6 de o sexto D y te busco el horario."
                )

            if (pregunta_horario or pregunta_disponibilidad) and grupo_id is None and "grupo" in texto_normalizado and not pregunta_profesor:
                return (
                    "No identifiqué el grupo con claridad. "
                    "Dímelo en formato como 6D, 6 de o sexto D y te busco el horario."
                )

            if grupo_id is not None or profesor_id is not None or materia_id is not None:
                return (
                    "Puedo consultar horarios por grupo, profesor o materia. "
                    "Dime cuál quieres ver y te lo busco en la base de datos."
                )

            if pregunta_horario:
                return (
                    "No identifiqué el grupo, profesor o materia con claridad. "
                    "Prueba diciendo 6D, el profesor Jaro o la materia exacta."
                )

        except Exception as error:
            return f"No pude consultar la base de datos en este momento: {error}"

        return None

    def es_comando_salida(self, texto):

        comandos = [
            "salir",
            "terminar",
            "adiós",
            "adios"
        ]

        return texto.lower() in comandos

    def es_consulta_codigo(self, texto):

        texto_normalizado = texto.lower()

        patrones = [
            r"\bc[oó]digo\b",
            r"\bprogramaci[oó]n\b",
            r"\bprogramar\b",
            r"\bscript\b",
            r"\balgoritmo\b",
            r"\bjava\b",
            r"\bpython\b",
            r"\bc\+\+\b",
            r"\bc#\b",
            r"\bjavascript\b",
            r"\bhtml\b",
            r"\bcss\b",
            r"\bsql\b",
            r"\bapi\b",
            r"\bfunci[oó]n\b",
            r"\bdepurar\b",
            r"\bcompilar\b",
            r"\bhola mundo\b",
            r"\bhello world\b"
        ]

        return any(re.search(patron, texto_normalizado) for patron in patrones)

    def iniciar(self):

        try:
            print("\nAsistente iniciado.\n")

            audio_queue = __import__("queue").Queue()
            stop_event = __import__("threading").Event()

            self.recorder.start_listening(
                on_utterance=audio_queue.put,
                on_speech_start=self.speaker.detener,
                stop_event=stop_event
            )

            self.speaker.hablar(
                "Hola, estoy aqui para resolver tus dudas acerca de la facultad."
            )

            while True:

                audio_path = audio_queue.get()

                texto = self.whisper.transcribir(audio_path)

                if not texto:

                    print("No se detectó voz.")
                    continue

                print("\nTú:", texto)

                if self.es_comando_salida(texto):

                    despedida = "Hasta luego."

                    print("\nIA:", despedida)

                    self.speaker.hablar(despedida)

                    break

                if self.es_consulta_codigo(texto):

                    respuesta = (
                        "No puedo ayudar con programación o código. "
                        "Puedo apoyarte como asistente en orientación académica y administrativa de la facultad."
                    )

                    print("\nIA:", respuesta)

                    self.historial.append({
                        "role": "user",
                        "content": texto
                    })

                    self.historial.append({
                        "role": "assistant",
                        "content": respuesta
                    })

                    self.speaker.hablar(respuesta)
                    continue

                respuesta_db = self._consultar_base_datos(texto)

                if respuesta_db:

                    print("\nIA:", respuesta_db)

                    self.historial.append({
                        "role": "user",
                        "content": texto
                    })

                    self.historial.append({
                        "role": "assistant",
                        "content": respuesta_db
                    })

                    self.speaker.hablar(respuesta_db)
                    continue

                self.historial.append({
                    "role": "user",
                    "content": texto
                })

                contexto = self.rag.search(texto)

                respuesta = self.ia.preguntar(
                    self.historial,
                    contexto=contexto
                )

                print("\nIA:", respuesta)

                self.historial.append({
                    "role": "assistant",
                    "content": respuesta
                })

                self.speaker.hablar(respuesta)
        finally:
            try:
                stop_event.set()
            except:
                pass

            try:
                if self.db_conn is not None:
                    self.db_conn.close()
            except:
                pass

            if self.on_finish is not None:
                try:
                    self.on_finish()
                except:
                    pass