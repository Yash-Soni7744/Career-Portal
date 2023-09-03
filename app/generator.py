from pymongo import MongoClient
import random
import os
import dotenv

dotenv.load_dotenv()

MONGODB_URI = MongoClient(os.environ.get("MONGODB_URI"))
MONGODB_DB = MONGODB_URI["KRMU"]


for i in range(2210101001, 2210105000):
    MONGODB_DB["student_info"].insert_one(
        {
            "email": str(i) + "@krmu.edu.in",
            "name": "Student " + str(i),
            "branch": "CSE",
            "year": "2023",
            "roll_no": str(i),
            "phone": random.randint(7000000000, 9999999999)
        }
    )
    print("Inserted", str(i)[6:])

print("Done")