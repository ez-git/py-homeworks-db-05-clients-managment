import psycopg2


def create_db(conn):
    with conn.cursor() as cur:
        cur.execute("""
                        CREATE TABLE IF NOT EXISTS clients(
                        id SERIAL PRIMARY KEY,
                        first_name VARCHAR(64) NOT NULL,
                        last_name VARCHAR(64) NOT NULL,
                        email VARCHAR(320) UNIQUE NOT NULL
                        );   
                        CREATE TABLE IF NOT EXISTS clients_phones(
                        id SERIAL PRIMARY KEY,
                        client_id INTEGER NOT NULL REFERENCES clients(id),
                        phone VARCHAR(64) UNIQUE NOT NULL               
                        );
                    """)
        conn.commit()


def add_client(conn, first_name, last_name, email, phones=None):

    with conn.cursor() as cur:
        cur.execute("""
                        INSERT INTO clients(first_name, last_name, email) 
                        VALUES(%s, %s, %s) RETURNING id;
                    """, (first_name, last_name, email))
        client_id = cur.fetchone()[0]
        if phones is not None:
            for phone in phones:
                add_phone(conn, client_id, phone)


def add_phone(conn, client_id, phone):
    with conn.cursor() as cur:
        cur.execute("""
                     INSERT INTO clients_phones(client_id, phone) 
                     VALUES(%s, %s);
                    """, (client_id, phone))
        conn.commit()


def change_client(conn, client_id, first_name=None, last_name=None, email=None,
                  phones=None):

    with conn.cursor() as cur:
        queries = ''
        params = []
        if first_name is not None:
            queries += """
                        UPDATE clients SET first_name=%s WHERE id=%s;
                       """
            params += [first_name, client_id]
        if last_name is not None:
            queries += """
                        UPDATE clients SET last_name=%s WHERE id=%s;
                       """
            params += [last_name, client_id]
        if email is not None:
            queries += """
                        UPDATE clients SET email=%s WHERE id=%s;
                        """
            params += [email, client_id]

        if queries != '':
            cur.execute(queries, tuple(params))
            conn.commit()

        if phones is not None:
            cur.execute("""
                            DELETE FROM clients_phones WHERE client_id=%s;
                        """, (client_id,))
            conn.commit()
            for phone in phones:
                add_phone(conn, client_id, phone)


def delete_phone(conn, client_id, phone):
    with conn.cursor() as cur:
        cur.execute("""
                       DELETE 
                       FROM clients_phones 
                       WHERE client_id=%s AND phone=%s;
                   """, (client_id, phone))
        conn.commit()


def delete_client(conn, client_id):
    with conn.cursor() as cur:
        cur.execute("""
                    DELETE 
                    FROM clients_phones 
                    WHERE client_id=%s;
                    DELETE 
                    FROM clients
                    WHERE id=%s;
                """, (client_id, client_id))
        conn.commit()


def find_client(conn, first_name=None, last_name=None, email=None, phone=None):
    query = ''
    if first_name is not None:
        query = """
                    SELECT first_name, 
                    last_name, 
                    email, 
                    clients_phones.phone
                    FROM clients 
                    LEFT JOIN clients_phones 
                            ON clients.id = clients_phones.client_id
                    WHERE first_name = %s
                """
        param = first_name
    elif last_name is not None:
        query = """
                    SELECT first_name,
                    last_name, 
                    email,
                    clients_phones.phone 
                    FROM clients 
                    LEFT JOIN clients_phones 
                    ON clients.id = clients_phones.client_id
                    WHERE last_name = %s
                """
        param = last_name
    elif email is not None:
        query = """
                    SELECT first_name, 
                    last_name, 
                    email, 
                    clients_phones.phone
                    FROM clients
                    LEFT JOIN clients_phones 
                    ON clients.id = clients_phones.client_id 
                    WHERE email = %s
                """
        param = email
    elif phone is not None:
        query = """
                    SELECT first_name, 
                    last_name,
                    email, 
                    phone
                    FROM clients
                    INNER JOIN clients_phones 
                    ON clients.id = clients_phones.client_id 
                    WHERE clients.id = (SELECT client_id
                    FROM clients_phones
                    WHERE phone = %s)
                """
        param = phone

    with conn.cursor() as cur:
        cur.execute(query, (param,))
        result = cur.fetchall()
        if len(result) > 0:
            client_data = ''
            phones = []
            for each_data in result:
                if client_data == '':
                    client_data = f'{each_data[0]} {each_data[1]}, {each_data[2]}'
                phones += [each_data[3]]
            if len(phones) > 0:
                client_data = f'{client_data}, phones: {", ".join(phones)}'
            print(client_data)


def delete_db(conn):
    with conn.cursor() as cur:
        cur.execute("""
        DROP TABLE clients_phones;
        DROP TABLE clients;     
        """)
        conn.commit()


with psycopg2.connect(database="clients_management",
                      user="postgres",
                      password="") as conn:
    delete_db(conn)
    create_db(conn)
    add_client(conn, 'Billy', 'Thompson', 'billy.thompson@gmail.com', ['+01234567890', '+90123456789'])
    add_phone(conn, 1, '+12345678901')
    change_client(conn, 1, 'Tommy', 'Beavers', 'tommy.beavers@gmail.com', ['+23456789012', '+34567890123'])
    delete_phone(conn, 1, '+34567890123')
    find_client(conn, 'Tommy', 'Beavers', 'tommy.beavers@gmail.com', '+23456789012')
