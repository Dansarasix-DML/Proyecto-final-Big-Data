# batch_generator.py
from faker import Faker
import random
import json
from datetime import datetime, timedelta
import mysql.connector
import subprocess
import os

fake = Faker('es_ES')

# Conexión a MySQL para obtener patient_ids
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="MedicineDB"
)
cursor = conn.cursor()
cursor.execute("SELECT patient_id FROM pacientes;")
patient_ids = [row[0] for row in cursor.fetchall()]

# Obtener el último analitica_id
cursor.execute("SELECT MAX(analitica_id) FROM analiticas;")
last_an = cursor.fetchone()
an_counter = last_an[0] if last_an[0] is not None else 0

# Obtener el último res_id
cursor.execute("SELECT MAX(res_id) FROM antibiotic_res;")
last_res = cursor.fetchone()
res_counter = last_res[0] if last_res else 0


# Datos posibles
bacterias = ["Klebsiella pneumoniae", "Escherichia coli", "Pseudomonas aeruginosa", "Staphylococcus aureus"]
antibioticos = ["ceftriaxona", "imipenem", "colistina", "ciprofloxacina"]

resistencias = ["resistente", "intermedio", "sensible"]
muestras = ["esputo", "sangre", "orina", "exudado nasal"]

# Generar lote de datos
resultados = []
for _ in range(200):  # cantidad de muestras generadas
    an_counter += 1
    analitica_id = an_counter
    patient_id = random.choice(patient_ids)
    sample_date = (datetime.today() - timedelta(days=random.randint(0, 10))).date().isoformat()
    sample_type = random.choice(muestras)
    bacteria_detected = random.choice(bacterias)

    query_an = """
        INSERT INTO analiticas (analitica_id, patient_id, sample_date, sample_type, bacteria_detected)
        VALUES (%s, %s, %s, %s, %s)
    """
    values_an = (analitica_id, patient_id, sample_date, sample_type, bacteria_detected)
    cursor.execute(query_an, values_an)

    for ab in antibioticos:
      res_counter += 1
      res_id = res_counter
      antibiotic_name = random.choice(antibioticos)
      resistance_level = random.choice(resistencias)
    
      query_res = """
        INSERT INTO antibiotic_res (res_id, analitica_id, antibiotic_name, resistance_level)
        VALUES (%s, %s, %s, %s)
      """
	    
      values_res = (res_id, analitica_id, antibiotic_name, resistance_level)
      cursor.execute(query_res, values_res)

# Confirmar y cerrar
conn.commit()
cursor.close()
conn.close()

print("Analíticas insertadas correctamente.")