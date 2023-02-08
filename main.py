
import psycopg2

class ClientsManager:

    def __init__(self):
        self.user = 'postgres'
        self.password = ''
        self.db = 'clients_management'

    def make_connect(self):
        return psycopg2.connect(database=self.db, user=self.user,
                         password=self.password)

    def init_db(self):
        with self.make_connect() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                CREATE TABLE IF NOT EXISTS clients(
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(64) NOT NULL,
                    surname VARCHAR(64) NOT NULL,
                    email VARCHAR(320) UNIQUE NOT NULL
                );
                
                CREATE TABLE IF NOT EXISTS clients_phones(
                    id SERIAL PRIMARY KEY,
                    phone VARCHAR(64) UNIQUE NOT NULL,
                    client_id INTEGER NOT NULL REFERENCES clients(id)
                );
                """)
                conn.commit()

    def email_is_exist(self, email: str) -> bool:
        with self.make_connect() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                       SELECT * 
                       FROM clients 
                       WHERE email = %s
                       LIMIT 1;     
                       """, (email,))
                return len(cur.fetchone()) > 0

    def add_client(self, name: str, surname: str, email: str) -> str:
        if self.email_is_exist(email):
            return 'Current e-mail already exist!'
        else:
            with self.make_connect() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                         INSERT INTO clients(name, surname, email) 
                         VALUES(%s, %s, %s);
                         """, (name, surname, email))
                    conn.commit()
                    return 'Client added.'

    def phone_is_exist(self, phone: str) -> bool:
        with self.make_connect() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                       SELECT * 
                       FROM clients_phones 
                       WHERE phone = %s
                       LIMIT 1;     
                       """, (phone,))
                return len(cur.fetchone()) > 0

    def add_phone(self, email: str, phone: str) -> str:
        if self.phone_is_exist(phone):
            return 'Current phone already exist!'
        else:
            with self.make_connect() as conn:
                with conn.cursor() as cur:
                    # cur.execute("""
                    #                        SELECT *
                    #                        FROM clients_phones
                    #                        WHERE phone = %s
                    #                        LIMIT 1;
                    #                        """, (phone,))
                    # cur.fetchone()[0]
                    # cur.execute("""
                    #                  INSERT INTO clients_phones(email, phone)
                    #                  VALUES(%s, %s, %s);
                    #                  """, (name, surname, email))
                    # conn.commit()
                    # return 'Phone added.'





