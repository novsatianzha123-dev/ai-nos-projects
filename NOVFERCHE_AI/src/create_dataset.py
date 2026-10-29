"""
====================================================
NOVFERCHE AI
Improved Raw Dataset Generator

Purpose:
Generate simulated wearable sensor data
for monitoring-status classification.

Class:
0 = Routine Monitoring
1 = Needs Additional Monitoring

====================================================
"""


import os
import random
from datetime import datetime, timedelta

import pandas as pd



# =====================================
# PATH CONFIGURATION
# =====================================


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


RAW_FOLDER = os.path.join(
    BASE_DIR,
    "dataset",
    "raw"
)


os.makedirs(
    RAW_FOLDER,
    exist_ok=True
)


OUTPUT_FILE = os.path.join(
    RAW_FOLDER,
    "sensor_data_raw.csv"
)



# =====================================
# DATA CONFIGURATION
# =====================================


TOTAL_DATA = 6000


dataset = []



# =====================================
# GENERATE DATA
# =====================================


for i in range(TOTAL_DATA):


    cow_id = random.randint(
        1,
        100
    )


    timestamp = (
        datetime.now()
        +
        timedelta(
            hours=i*6
        )
    )



    # Simulasi pola sensor yang memerlukan pemantauan tambahan.

    if random.random() < 0.30:


        # ==========================
        # POLA SENSOR UNTUK PEMANTAUAN TAMBAHAN
        # ==========================


        temperature = random.uniform(
            39.3,
            40.2
        )


        activity = random.uniform(
            20,
            50
        )


        movement = random.uniform(
            10,
            40
        )


        rest_time = random.uniform(
            8,
            14
        )


        monitoring_status = 1



    else:


        # ==========================
        # KONDISI NORMAL
        # ==========================


        temperature = random.uniform(
            38.0,
            38.8
        )


        activity = random.uniform(
            60,
            100
        )


        movement = random.uniform(
            50,
            90
        )


        rest_time = random.uniform(
            3,
            8
        )


        monitoring_status = 0




    dataset.append(

        [

            cow_id,

            timestamp,

            round(
                temperature,
                2
            ),

            round(
                activity,
                2
            ),

            round(
                movement,
                2
            ),

            round(
                rest_time,
                2
            ),

            monitoring_status

        ]

    )



# =====================================
# DATAFRAME
# =====================================


df = pd.DataFrame(

    dataset,

    columns=[

        "cow_id",

        "timestamp",

        "temperature_celsius",

        "activity_level",

        "movement_index",

        "rest_duration_hour",

        "monitoring_status"

    ]

)



# =====================================
# SAVE DATA
# =====================================


df.to_csv(

    OUTPUT_FILE,

    index=False

)



print("==============================")
print("NOVFERCHE DATASET CREATED")
print("==============================")


print(df.head())


print("\nClass Distribution:")

print(
    df["monitoring_status"]
    .value_counts()
)


print("\nSaved:")

print(
    OUTPUT_FILE
)
