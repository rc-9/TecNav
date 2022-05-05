# Databricks notebook source
# SparkSQL imports
import pyspark.sql.functions as f
from pyspark.sql import Row
from pyspark.sql.types import *

# SparkML imports
from pyspark.ml.linalg import Vectors
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from pyspark.ml.feature import StringIndexer, Bucketizer, VectorAssembler, MinMaxScaler
from pyspark.ml import Pipeline

from datetime import datetime

# Establish Spark context
sc = spark.sparkContext 

# COMMAND ----------

# %fs rm -r /FileStore/tables/uc_past_patients.csv

# COMMAND ----------

patients_file = "dbfs:///FileStore/tables/uc_past_patients.csv"

patients_df =  spark.read.format('csv') \
    .option('header', True) \
    .load(patients_file)

# COMMAND ----------

patients_df = patients_df.filter(f.col('visit_date') == '2021-05-01')
patients_df.display()

# COMMAND ----------

# # patients_df.select(f.col('datetime')).transform(lambda x : patients_df.select(f.col('datetime').fromisoformat(x)))
def convert_time(x):
    return datetime.fromisoformat(x)
convert_timeUDF = udf(convert_time, DateType())
    
patients_df.withColumn('newdt', convert_timeUDF('datetime'))

# COMMAND ----------

patients_df = patients_df.withColumn('datetime', patients_df.select(f.to_timestamp(patients_df.datetime, 'yyyy-MM-dd HH:mm:ss').alias('datetime')))
patients_df.display()


# COMMAND ----------

### REPARTITION DATA BY CLINIC
patients_df.write \
    .format("csv") \
    .mode("overwrite") \
    .option("header", True) \
    .partitionBy('visit_location') \
    .save("FileStore/tables/partitioned_clinics/") 

# COMMAND ----------


