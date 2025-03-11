import flet as ft
import requests
import time
import threading  # <-- Importante para usar hilos

from backend.app import PROBLEMAS

# Configuración del backend
BACKEND_URL_CHAT = "http://127.0.0.1:5000/chat"
BACKEND_URL_VERIFICAR = "http://127.0.0.1:5000/verificar_respuesta"
BACKEND_URL_OBTENER_PROBLEMA = "http://127.0.0.1:5000/obtener_problema"
BACKEND_URL_REGISTRAR_USUARIO = "http://127.0.0.1:5000/registrar_usuario"

def main(page: ft.Page):
    # Configuración de la página
    page.title = "Chatbot y Problemas Matemáticos"
    page.horizontal_alignment = "stretch"
    page.vertical_alignment = "stretch"
    page.padding = 20
    page.bgcolor = ft.colors.GREY_200

    # Variable para almacenar el ID del problema actual
    problema_actual_id = 1  # Por defecto, el primer problema

    # Variable para almacenar el ID del usuario
    usuario_id = None

    # --------------------------------
    # Pantalla 1: Consentimiento
    # --------------------------------
    def mostrar_pantalla_consentimiento():
        nombre_usuario = ft.TextField(
            hint_text="Ingresa tu nombre",
            width=200,
            bgcolor=ft.colors.WHITE,
            color=ft.colors.BLACK,
            border_color=ft.colors.BLUE_GREY_300,
            focused_border_color=ft.colors.BLUE_GREY_500
        )

        def registrar_usuario(e):
            nombre = nombre_usuario.value.strip()
            if not nombre:
                page.snack_bar = ft.SnackBar(content=ft.Text("Por favor, ingresa tu nombre."))
                page.snack_bar.open = True
                page.update()
                return

            try:
                response = requests.post(
                    BACKEND_URL_REGISTRAR_USUARIO,
                    json={"nombre": nombre}
                )
                if response.status_code == 200:
                    nonlocal usuario_id
                    usuario_id = response.json()["usuario_id"]
                    mostrar_pantalla_encuesta_inicial()
                else:
                    page.snack_bar = ft.SnackBar(content=ft.Text("Error al registrar el usuario."))
                    page.snack_bar.open = True
                    page.update()
            except requests.exceptions.RequestException:
                page.snack_bar = ft.SnackBar(content=ft.Text("Error al conectar con el servidor."))
                page.snack_bar.open = True
                page.update()

        consentimiento_text = ft.Text(
            "Por favor, lee y acepta el consentimiento informado para participar en este estudio.",
            size=16,
            color=ft.colors.BLACK87
        )
        aceptar_button = ft.ElevatedButton(
            text="Aceptar",
            on_click=registrar_usuario,
            bgcolor=ft.colors.BLUE_500,
            color=ft.colors.WHITE
        )
        page.clean()
        page.add(ft.Column(controls=[nombre_usuario, consentimiento_text, aceptar_button], spacing=20))

    # --------------------------------
    # Pantalla 2: Encuesta Inicial
    # --------------------------------
    def mostrar_pantalla_encuesta_inicial():
        # Combobox para la edad
        edad_combobox = ft.Dropdown(
            options=[
                ft.dropdown.Option("14"),
                ft.dropdown.Option("15"),
                ft.dropdown.Option("16"),
                ft.dropdown.Option("17"),
                ft.dropdown.Option("18"),
                ft.dropdown.Option("Mayor a 19")
            ],
            hint_text="Selecciona tu edad",
            width=200
        )

        # Radio buttons para el género
        genero_radio = ft.RadioGroup(
            content=ft.Column([
                ft.Radio(value="Femenino", label="Femenino"),
                ft.Radio(value="Masculino", label="Masculino"),
                ft.Radio(value="No binario", label="No binario"),
                ft.Radio(value="Prefiero no decirlo", label="Prefiero no decirlo")
            ])
        )

        # Combobox para la escuela
        escuela_combobox = ft.Dropdown(
            options=[
                ft.dropdown.Option("Bachillerato UNDL"),
                ft.dropdown.Option("Escuela 2"),
                ft.dropdown.Option("Escuela 3")
            ],
            hint_text="Selecciona tu escuela",
            width=200
        )

        # Checkbox para el nivel educativo de los padres
        nivel_educativo_checkbox = ft.Column([
            ft.Checkbox(label="No lo sé"),
            ft.Checkbox(label="No asistió a la escuela"),
            ft.Checkbox(label="Primaria incompleta"),
            ft.Checkbox(label="Primaria completa"),
            ft.Checkbox(label="Secundaria incompleta"),
            ft.Checkbox(label="Secundaria completa"),
            ft.Checkbox(label="Educación técnica o tecnológica"),
            ft.Checkbox(label="Universitaria incompleta"),
            ft.Checkbox(label="Universitaria completa"),
            ft.Checkbox(label="Posgrado (maestría o doctorado)")
        ])

        # Radio buttons para el uso de chatbots
        uso_chatbot_radio = ft.RadioGroup(
            content=ft.Column([
                ft.Radio(value="Sí", label="Sí"),
                ft.Radio(value="No", label="No")
            ])
        )

        # Radio buttons para el tiempo de uso de chatbots
        tiempo_uso_radio = ft.RadioGroup(
            content=ft.Column([
                ft.Radio(value="Menos de un mes", label="Menos de un mes"),
                ft.Radio(value="Entre 1 a 6 meses", label="Entre 1 a 6 meses"),
                ft.Radio(value="Entre 6 y 12 meses", label="Entre 6 y 12 meses"),
                ft.Radio(value="Más de un año", label="Más de un año")
            ])
        )

        # Radio buttons para la frecuencia de uso de chatbots
        frecuencia_uso_radio = ft.RadioGroup(
            content=ft.Column([
                ft.Radio(value="Una vez al día", label="Una vez al día"),
                ft.Radio(value="Varias veces al día", label="Varias veces al día"),
                ft.Radio(value="Una vez a la semana", label="Una vez a la semana"),
                ft.Radio(value="Varias veces a la semana", label="Varias veces a la semana"),
                ft.Radio(value="Una vez al mes", label="Una vez al mes"),
                ft.Radio(value="No lo utilicé este mes", label="No lo utilicé este mes.")
            ])
        )

        # Checkbox para áreas de uso de chatbots
        areas_uso_checkbox = ft.Column([
            ft.Checkbox(label="Educación"),
            ft.Checkbox(label="Trabajo"),
            ft.Checkbox(label="Entretenimiento"),
            ft.Checkbox(label="Salud"),
            ft.Checkbox(label="Otros")
        ])

        # Radio buttons para el uso de chatbots en matemáticas
        uso_matematicas_radio = ft.RadioGroup(
            content=ft.Column([
                ft.Radio(value="Sí", label="Sí"),
                ft.Radio(value="No", label="No")
            ])
        )

        # Botón para continuar
        continuar_button = ft.ElevatedButton(
            text="Continuar",
            on_click=lambda e: mostrar_pantalla_instrucciones(),
            bgcolor=ft.colors.BLUE_500,
            color=ft.colors.WHITE
        )

        # Layout de la encuesta inicial
        encuesta_inicial_layout = ft.Column(
            controls=[
                ft.Text("Edad:", size=16),
                edad_combobox,
                ft.Text("Género:", size=16),
                genero_radio,
                ft.Text("Escuela a la que pertenece:", size=16),
                escuela_combobox,
                ft.Text("Nivel educativo más alto de tus padres o cuidador principal:", size=16),
                nivel_educativo_checkbox,
                ft.Text("¿Has utilizado algún chatbot basado en IA Generativa?", size=16),
                uso_chatbot_radio,
                ft.Text("Si tu respuesta es sí, ¿Desde cuándo lo utilizas?", size=16),
                tiempo_uso_radio,
                ft.Text("Frecuencia de uso en el último mes:", size=16),
                frecuencia_uso_radio,
                ft.Text("Áreas de uso de chatbots:", size=16),
                areas_uso_checkbox,
                ft.Text("¿Has utilizado un chatbot para resolver problemas de matemáticas?", size=16),
                uso_matematicas_radio,
                continuar_button
            ],
            spacing=20,
            scroll=ft.ScrollMode.AUTO  # Habilitar scroll si el contenido es muy largo
        )

        page.clean()
        page.add(ft.Container(
            content=encuesta_inicial_layout,
            padding=20,
            bgcolor=ft.colors.WHITE70,
            border_radius=10,
            expand=True
        ))

    # --------------------------------
    # Pantalla 3: Instrucciones
    # --------------------------------
    def mostrar_pantalla_instrucciones():
        instrucciones_text = ft.Text(
            "Instrucciones:\n\n"
            "1. Resuelve los problemas matemáticos que se te presenten.\n"
            "2. Utiliza el chatbot para obtener ayuda si lo necesitas.\n"
            "3. Verifica tus respuestas antes de continuar.\n\n"
            "¡Buena suerte!",
            size=16,
            color=ft.colors.BLACK87
        )
        comenzar_button = ft.ElevatedButton(
            text="Comenzar",
            on_click=lambda e: mostrar_pantalla_intervencion(),
            bgcolor=ft.colors.BLUE_500,
            color=ft.colors.WHITE
        )
        page.clean()
        page.add(ft.Column(controls=[instrucciones_text, comenzar_button], spacing=20))

    # --------------------------------
    # Pantalla de Intervención (Chatbot y Problemas)
    # --------------------------------
    def mostrar_pantalla_intervencion():
        # Contenedor Izquierdo (Chatbot)
        chat_area = ft.ListView(expand=True, spacing=10, auto_scroll=True)

        user_input = ft.TextField(
            hint_text="Escribe tu mensaje...",
            expand=True,
            bgcolor=ft.colors.WHITE,
            color=ft.colors.BLACK,
            border_color=ft.colors.BLUE_GREY_300,
            focused_border_color=ft.colors.BLUE_GREY_500
        )

        def send_message(e):
            user_message = user_input.value.strip()
            if not user_message:
                chat_area.controls.append(
                    ft.Container(
                        content=ft.Text("Por favor, escribe un mensaje.", color=ft.colors.RED),
                        padding=10,
                        margin=ft.margin.only(bottom=5),
                        bgcolor=ft.colors.RED_50,
                        border_radius=5
                    )
                )
                page.update()
                return

            # Agregar el mensaje del usuario al chat
            chat_area.controls.append(
                ft.Container(
                    content=ft.Text(f"Usuario: {user_message}", color=ft.colors.BLACK),
                    padding=10,
                    margin=ft.margin.only(bottom=5),
                    bgcolor=ft.colors.BLUE_GREY_50,
                    border_radius=5
                )
            )
            user_input.value = ""
            page.update()

            # Enviar el mensaje al backend
            try:
                response = requests.post(
                    BACKEND_URL_CHAT,
                    json={"message": user_message}
                ).json()
                chat_area.controls.append(
                    ft.Container(
                        content=ft.Text(f"Bot: {response['response']}", color=ft.colors.BLACK),
                        padding=10,
                        margin=ft.margin.only(bottom=5),
                        bgcolor=ft.colors.BLUE_50,
                        border_radius=5
                    )
                )
            except requests.exceptions.RequestException:
                chat_area.controls.append(
                    ft.Container(
                        content=ft.Text("Error: No se pudo conectar con el servidor.", color=ft.colors.RED),
                        padding=10,
                        margin=ft.margin.only(bottom=5),
                        bgcolor=ft.colors.RED_50,
                        border_radius=5
                    )
                )
            page.update()

        send_button = ft.ElevatedButton(
            text="Enviar",
            icon=ft.icons.SEND,
            on_click=send_message,
            bgcolor=ft.colors.BLUE_500,
            color=ft.colors.WHITE
        )

        input_container = ft.Row(controls=[user_input, send_button], spacing=10)

        chat_container = ft.Container(
            content=ft.Column(controls=[chat_area, input_container], spacing=10, expand=True),
            width=400,
            border_radius=10,
            padding=15,
            bgcolor=ft.colors.BLUE_GREY_100
        )

        # Contenedor Derecho (Problemas Matemáticos)
        ejercicio_text = ft.Text(size=16, color=ft.colors.BLACK87)
        respuesta_container = ft.Column()
        feedback_text = ft.Text("", size=14, color=ft.colors.BLACK87)

        # Función para cargar un problema
        def cargar_problema(id_problema):
            nonlocal problema_actual_id
            problema_actual_id = id_problema  # Actualizar el ID del problema actual
            response = requests.get(f"{BACKEND_URL_OBTENER_PROBLEMA}/{id_problema}")
            if response.status_code == 200:
                problema = response.json()
                ejercicio_text.value = f"Problema {problema['id']}\n\n{problema['enunciado']}"
                respuesta_container.controls.clear()

                if problema["tipo"] == "texto":
                    respuesta_container.controls.append(
                        ft.TextField(
                            hint_text="Ingresa tu respuesta aquí...",
                            expand=True,
                            bgcolor=ft.colors.WHITE,
                            color=ft.colors.BLACK,
                            border_color=ft.colors.BLUE_GREY_300,
                            focused_border_color=ft.colors.BLUE_GREY_500
                        )
                    )
                elif problema["tipo"] == "opcion_multiple":
                    for opcion in problema["opciones"]:
                        respuesta_container.controls.append(
                            ft.Radio(value=opcion["valor"], label=opcion["texto"])
                        )

                page.update()
            else:
                feedback_text.value = "Error al cargar el problema."
                page.update()

        # Botones de flechas para cambiar de problema
        def avanzar_problema(e):
            nonlocal problema_actual_id
            if problema_actual_id < len(PROBLEMAS):
                problema_actual_id += 1
                cargar_problema(problema_actual_id)

        def retroceder_problema(e):
            nonlocal problema_actual_id
            if problema_actual_id > 1:
                problema_actual_id -= 1
                cargar_problema(problema_actual_id)

        botones_flechas = ft.Row(
            controls=[
                ft.IconButton(
                    icon=ft.icons.ARROW_BACK,
                    on_click=retroceder_problema,
                    icon_size=30,
                    tooltip="Problema anterior"
                ),
                ft.IconButton(
                    icon=ft.icons.ARROW_FORWARD,
                    on_click=avanzar_problema,
                    icon_size=30,
                    tooltip="Siguiente problema"
                )
            ],
            spacing=10
        )

        # Función para enviar la respuesta
        def enviar_respuesta(e):
            nonlocal problema_actual_id, usuario_id
            respuesta_usuario = None

            if respuesta_container.controls:
                # Si es un TextField
                if isinstance(respuesta_container.controls[0], ft.TextField):
                    respuesta_usuario = respuesta_container.controls[0].value
                # Si es un RadioGroup (opción múltiple)
                elif isinstance(respuesta_container.controls[0], ft.Radio):
                    respuesta_usuario = next(
                        (r.value for r in respuesta_container.controls if getattr(r, "value", None)),
                        None
                    )

            if not respuesta_usuario:
                feedback_text.value = "Por favor, ingresa una respuesta."
                page.update()
                return

            # Enviar la respuesta al backend para registrarla
            try:
                resp = requests.post(
                    f"{BACKEND_URL_VERIFICAR}/{problema_actual_id}",
                    json={"respuesta": respuesta_usuario, "usuario_id": usuario_id}
                )
                # Verificamos si hubo error
                if resp.status_code == 200:
                    feedback_text.value = "Respuesta enviada correctamente."
                    feedback_text.color = ft.colors.GREEN
                    # Pasar automáticamente al siguiente problema
                    if problema_actual_id < len(PROBLEMAS):
                        problema_actual_id += 1
                        cargar_problema(problema_actual_id)
                    else:
                        # Si no hay más problemas, redirigir a la encuesta final
                        mostrar_pantalla_encuesta_final()
                else:
                    feedback_text.value = "Error al enviar la respuesta."
                    feedback_text.color = ft.colors.RED
            except requests.exceptions.RequestException:
                feedback_text.value = "Error al enviar la respuesta (conexión)."
                feedback_text.color = ft.colors.RED

            page.update()

        # Botón para enviar la respuesta
        enviar_button = ft.ElevatedButton(
            text="Enviar",
            icon=ft.icons.SEND,
            on_click=enviar_respuesta,
            bgcolor=ft.colors.BLUE_500,
            color=ft.colors.WHITE
        )

        # Contenedor de problemas
        problemas_container = ft.Container(
            content=ft.Column(
                controls=[botones_flechas, ejercicio_text, respuesta_container, enviar_button, feedback_text],
                spacing=20,
                expand=True
            ),
            padding=20,
            bgcolor=ft.colors.WHITE70,
            border_radius=10,
            expand=True
        )

        # Layout principal (Row)
        main_layout = ft.Row(
            controls=[chat_container, problemas_container],
            spacing=20,
            expand=True
        )

        # Temporizador
        temporizador_text = ft.Text("30:00", size=24, color=ft.colors.BLACK87)

        # -- TEMPORIZADOR EN UN HILO PARA NO BLOQUEAR LA UI --
        def iniciar_temporizador():
            def cuenta_regresiva():
                tiempo_restante = 1800  # 30 minutos en segundos
                while tiempo_restante > 0:
                    minutos, segundos = divmod(tiempo_restante, 60)
                    temporizador_text.value = f"{minutos:02}:{segundos:02}"
                    page.update()
                    time.sleep(1)
                    tiempo_restante -= 1

                temporizador_text.value = "¡Tiempo terminado!"
                user_input.disabled = True
                send_button.disabled = True
                enviar_button.disabled = True
                page.update()

            # Crear e iniciar el hilo
            hilo = threading.Thread(target=cuenta_regresiva, daemon=True)
            hilo.start()

        # Llamamos a iniciar_temporizador() cuando cargamos esta pantalla
        iniciar_temporizador()

        # Cargar el primer problema por defecto
        cargar_problema(1)

        page.clean()
        page.add(ft.Column(controls=[temporizador_text, main_layout], spacing=20))

    # --------------------------------
    # Pantalla después de la intervención: Encuesta Final
    # --------------------------------
    def mostrar_pantalla_encuesta_final():
        encuesta_final_text = ft.Text(
            "Por favor, responde la siguiente encuesta sobre tu experiencia con el chatbot.",
            size=16,
            color=ft.colors.BLACK87
        )
        finalizar_button = ft.ElevatedButton(
            text="Finalizar",
            on_click=lambda e: page.window_close(),
            bgcolor=ft.colors.BLUE_500,
            color=ft.colors.WHITE
        )
        page.clean()
        page.add(ft.Column(controls=[encuesta_final_text, finalizar_button], spacing=20))

    # Iniciar con la pantalla de consentimiento
    mostrar_pantalla_consentimiento()

if __name__ == "__main__":
    ft.app(target=main)