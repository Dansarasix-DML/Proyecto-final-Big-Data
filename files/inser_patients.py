import mysql.connector
from faker import Faker
import random

# Configuración de conexión
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='1234',
    database='MedicineDB'
)

cursor = conn.cursor()
fake = Faker('es_ES')
random.seed(42)

condiciones = [
    "Hipertensión", "Diabetes tipo 2", "Insuficiencia renal", 
    "Asma", "Colesterol alto", "EPOC", "Cáncer", "Obesidad"
]

def generar_condiciones():
    num = random.randint(0, 2)
    return ", ".join(random.sample(condiciones, num)) if num > 0 else ""

# Generar e insertar 100 pacientes
for i in range(100):
    patient_id = f"p{i+1:03d}"
    nombre = fake.first_name()
    apellidos = fake.last_name() + " " + fake.last_name()
    edad = random.randint(18, 90)
    sex = random.choice(["M", "F"])
    condiciones_conocidas = generar_condiciones()

    query = """
        INSERT INTO pacientes (patient_id, nombre, apellidos, edad, sex, condiciones_conocidas)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    values = (patient_id, nombre, apellidos, edad, sex, condiciones_conocidas)
    cursor.execute(query, values)

# Confirmar y cerrar
conn.commit()
cursor.close()
conn.close()

print("Pacientes insertados correctamente.")
