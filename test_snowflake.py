import snowflake.connector
from getpass import getpass

# Prompt for password
password = getpass("Enter your Snowflake password: ")

# Connect to Snowflake
conn = snowflake.connector.connect(
    user='PraveenMeg',
    account='mopfeujvewrgribb',
    password=password
)

# Create a cursor object
cs = conn.cursor()

try:
    cs.execute("SELECT CURRENT_VERSION()")
    one_row = cs.fetchone()
    print("Snowflake version:", one_row[0])
finally:
    cs.close()
