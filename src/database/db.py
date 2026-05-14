'''
Logic for interacting with the database
'''

from typing import Literal
import sqlite3

DATABASE_FILE = 'src/database/weather-station.db'

MeasurementType = Literal["temperature", "humidity", "pressure"]
CompareOperator = Literal["<", ">"]

# region General


def create_database():
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.executescript('''
            CREATE TABLE
                IF NOT EXISTS measurement (
                    measurement_id INTEGER PRIMARY KEY,
                    TIMESTAMP INTEGER,
                    pressure REAL,
                    humidity REAL,
                    temperature REAL
                );

            CREATE TABLE
                IF NOT EXISTS threshold (
                    threshold_id INTEGER PRIMARY KEY,
                    name TEXT,
                    measurement_type TEXT,
                    threshold_value REAL,
                    compare_operator TEXT,
                    last_triggered INTEGER
                );
        ''')
        conn.commit()


# region Measurements
def add_measurement(
    timestamp: int,
    temperature: float,
    humidity: float,
    pressure: float
):
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO measurement (timestamp, temperature, humidity, pressure)
            VALUES (?, ?, ?, ?)
        ''', (timestamp, temperature, humidity, pressure))
        conn.commit()


def get_measurement_count():
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM measurement')
        count = cursor.fetchone()[0]
        return count


def get_measurements_since(since_timestamp: int) -> list[dict]:
    '''Get all measurements since a given timestamp'''
    with sqlite3.connect(DATABASE_FILE) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM measurement 
            WHERE timestamp >= ?
            ORDER BY timestamp ASC
        ''', (since_timestamp,))
        rows = cursor.fetchall()
        result: list[dict] = []
        for row in rows:
            # normalize column names to lowercase to avoid KeyError due to case differences
            d: dict = {}
            for k in row.keys():
                d[k.lower()] = row[k]
            result.append(d)
        return result


# region Thresholds
def put_threshold(
    threshold_id: int | None,
    *,
    name: str = None,
    measurement_type: MeasurementType = None,
    threshold_value: float = None,
    compare_operator: CompareOperator = None,
    last_triggered: int = None
):
    '''
    create or update a threshold. 
    if id is None, a new threshold will be created.
    '''
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        if threshold_id is None:
            cursor.execute('''
                INSERT INTO threshold (name, measurement_type, threshold_value, compare_operator, last_triggered)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, measurement_type, threshold_value, compare_operator, last_triggered))
        else:
            cursor.execute('''
                UPDATE threshold
                SET
                    name = COALESCE(?, name),
                    measurement_type = COALESCE(?, measurement_type),
                    threshold_value = COALESCE(?, threshold_value),
                    compare_operator = COALESCE(?, compare_operator),
                    last_triggered = COALESCE(?, last_triggered)
                WHERE threshold_id = ?
            ''', (name, measurement_type, threshold_value, compare_operator, last_triggered, threshold_id))
        conn.commit()


def delete_threshold(threshold_id: int):
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            'DELETE FROM threshold WHERE threshold_id = ?', (threshold_id,))
        conn.commit()


def get_thresholds() -> list[dict]:
    with sqlite3.connect(DATABASE_FILE) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM threshold')
        return [dict(row) for row in cursor.fetchall()]


# create database on module load
create_database()
