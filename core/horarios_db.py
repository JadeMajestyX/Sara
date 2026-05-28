import psycopg2

from config import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER


def conectar():

    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )


def crear_tablas(conn):

    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS grupos (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(10) UNIQUE NOT NULL
            );
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS salones (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(20) UNIQUE NOT NULL,
                capacidad INTEGER
            );
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS profesores (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL
            );
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS materias (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(100) UNIQUE NOT NULL
            );
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS horarios (
                id SERIAL PRIMARY KEY,
                grupo_id INTEGER NOT NULL,
                materia_id INTEGER NOT NULL,
                profesor_id INTEGER NOT NULL,
                salon_id INTEGER NOT NULL,
                dia_semana VARCHAR(15) NOT NULL,
                hora_inicio TIME NOT NULL,
                hora_fin TIME NOT NULL,
                CHECK (hora_fin > hora_inicio),
                FOREIGN KEY (grupo_id) REFERENCES grupos(id),
                FOREIGN KEY (materia_id) REFERENCES materias(id),
                FOREIGN KEY (profesor_id) REFERENCES profesores(id),
                FOREIGN KEY (salon_id) REFERENCES salones(id)
            );
            """
        )

    conn.commit()


def listar_grupos(conn):

    with conn.cursor() as cur:
        cur.execute("SELECT id, nombre FROM grupos ORDER BY nombre;")
        return cur.fetchall()


def listar_salones(conn):

    with conn.cursor() as cur:
        cur.execute("SELECT id, nombre, capacidad FROM salones ORDER BY nombre;")
        return cur.fetchall()


def listar_profesores(conn):

    with conn.cursor() as cur:
        cur.execute("SELECT id, nombre FROM profesores ORDER BY nombre;")
        return cur.fetchall()


def listar_materias(conn):

    with conn.cursor() as cur:
        cur.execute("SELECT id, nombre FROM materias ORDER BY nombre;")
        return cur.fetchall()


def crear_grupo(conn, nombre):

    with conn.cursor() as cur:
        cur.execute("INSERT INTO grupos (nombre) VALUES (%s);", (nombre,))
    conn.commit()


def crear_salon(conn, nombre, capacidad):

    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO salones (nombre, capacidad) VALUES (%s, %s);",
            (nombre, capacidad)
        )
    conn.commit()


def crear_profesor(conn, nombre):

    with conn.cursor() as cur:
        cur.execute("INSERT INTO profesores (nombre) VALUES (%s);", (nombre,))
    conn.commit()


def crear_materia(conn, nombre):

    with conn.cursor() as cur:
        cur.execute("INSERT INTO materias (nombre) VALUES (%s);", (nombre,))
    conn.commit()


def eliminar_grupo(conn, grupo_id):

    with conn.cursor() as cur:
        cur.execute("DELETE FROM grupos WHERE id = %s;", (grupo_id,))
    conn.commit()


def eliminar_salon(conn, salon_id):

    with conn.cursor() as cur:
        cur.execute("DELETE FROM salones WHERE id = %s;", (salon_id,))
    conn.commit()


def eliminar_profesor(conn, profesor_id):

    with conn.cursor() as cur:
        cur.execute("DELETE FROM profesores WHERE id = %s;", (profesor_id,))
    conn.commit()


def eliminar_materia(conn, materia_id):

    with conn.cursor() as cur:
        cur.execute("DELETE FROM materias WHERE id = %s;", (materia_id,))
    conn.commit()


def listar_horarios(conn):

    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                h.id,
                g.nombre,
                m.nombre,
                p.nombre,
                s.nombre,
                h.dia_semana,
                h.hora_inicio,
                h.hora_fin
            FROM horarios h
            JOIN grupos g ON h.grupo_id = g.id
            JOIN materias m ON h.materia_id = m.id
            JOIN profesores p ON h.profesor_id = p.id
            JOIN salones s ON h.salon_id = s.id
            ORDER BY h.dia_semana, h.hora_inicio;
            """
        )
        return cur.fetchall()


def crear_horario(conn, grupo_id, materia_id, profesor_id, salon_id, dia_semana, hora_inicio, hora_fin):

    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO horarios (
                grupo_id,
                materia_id,
                profesor_id,
                salon_id,
                dia_semana,
                hora_inicio,
                hora_fin
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s);
            """,
            (grupo_id, materia_id, profesor_id, salon_id, dia_semana, hora_inicio, hora_fin)
        )
    conn.commit()


def eliminar_horario(conn, horario_id):

    with conn.cursor() as cur:
        cur.execute("DELETE FROM horarios WHERE id = %s;", (horario_id,))
    conn.commit()


def hay_conflicto(conn, grupo_id, salon_id, dia_semana, hora_inicio, hora_fin):

    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT 1
            FROM horarios
            WHERE dia_semana = %s
            AND (
                (salon_id = %s)
                OR (grupo_id = %s)
            )
            AND NOT (hora_fin <= %s OR hora_inicio >= %s)
            LIMIT 1;
            """,
            (dia_semana, salon_id, grupo_id, hora_inicio, hora_fin)
        )
        return cur.fetchone() is not None


def consultar_horarios_por_grupo(conn, grupo_id):

    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                g.nombre,
                m.nombre,
                p.nombre,
                s.nombre,
                h.dia_semana,
                h.hora_inicio,
                h.hora_fin
            FROM horarios h
            JOIN grupos g ON h.grupo_id = g.id
            JOIN materias m ON h.materia_id = m.id
            JOIN profesores p ON h.profesor_id = p.id
            JOIN salones s ON h.salon_id = s.id
            WHERE h.grupo_id = %s
            ORDER BY h.dia_semana, h.hora_inicio;
            """,
            (grupo_id,)
        )
        return cur.fetchall()


def consultar_horarios_por_profesor(conn, profesor_id):

    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                g.nombre,
                m.nombre,
                p.nombre,
                s.nombre,
                h.dia_semana,
                h.hora_inicio,
                h.hora_fin
            FROM horarios h
            JOIN grupos g ON h.grupo_id = g.id
            JOIN materias m ON h.materia_id = m.id
            JOIN profesores p ON h.profesor_id = p.id
            JOIN salones s ON h.salon_id = s.id
            WHERE h.profesor_id = %s
            ORDER BY h.dia_semana, h.hora_inicio;
            """,
            (profesor_id,)
        )
        return cur.fetchall()


def consultar_horarios_por_materia(conn, materia_id):

    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                g.nombre,
                m.nombre,
                p.nombre,
                s.nombre,
                h.dia_semana,
                h.hora_inicio,
                h.hora_fin
            FROM horarios h
            JOIN grupos g ON h.grupo_id = g.id
            JOIN materias m ON h.materia_id = m.id
            JOIN profesores p ON h.profesor_id = p.id
            JOIN salones s ON h.salon_id = s.id
            WHERE h.materia_id = %s
            ORDER BY h.dia_semana, h.hora_inicio;
            """,
            (materia_id,)
        )
        return cur.fetchall()


def salones_libres(conn, dia_semana, hora):

    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT nombre
            FROM salones
            WHERE id NOT IN (
                SELECT salon_id
                FROM horarios
                WHERE dia_semana = %s
                AND %s BETWEEN hora_inicio AND hora_fin
            )
            ORDER BY nombre;
            """,
            (dia_semana, hora)
        )
        return cur.fetchall()
