from nicegui import app
import time

import config as c
from database import db
from mail import send_email
from sensor import get_measure


def measure_and_store():
    '''global measure and store function'''
    measurement = get_measure()
    db.add_measurement(
        timestamp=int(measurement.timestamp.timestamp()),
        temperature=measurement.temperature,
        humidity=measurement.humidity,
        pressure=measurement.pressure)


def check_for_thresholds():
    '''global check for thresholds function'''
    thresholds = db.get_thresholds()
    measurement = get_measure()
    now = int(time.time())
    measurement_values = {
        'temperature': measurement.temperature,
        'humidity': measurement.humidity,
        'pressure': measurement.pressure,
    }

    for threshold in thresholds:
        relevant_value = measurement_values.get(threshold['measurement_type'])
        if relevant_value is None:
            continue

        if threshold['compare_operator'] == '<':
            threshold_hit = relevant_value < threshold['threshold_value']
        elif threshold['compare_operator'] == '>':
            threshold_hit = relevant_value > threshold['threshold_value']
        else:
            continue

        if not threshold_hit:
            continue

        last_triggered = threshold.get('last_triggered') or 0
        if last_triggered and now - last_triggered < c.THRESHOLD_TRIGGER_COOLDOWN:
            continue

        subject = f"Weather Station threshold triggered: {threshold['name']}"
        body = (
            f"Threshold '{threshold['name']}' was triggered.\n\n"
            f"Measurement: {threshold['measurement_type']}\n"
            f"Operator: {threshold['compare_operator']}\n"
            f"Threshold: {threshold['threshold_value']}\n"
            f"Current value: {relevant_value}\n"
            f"Triggered at: {measurement.timestamp.isoformat()}"
        )

        db.put_threshold(threshold['threshold_id'], last_triggered=now)
        send_email(subject, body)


# Setup timer at module import
app.timer(c.REGULAR_MEASURE_INTERVAL, measure_and_store)
app.timer(c.THRESHOLD_CHECK_INTERVAL, check_for_thresholds)
