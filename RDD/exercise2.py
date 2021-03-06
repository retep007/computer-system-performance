from pyspark import SparkConf
from pyspark.context import SparkContext
from pyspark.sql.session import SparkSession
from datetime import datetime
from pyspark.sql.types import *
import time
# import argparse

# coreCount = '*'
# execMem = '1g'
# driverMem = '1g'
# masterMode = 'local[' + coreCount + ']'

conf = (SparkConf()
        # .setMaster(masterMode)
        # .set('spark.executor.memory', execMem)
        # .set('spark.driver.memory', driverMem)
       )

totalParseErrors = 0
        # .set('spark.executor.memory', '4g')

# spark-submit --master local[*] --driver-memory 500m --executor-memory 500m exercise2.py
# spark-submit exercise2.py --driver-memory 20g --executor-memory 20g
# spark-submit exercise2.py --driver-memory 500m --executor-memory 500m
# spark-submit exercise2.py --driver-memory 1g --executor-memory 1g

# sc = SparkContext('local[*]')
sc = SparkContext(conf=conf)
spark = SparkSession(sc)

schema = StructType([
    StructField("taxi_id", IntegerType()),
    StructField("trip_start_timestamp", TimestampType()),
    StructField("trip_end_timestamp", TimestampType()),
    StructField("trip_seconds", IntegerType()),
    StructField("trip_miles", FloatType()),
    StructField("pickup_census_tract", IntegerType()),
    StructField("dropoff_census_tract", IntegerType()),
    StructField("pickup_community_area", IntegerType()),
    StructField("dropoff_community_area", IntegerType()),
    StructField("fare", FloatType()),
    StructField("tips", FloatType()),
    StructField("tolls", FloatType()),
    StructField("extras", FloatType()),
    StructField("trip_total", FloatType()),
    StructField("payment_type", StringType()),
    StructField("company", IntegerType()),
    StructField("pickup_latitude", IntegerType()),
    StructField("pickup_longitude", IntegerType()),
    StructField("dropoff_latitude", IntegerType()),
    StructField("dropoff_longitude", IntegerType())
])


def parseData(fields):
    global totalParseErrors

    trip_start = fields[1]
    trip_end = fields[2]

    try:
        trip_start_month = fields[1].month
    except:
        totalParseErrors += 1
        # print("--------------PARSE ERROR-----------------")
        # print(fields)
        # print("------------------------------------------")
        trip_start_month = 1


    try:
        trip_end_month = fields[2].month
    except:
        totalParseErrors += 1
        # print("--------------PARSE ERROR-----------------")
        # print(fields)
        # print("------------------------------------------")
        trip_end_month = 1


    try:
        trip_seconds = int(fields[3])
    except:
        totalParseErrors += 1
        # print("--------------PARSE ERROR-----------------")
        # print(fields)
        # print("------------------------------------------")
        trip_seconds = 0

    try:
        trip_miles = float(fields[4])
    except:
        totalParseErrors += 1
        trip_miles = 0

    try:
        trip_total = float(fields[13])
    except:
        totalParseErrors += 1
        trip_total = 0

    payment_type = str(fields[14])

    return (trip_start_month, trip_seconds, trip_miles, trip_total, payment_type)


#path = "chicago_taxi_trips_2016_*.csv"
#path = "/opt/chicago-taxi-rides-2016/chicago_taxi_trips_2016_*.csv" # path on the server

# Loading the path of the data from a text file
dataPath = "dataPath.txt"
path = str(sc.textFile("dataPath.txt").first())

time1 = time.time()

# df = spark.read.option("header", "true").csv(path)
df = (spark.read
            .format("csv")
            .option("header", "true")
            .option("delimiter", ",")
            .schema(schema)
            .load(path)
        )


myRdd = df.rdd

time2 = time.time()

# myRdd.count()

time3 = time.time()

# paymentData = myRdd.map(parseData).filter(lambda x: x[1] > 60).filter(lambda y: y[2] > 1.0).filter(lambda z: "Cash" in z[4]).groupBy(lambda a: a[0])
paymentData = (myRdd.map(parseData)
                    .filter(lambda x: x[1] > 60)
                    .filter(lambda y: y[2] > 1.0)
                    .filter(lambda z: "Cash" in z[4])
                    .map(lambda a: ( a[0], a[3] ))
                    .reduceByKey(lambda c, d: c+d)
              )

time4 = time.time()




# print("Total parse errors:", totalParseErrors)




# print("Total payments with cash:")
# print(total)

print("\r\n")

print(paymentData.take(12))
time5 = time.time()

print("\r\n")

print("Dataframe 'load' time: ", time2 - time1)
print("RDD.count time: ", time3 - time2)
print("RDD Calculation time (seconds): ", time4 - time3)


epoch = str(int(time.time()))
# fileName = epoch + '_' + coreCount + 'core_' + driverMem + 'mem'
fileName = epoch
f = open(fileName + '.log',"w+")


content = (
    # "Config:  CPU core: " + coreCount + "  Driver memory: " + driverMem + "  Executor memory: " + execMem + "\r\n" +
    "Config:  " + str(sc._conf.getAll()) + "\r\n\r\n" +
    "Dataframe load time: " + str(time2 - time1) + "\r\n" +
    "RDD.count time:" + str(time3-time2) + "\r\n" +
    "RDD Calculation time: " + str(time4-time3) + "\r\n"
    "Total time: " + str(time5-time1) + "\r\n"
    )

f.write(content)
f.close()
