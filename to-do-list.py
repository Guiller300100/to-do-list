import sqlite3
import PySimpleGUI as sg
from datetime import date, timedelta

fecha = date.today()


def consulta_tasks_not_do(cursor, date):
    consult = (
        "Select id, task from tasks where fecha="
        + "'"
        + date.strftime("%Y-%m-%d")
        + "' and hecho = 0"
    )
    cursor.execute(consult)
    return cursor.fetchall()


def consulta_tareas(cursor, fecha, hecho):
    consult = f"SELECT id, task FROM tasks WHERE fecha='{fecha.strftime('%Y-%m-%d')}' AND hecho={int(hecho)}"
    cursor.execute(consult)
    return cursor.fetchall()


def start_window(cursor):
    global fecha
    rows_not_do = consulta_tareas(cursor, fecha, False)
    rows_do = consulta_tareas(cursor, fecha, True)
    sg.theme("LightBrown11")
    layout = [
        [
            sg.Button("<", key="yesterday"),
            sg.Text(fecha, key="fechaCabecera"),
            sg.Button(">", key="tomorrow"),
            sg.Stretch(),
            sg.Button("Close", key="Close", size=(10, 1)),
        ],
        [
            sg.Listbox(
                [f"{row[0]}: {row[1]}" for row in rows_not_do],
                size=(40, 10),
                expand_x=True,
                key="-TASK LIST-",
                select_mode="multiple",
                enable_events=True,
            )
        ],
        [
            sg.Button("Do it", key="hecho"),
            sg.Button("Borrar", key="borrar"),
            sg.Button("Undo", key="undo"),
        ],
        [
            sg.Listbox(
                [f"{row[0]}: {row[1]}" for row in rows_do],
                size=(40, 10),
                expand_x=True,
                key="TASKHECHAS",
                select_mode="multiple",
                enable_events=True,
            )
        ],
        [
            sg.Text(""),
        ],
        [
            sg.Input(default_text="Task", size=(15, 1), key="-TASK-"),
            sg.InputText(
                default_text=date.today().strftime("%Y-%m-%d"),
                key="-FECHA-",
                size=(11, 1),
            ),
            sg.CalendarButton("Calendario", target="-FECHA-", format="%Y-%m-%d"),
            sg.Button("Add", key="add"),
        ],
    ]

    window = sg.Window(
        "Bases de datos",
        layout,
        location=(None, None),
        element_justification="center",
        resizable=True,
        size=(600, 500),
    )
    return window


def actualizar_ventana(window, cursor, fecha):
    # Actualiza el texto de la fecha en la cabecera
    window["fechaCabecera"].update(fecha.strftime("%Y-%m-%d"))

    # Consulta las tareas de la fecha actual en la base de datos
    rows_not_do = consulta_tareas(cursor, fecha, False)
    rows_do = consulta_tareas(cursor, fecha, True)
    if not rows_not_do:
        window["-TASK LIST-"].update(values=[])
    else:
        # Actualiza la lista de tareas en la ventana
        task_list = window["-TASK LIST-"]
        task_list.update(values=[f"{row[0]}: {row[1]}" for row in rows_not_do])

    if not rows_do:
        window["TASKHECHAS"].update(values=[])
    else:
        # Actualiza la lista de tareas en la ventana
        task_list = window["TASKHECHAS"]
        task_list.update(values=[f"{row[0]}: {row[1]}" for row in rows_do])

    return window


def task_hecha(window, cursor):
    fec = window["fechaCabecera"].get()
    selected_indices = window["-TASK LIST-"].get_indexes()
    if len(selected_indices) == 1:
        id = window["-TASK LIST-"].get()[0].split(":")[0]
        update_query = f"UPDATE tasks SET hecho = 1 WHERE id = {id}"
        cursor.execute(update_query)
        conn.commit()
    else:
        task_list = window["-TASK LIST-"].get()
        for i in range(0, len(task_list)):
            id = task_list[i].split(":")[0]
            update_query = f"UPDATE tasks SET hecho = 1 WHERE id ='{id}'"
            cursor.execute(update_query)
            conn.commit()
    actualizar_ventana(window, cursor, fecha)


def borrar_seleccionados_no_hechos(window, cursor):
    selected_indices_not_do = window["-TASK LIST-"].get_indexes()
    selected_indices_do = window["TASKHECHAS"].get_indexes()
    if len(selected_indices_not_do) == 1:
        task_id = window["-TASK LIST-"].get()[selected_indices_not_do[0]].split(":")[0]
        delete_query = f"DELETE FROM tasks WHERE id ='{task_id}'"
        cursor.execute(delete_query)
        conn.commit()
    else:
        for index in selected_indices_not_do:
            task_id = window["-TASK LIST-"].get()[index].split(":")[0]
            delete_query = f"DELETE FROM tasks WHERE id ='{task_id}'"
            cursor.execute(delete_query)
            conn.commit()

    if len(selected_indices_do) == 1:
        task_id = window["TASKHECHAS"].get()[selected_indices_do[0]].split(":")[0]
        delete_query = f"DELETE FROM tasks WHERE id ='{task_id}'"
        cursor.execute(delete_query)
        conn.commit()
    else:
        for index in selected_indices_do:
            task_id = window["TASKHECHAS"].get()[index - 1].split(":")[0]
            delete_query = f"DELETE FROM tasks WHERE id ='{task_id}'"
            cursor.execute(delete_query)
            conn.commit()
    actualizar_ventana(window, cursor, fecha)

def recuperar_task(window, cursor):
    selected_indices = window["TASKHECHAS"].get_indexes()
    if len(selected_indices) == 1:
        id = window["TASKHECHAS"].get()[0].split(":")[0]
        update_query = f"UPDATE tasks SET hecho = 0 WHERE id={id}"
        cursor.execute(update_query)
        conn.commit()
    else:
        for index in selected_indices:
            task_list = window["TASKHECHAS"].get()
            if 0 <= index < len(task_list):
                id = task_list[index].split(":")[0]
                update_query = f"UPDATE tasks SET hecho = 0 WHERE id ='{id}'"
                cursor.execute(update_query)
                conn.commit()
    actualizar_ventana(window, cursor, fecha)


def crear_task(window, cursor):
    task = window["-TASK-"].get()
    fec = window["-FECHA-"].get()
    create_query = (
        f"INSERT INTO tasks(task, fecha, hecho) values ('{task}', '{fec}', 0)"
    )
    cursor.execute(create_query)
    conn.commit()
    window["-TASK-"].update(value="")
    actualizar_ventana(window, cursor, fecha)


def check(check_window, cursor):
    global fecha
    while True:
        event, values = check_window.read()
        if event == "Close" or event == sg.WIN_CLOSED:
            return
        elif event == "yesterday":
            fecha = fecha - timedelta(days=1)
            check_window = actualizar_ventana(check_window, cursor, fecha)
            check_window["fechaCabecera"].update(fecha.strftime("%Y-%m-%d"))

        elif event == "tomorrow":
            fecha = fecha + timedelta(days=1)
            check_window = actualizar_ventana(check_window, cursor, fecha)
            check_window["fechaCabecera"].update(fecha.strftime("%Y-%m-%d"))
        elif event == "borrar":
            borrar_seleccionados_no_hechos(check_window, cursor)
        elif event == "hecho":
            task_hecha(check_window, cursor)
        elif event == "undo":
            recuperar_task(check_window, cursor)
        elif event == "add":
            crear_task(check_window, cursor)


conn = sqlite3.connect("data.db")
cursor = conn.cursor()
window = start_window(cursor)

check(window, cursor)

window.close()
cursor.close()
conn.close()
