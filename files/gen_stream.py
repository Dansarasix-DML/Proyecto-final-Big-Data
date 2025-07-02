# streaming_generator.py
from faker import Faker
import random
import json
from datetime import datetime
from kafka import KafkaProducer
import time
import mysql.connector

fake = Faker()

# Conexión a MySQL para obtener patient_ids
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="MedicineDB"
)
cursor = conn.cursor()
cursor.execute("SELECT patient_id FROM pacientes")
patient_ids = [row[0] for row in cursor.fetchall()]
cursor.close()
conn.close()

# Configuración del productor Kafka
producer = KafkaProducer(
    bootstrap_servers=['192.168.18.8:9094'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Función para crear datos sintéticos
def generate_vital_data():
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "patient_id": random.choice(patient_ids),
        "heart_rate": random.randint(60, 140),
        "blood_pressure": f"{random.randint(100, 180)}/{random.randint(60, 120)}",
        "temperature": round(random.uniform(36.0, 40.5), 1),
        "oxygen_saturation": random.randint(85, 100),
        "blood_glucose": random.randint(70, 200),
        "unit": random.choice(["UCI", "Planta", "Urgencias"])
    }

# Bucle de envío continuo
while True:
    message = generate_vital_data()
    producer.send('vitales_pacientes', value=message)
    print("Enviado:", message)
    time.sleep(1.5)  # Simula frecuencia de monitorización