import psycopg2


connection = psycopg2.connect(
    host="127.0.0.1",
    port="5432",
    database="sunvoltage_system",
    user="postgres",
    password="200303"
)
