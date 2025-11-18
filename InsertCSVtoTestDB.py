import pandas as pd
from neo4j import GraphDatabase

# -----------------------------
# Neo4j холболт
# -----------------------------
URI = "bolt://localhost:7687"
USER = "neo4j"
PASSWORD = "12345678"
DATABASE = "test"  # Таны test database нэр
driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD), encrypted=False)

# -----------------------------
# CSV унших, багануудыг монголчлох
# -----------------------------
csv_file = "data.csv"
df = pd.read_csv(csv_file)

# Монгол нэрээр баганын нэр солих
df.rename(columns={
    "INCIDENT_NUMBER":"id",
    "OFFENSE_CODE":"зөрчлийн_код",
    "OFFENSE_CODE_GROUP":"зөрчлийн_бүлэг",
    "OFFENSE_DESCRIPTION":"зөрчлийн_тайлбар",
    "DISTRICT":"дүүрэг",
    "REPORTING_AREA":"тайлагнасан_газар",
    "SHOOTING":"тэсрэлт_эсэх",
    "OCCURRED_ON_DATE":"огноо",
    "YEAR":"он",
    "MONTH":"сар",
    "DAY_OF_WEEK":"долоо_хоногийн_өдөр",
    "HOUR":"цаг",
    "UCR_PART":"ucr_хэсэг",
    "STREET":"Гудамж",
    "Lat":"уртраг",
    "Long":"өргөрөг",
    "Location":"байршил"
}, inplace=True)

# Эхний 1000 мөрийг авах (туршилт)
df_head = df.head(1000)

# -----------------------------
# Incident node-г Neo4j-д оруулах функц
# -----------------------------
def insert_incidents(df):
    with driver.session(database=DATABASE) as session:
        for _, row in df.iterrows():
            session.run(
                """
                MERGE (i:Incident {id:$id})
                SET i.зөрчлийн_код = $code,
                    i.зөрчлийн_бүлэг = $group,
                    i.зөрчлийн_тайлбар = $desc,
                    i.дүүрэг = $district,
                    i.тайлагнасан_газар = $area,
                    i.тэсрэлт_эсэх = $shooting,
                    i.огноо = $date,
                    i.он = $year,
                    i.сар = $month,
                    i.долоо_хоногийн_өдөр = $day,
                    i.цаг = $hour,
                    i.ucr_хэсэг = $ucr,
                    i.Гудамж = $street,
                    i.уртраг = $lat,
                    i.өргөрөг = $long,
                    i.байршил = $location
                """,
                id=row["id"],
                code=row["зөрчлийн_код"] if pd.notna(row["зөрчлийн_код"]) else "",
                group=row["зөрчлийн_бүлэг"] if pd.notna(row["зөрчлийн_бүлэг"]) else "",
                desc=row["зөрчлийн_тайлбар"] if pd.notna(row["зөрчлийн_тайлбар"]) else "",
                district=row["дүүрэг"] if pd.notna(row["дүүрэг"]) else "",
                area=row["тайлагнасан_газар"] if pd.notna(row["тайлагнасан_газар"]) else "",
                shooting=row["тэсрэлт_эсэх"] if pd.notna(row["тэсрэлт_эсэх"]) else "",
                date=row["огноо"] if pd.notna(row["огноо"]) else "",
                year=row["он"] if pd.notna(row["он"]) else 0,
                month=row["сар"] if pd.notna(row["сар"]) else 0,
                day=row["долоо_хоногийн_өдөр"] if pd.notna(row["долоо_хоногийн_өдөр"]) else "",
                hour=row["цаг"] if pd.notna(row["цаг"]) else 0,
                ucr=row["ucr_хэсэг"] if pd.notna(row["ucr_хэсэг"]) else "",
                street=row["Гудамж"] if pd.notna(row["Гудамж"]) else "",
                lat=row["уртраг"] if pd.notna(row["уртраг"]) else 0.0,
                long=row["өргөрөг"] if pd.notna(row["өргөрөг"]) else 0.0,
                location=row["байршил"] if pd.notna(row["байршил"]) else ""
            )
    print("✅ Эхний 1000 мөр амжилттай Neo4j-д орууллаа.")

# -----------------------------
# Incident → District & Street холболт үүсгэх
# -----------------------------
def insert_relations():
    with driver.session(database='test') as session:
        # Incident → District
        session.run("""
            MATCH (i:Incident)
            WHERE i.дүүрэг IS NOT NULL AND i.дүүрэг <> ''
            MERGE (d:District {name: i.дүүрэг})
            MERGE (i)-[:OCCURRED_IN]->(d)
        """)
        # Incident → Street
        session.run("""
            MATCH (i:Incident)
            WHERE i.Гудамж IS NOT NULL AND i.Гудамж <> ''
            MERGE (s:Street {name: i.Гудамж})
            MERGE (i)-[:ON_STREET]->(s)
        """)
    print("✅ Холболтууд амжилттай үүсгэлээ.")

# -----------------------------
# Script ажиллуулах
# -----------------------------
if __name__ == "__main__":
    insert_incidents(df_head)
    insert_relations()
    driver.close()
