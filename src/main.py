from typing import Literal, get_args
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from nicegui import ui, app

import config as c
from database import db
from sensor import get_measure

# include other pages
import tasks  # noqa: F401


def draw_navbar(active_page: Literal["Home", "Live", "History", "Thresholds"] = 'home'):

    ui.label("Weather Station").classes('text-2xl font-bold')

    buttons = [
        {"label": "Home", "icon": "home", "path": '/'},
        {"label": "Live", "icon": "live_tv", "path": '/live'},
        {"label": "History", "icon": "history", "path": '/history'},
        {"label": "Thresholds", "icon": "data_thresholding", "path": '/thresholds'},
    ]

    with ui.row().classes('justify-between'):
        for b in buttons:

            color = "primary" if b['label'] == active_page else "gray"
            current = ui.button(
                text=b['label'],
                icon=b['icon'],
                color=color,
                on_click=lambda path=b['path']: ui.navigate.to(path)
            )


@ui.page('/')
def index():
    draw_navbar("Home")
    ui.label("Welcome to the Weather Station Dashboard!")
    ui.label(f"Total measurements in database: {db.get_measurement_count()}")


@ui.page('/live')
def live():
    draw_navbar("Live")
    ui.label(
        f"Live Measurements - updates every {c.LIVE_MEASURE_INTERVAL} second(s)").classes(
        'text-xl font-bold')
    temperature_label = ui.label("N/A")
    humidity_label = ui.label("N/A")
    pressure_label = ui.label("N/A")

    def update_labels():
        measurement = get_measure()
        temperature_label.set_text(
            f"Temperature: {measurement.temperature:.2f} °C")
        humidity_label.set_text(f"Humidity: {measurement.humidity:.2f} %")
        pressure_label.set_text(f"Pressure: {measurement.pressure:.2f} hPa")

    ui.timer(c.LIVE_MEASURE_INTERVAL, update_labels)


@ui.page('/history')
def history_redirect():
    ui.navigate.to('/history/hour')


@ui.page('/history/{range}')
def history(range: Literal["hour", "today"] = "hour"):
    draw_navbar("History")
    ui.label("Historical Measurements").classes('text-xl font-bold')

    # secondary navbar: Last Hour / Today
    selected_range = {"value": range}

    with ui.row().classes('items-center gap-2'):
        last_hour_btn = ui.button(
            "Last Hour", color="primary" if range == 'hour' else "gray", on_click=lambda: set_range('hour'))
        today_btn = ui.button("Today", color="primary" if range == 'today' else "gray",
                              on_click=lambda: set_range('today'))

    # echart element
    echart = ui.echart({
        "tooltip": {},
        "xAxis": {"type": "category"},
        "yAxis": {
            "type": "value",
            'axisLabel': {':formatter': 'value => value + " °C"'}
        },
        "series": [
            {"type": "line", "color": "red", "data": []},
        ],
    })

    def load_data(range_option: str):
        now = datetime.now(tz=ZoneInfo(c.UI_TIMEZONE))
        if range_option == 'hour':
            since = int((now - timedelta(hours=1)).timestamp())
        elif range_option == 'today':
            since = int(now.replace(hour=0, minute=0,
                        second=0, microsecond=0).timestamp())

        rows = db.get_measurements_since(since)
        if not rows:
            ui.notify(
                "No measurements found for the selected range",
                type="warning")
            echart.options["series"][0]["data"] = []
            echart.options["xAxis"]["data"] = []
            echart.options["yAxis"]["min"] = 0
            echart.options["yAxis"]["max"] = 30
            echart.update()
            return

        data = [r['temperature'] for r in rows]
        times = [datetime.fromtimestamp(r['timestamp'], tz=ZoneInfo(
            c.UI_TIMEZONE)).strftime('%H:%M:%S') for r in rows]

        echart.options["series"][0]["data"] = data
        echart.options["xAxis"]["data"] = times
        echart.options["yAxis"]["min"] = int(min(data)) - 1
        echart.options["yAxis"]["max"] = int(max(data)) + 1
        echart.update()

    def set_range(range_option: str):
        selected_range['value'] = range_option
        ui.navigate.to(f'/history/{range_option}')

    # initial load
    load_data(range)


@ui.page('/thresholds')
def thresholds():
    def create_popup():
        with ui.dialog() as dialog, ui.card():
            with ui.column().classes('items-stretch'):
                ui.label("Create New Threshold").classes('text-lg font-bold')
                name_input = ui.input("Name")

                select_pool = list(get_args(db.MeasurementType))
                type_input = ui.select(
                    select_pool, label="Type", value=select_pool[0])

                operator_pool = list(get_args(db.CompareOperator))
                operator_input = ui.select(
                    operator_pool, label="Compare Operator", value=operator_pool[1])

                value_input = ui.input("Threshold Value")

                def submit():
                    nonlocal name_input, type_input, operator_input, value_input
                    if not name_input.value or not type_input.value or not operator_input.value or not value_input.value:
                        ui.notify("Please fill in all fields", color="red")
                        return
                    db.put_threshold(
                        None,
                        name=name_input.value,
                        measurement_type=type_input.value,
                        threshold_value=float(value_input.value),
                        compare_operator=operator_input.value,
                        last_triggered=0
                    )
                    dialog.close()
                    # refresh page to show new threshold
                    ui.navigate.to('/thresholds')

                ui.button("Submit", on_click=submit, color="primary")

        dialog.open()

    def delete_threshold(threshold_id: int):
        db.delete_threshold(threshold_id)
        ui.notify("Threshold deleted")
        ui.navigate.to('/thresholds')

    draw_navbar("Thresholds")
    ui.label("Threshold Settings").classes('text-xl font-bold')
    ui.button("Create New Threshold", icon="add", color="primary",
              on_click=create_popup)

    thresholds = db.get_thresholds()
    with ui.column():
        for t in thresholds:
            if t['last_triggered']:
                last_triggered = datetime.fromtimestamp(t['last_triggered'], tz=ZoneInfo(
                    c.UI_TIMEZONE)).strftime('%Y-%m-%d %H:%M:%S')
            else:
                last_triggered = "Never"
            with ui.card():
                md_lines = [
                    f"**{t['name']}**",
                    f"reacts on **{t['measurement_type']} {t['compare_operator']} {t['threshold_value']:.2f}**",
                    f"last triggered: **{last_triggered}**"
                ]
                ui.markdown(
                    "\n\n".join(md_lines)
                )
                ui.button("Delete", icon="delete", color="red",
                          on_click=lambda id=t['threshold_id']: delete_threshold(id))


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        dark=True,
        host='0.0.0.0',
        title='Weather Station',
        favicon='src/favicon.png',
    )
