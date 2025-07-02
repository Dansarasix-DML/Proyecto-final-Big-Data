from pyspark.sql import SparkSession
from pyspark.sql.functions import col, split, when, from_json, to_json, struct, concat, lit, unix_timestamp, expr
from pyspark.sql.types import *
import json

# 1. Crear sesión Spark
spark = SparkSession.builder \
    .appName("KafkaToSparkStreaming") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

# 2. Definir el esquema del JSON entrante
schema = StructType([
    StructField("id", IntegerType(), True),
    StructField("timestamp", StringType(), True),
    StructField("patient_id", StringType(), True),
    StructField("heart_rate", IntegerType(), True),
    StructField("blood_pressure", StringType(), True),
    StructField("temperature", FloatType(), True),
    StructField("oxygen_saturation", IntegerType(), True),
    StructField("blood_glucose", IntegerType(), True),
    StructField("unit", StringType(), True),
])

# 3. Leer desde Kafka
df_kafka = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "192.168.18.8:9094") \
    .option("subscribe", "vitales_pacientes") \
    .option("startingOffsets", "earliest") \
    .load()

# 4. Convertir el value (bytes) a JSON
df_json = df_kafka.selectExpr("CAST(value AS STRING) as json") \
    .select(from_json(col("json"), schema).alias("data")) \
    .select("data.*")

# 5. ETL
# Separar presión arterial
df = df_json.withColumn("systolic_pressure", split(col("blood_pressure"), "/").getItem(0).cast("int")) \
    .withColumn("diastolic_pressure", split(col("blood_pressure"), "/").getItem(1).cast("int")) \
    .drop("blood_pressure")

# Convertir timestamp a milisegundos UNIX y reemplazar la columna
df = df.withColumn("timestamp_trimmed", expr("substring(timestamp, 1, 19)")) \
       .withColumn("timestamp_ms", (unix_timestamp("timestamp_trimmed", "yyyy-MM-dd'T'HH:mm:ss") * 1000).cast("long")) \
       .drop("timestamp") \
       .withColumnRenamed("timestamp_ms", "timestamp")

# Mapeo de unidades hospitalarias
df = df.withColumn("unit_index",
    when(col("unit") == "Urgencias", 0)
    .when(col("unit") == "UCI", 1)
    .when(col("unit") == "Planta", 2)
    .otherwise(-1))

# Filtro de datos erróneos
df = df.filter((col("temperature") >= 35) & (col("temperature") <= 42))

# Generación de alertas médicas
df = df.withColumn("alert",
    when((col("systolic_pressure") > 140) | (col("diastolic_pressure") > 90), "HIPERTENSION")
    .when((col("oxygen_saturation") < 90), "HIPOXIA")
    .when((col("blood_glucose") > 150), "HIPERGLUCEMIA")
    .otherwise("OK"))

# 6. Escritura en consola o en parquet (HDFS)
query_parquet = df.writeStream \
    .outputMode("append") \
    .format("parquet") \
    .option("path", "bda/proyecto/streaming/parquet") \
    .option("checkpointLocation", "bda/proyecto/streaming/checkpoints/parquet") \
    .start()

# 7. Construcción schema+payload
schema_json = {
    "type": "struct",
    "fields": [
        {"field": "timestamp", "type": "int64", "optional": True},
        {"field": "patient_id", "type": "string", "optional": True},
        {"field": "heart_rate", "type": "int32", "optional": True},
        {"field": "temperature", "type": "float", "optional": True},
        {"field": "oxygen_saturation", "type": "int32", "optional": True},
        {"field": "blood_glucose", "type": "int32", "optional": True},
        {"field": "unit", "type": "string", "optional": True},
        {"field": "systolic_pressure", "type": "int32", "optional": True},
        {"field": "diastolic_pressure", "type": "int32", "optional": True},
        {"field": "unit_index", "type": "int32", "optional": True},
        {"field": "alert", "type": "string", "optional": True}
    ],
    "optional": False,
    "name": "VitalSigns"
}

schema_str = json.dumps(schema_json)

payload_struct = struct(
    col("timestamp"),
    col("patient_id"),
    col("heart_rate"),
    col("temperature"),
    col("oxygen_saturation"),
    col("blood_glucose"),
    col("unit"),
    col("systolic_pressure"),
    col("diastolic_pressure"),
    col("unit_index"),
    col("alert")
)

df_out = df.select(
    concat(lit('"'), col("patient_id"), lit('"')).alias("key"),
    to_json(payload_struct).alias("payload_json")
).select(
    col("key"),
    concat(
        lit('{"schema": '), lit(schema_str), lit(', "payload": '), col("payload_json"), lit('}')
    ).alias("value")
)

# 8. Escribir al topic Kafka de salida
query_kafka = df_out.writeStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "192.168.18.8:9094") \
    .option("topic", "alertas_pacientes") \
    .option("checkpointLocation", "/bda/proyecto/streaming/checkpoints/kafka") \
    .start()

query_kafka.awaitTermination()
query_parquet.awaitTermination()