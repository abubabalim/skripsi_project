from mysql import connector
import configparser
import os

def load_db_config():
    config = configparser.ConfigParser()
    base_path = os.path.dirname(os.path.abspath(__file__))
    # print(base_path)
    parent_path = os.path.dirname(base_path)
    # print(parent_path)
    config_path = os.path.join(parent_path, 'config','config.ini')
    # print(config_path)
    try:
        config.read(config_path)
        return config
    except Exception as e:
        # print(f"Error reading config.ini: {e}")
        return None

# Initialize Database Connection
def get_db_connection():
    connection = None
    
    config = load_db_config()
    if config:
        # print(config.sections())
        try:
            database_config = config['Database']
        except KeyError:
            # print("Bagian 'Database' tidak ditemukan di config.ini")
            database_config = None
    else:
        database_config = None

    if not database_config:
        # print('')
        return connection
    
    try:
        connection = connector.connect(
            host=database_config.get('host'),
            user=database_config.get('user'),
            password=database_config.get('password'),
            database=database_config.get('database')
        )
    except Exception as ex:
        # print(ex)
        connection = connector.connect(
            host=database_config.get('host'),
            user=database_config.get('user'),
            password=database_config.get('password'),
        )

    return connection

# Function to Create Database and Table
def initialize_database():
    conn = get_db_connection()
    if not conn:
        # print("Failed to initialized Database!")
        return
    cursor = conn.cursor()

    # Create database if not exists
    cursor.execute("CREATE DATABASE IF NOT EXISTS skripsi_db")
    cursor.execute("USE skripsi_db")

    # Create barang table if not exists
    create_barang_table_query = """
    CREATE TABLE IF NOT EXISTS barang (
        kode_barang VARCHAR(50) NOT NULL PRIMARY KEY,
        barcode VARCHAR(50) NOT NULL,
        nama_barang VARCHAR(255) NOT NULL
    )
    """
    cursor.execute(create_barang_table_query)

    # Create transaksi table if not exists
    create_transaksi_table_query = """
    CREATE TABLE IF NOT EXISTS transaksi (
        kode_transaksi VARCHAR(50) NOT NULL PRIMARY KEY,
        tanggal_transaksi DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
    """
    cursor.execute(create_transaksi_table_query)

    # Create detail transaksi table if not exists
    create_detail_transaksi_table_query = """
    CREATE TABLE IF NOT EXISTS detail_transaksi (
        id INT AUTO_INCREMENT PRIMARY KEY,
        kode_transaksi VARCHAR(50) NOT NULL,
        kode_barang VARCHAR(50) NOT NULL,
        jumlah INT NOT NULL,
        harga DECIMAL(10,2) NOT NULL,
        diskon DECIMAL(10,2) NOT NULL,
        total_harga DECIMAL(10,2) NOT NULL,
        CONSTRAINT fk_detail_transaksi_transaksi FOREIGN KEY (kode_transaksi) REFERENCES transaksi(kode_transaksi) ON DELETE CASCADE ON UPDATE CASCADE,
        CONSTRAINT fk_detail_transaksi_barang FOREIGN KEY (kode_barang) REFERENCES barang(kode_barang) ON DELETE CASCADE ON UPDATE CASCADE
    )
    """
    cursor.execute(create_detail_transaksi_table_query)

    # Create analisis table if not exists
    create_analisis_table_query = """
    CREATE TABLE IF NOT EXISTS analisis (
        id_analisis INT AUTO_INCREMENT PRIMARY KEY,
        waktu_pembuatan DATETIME DEFAULT NOW()
    )
    """
    cursor.execute(create_analisis_table_query)

    # Create aturan asosiasi table if not exists
    create_aturan_asosiasi_table_query = """
    CREATE TABLE IF NOT EXISTS aturan_asosiasi (
        id_rules INT AUTO_INCREMENT PRIMARY KEY,
        id_analisis INT NOT NULL,
        support FLOAT NOT NULL,
        confidence FLOAT NOT NULL,
        lift_ratio FLOAT NOT NULL,
        CONSTRAINT fk_id_analisis FOREIGN KEY (id_analisis) REFERENCES analisis(id_analisis) ON DELETE CASCADE ON UPDATE CASCADE
    )
    """
    cursor.execute(create_aturan_asosiasi_table_query)

    # Create itemset table if not exists
    create_itemset_table_query = """
    CREATE TABLE IF NOT EXISTS itemset (
        id_itemset INT AUTO_INCREMENT PRIMARY KEY,
        kode_barang VARCHAR(50) NOT NULL,
        kategori ENUM('antecedents','consequents') NOT NULL,
        CONSTRAINT fk_itemset_barang FOREIGN KEY (kode_barang) REFERENCES barang(kode_barang) ON DELETE CASCADE ON UPDATE CASCADE
    )
    """
    cursor.execute(create_itemset_table_query)

    # Create rule items table if not exists
    create_rule_items_table_query = """
    CREATE TABLE IF NOT EXISTS rule_items (
        id_rules INT NOT NULL,
        id_itemset INT NOT NULL,
        PRIMARY KEY(id_rules, id_itemset),
        CONSTRAINT fk_id_rules FOREIGN KEY (id_rules) REFERENCES aturan_asosiasi(id_rules) ON DELETE CASCADE ON UPDATE CASCADE,
        CONSTRAINT fk_id_itemset FOREIGN KEY (id_itemset) REFERENCES itemset(id_itemset) ON DELETE CASCADE ON UPDATE CASCADE
    )
    """
    cursor.execute(create_rule_items_table_query)

    cursor.close()
    conn.close()
    # print("Database initialized successfully!")


# Function to Search and Paginate Results
def get_barang(
    search_keyword="", order_by="kode_barang", desc=False, offset=0, limit=10
):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)  # Dictionary cursor for JSON-like output

    # SQL Query
    query = f"""
    SELECT SQL_CALC_FOUND_ROWS * 
    FROM barang 
    WHERE kode_barang LIKE %s OR nama_barang LIKE %s
    ORDER BY {order_by} {'DESC' if desc else 'ASC'}
    LIMIT %s, %s;
    """

    # Execute Query
    cursor.execute(query, (f"%{search_keyword}%", f"%{search_keyword}%", offset, limit))
    results = cursor.fetchall()

    # Get Total Count
    cursor.execute("SELECT FOUND_ROWS();")
    total_count = cursor.fetchone()["FOUND_ROWS()"]

    cursor.close()
    conn.close()

    return {"total_count": total_count, "data": results}


# Function to get single barang using id
def get_barang_by_id(kode_barang):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)  # Dictionary cursor for JSON-like output

    # SQL Query
    query = f"""
    SELECT SQL_CALC_FOUND_ROWS * 
    FROM barang 
    WHERE kode_barang = {kode_barang}
    """

    # Execute Query
    cursor.execute(query)
    results = cursor.fetchall()

    # Get Total Count
    cursor.execute("SELECT FOUND_ROWS();")
    total_count = cursor.fetchone()["FOUND_ROWS()"]

    cursor.close()
    conn.close()

    return {"total_count": total_count, "data": results}


# Function to Search and Paginate Results
def get_transaksi(
    search_keyword="", order_by="kode_transaksi", desc=False, offset=0, limit=10
):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)  # Dictionary cursor for JSON-like output

    # SQL Query
    query = f"""
    SELECT dt.id, 
        dt.kode_transaksi, 
        t.tanggal_transaksi, 
        dt.kode_barang, 
        b.nama_barang, 
        dt.jumlah, 
        dt.total_harga 
    FROM detail_transaksi dt 
    JOIN transaksi t ON dt.kode_transaksi = t.kode_transaksi
    JOIN barang b ON dt.kode_barang = b.kode_barang
    WHERE dt.kode_transaksi LIKE %s 
       OR dt.kode_barang LIKE %s 
       OR b.nama_barang LIKE %s
    ORDER BY {order_by} {'DESC' if desc else 'ASC'}
    LIMIT %s, %s;
    """

    # Execute Query
    cursor.execute(
        query,
        (
            f"%{search_keyword}%",
            f"%{search_keyword}%",
            f"%{search_keyword}%",
            offset,
            limit,
        ),
    )
    results = cursor.fetchall()

    # Get Total Count
    cursor.execute("SELECT FOUND_ROWS();")
    total_count = cursor.fetchone()["FOUND_ROWS()"]

    cursor.close()
    conn.close()

    return {"total_count": total_count, "data": results}


# Get table row count
def get_row_count(table_name):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)  # Dictionary cursor for JSON-like output
    query = f"""
    SELECT COUNT(*) AS total_count FROM {table_name};
    """
    cursor.execute(query)
    results = cursor.fetchone()
    cursor.close()
    conn.close()
    return results


# Get top barang by jumlah terjual in detail_transaksi
def get_top_barang(limit=5):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)  # Dictionary cursor for JSON-like output

    query = f"""
    SELECT 
    b.kode_barang, 
    b.nama_barang, 
    COALESCE(SUM(dt.jumlah), 0) AS total_terjual
    FROM barang b
    LEFT JOIN detail_transaksi dt ON b.kode_barang = dt.kode_barang
    GROUP BY b.kode_barang, b.nama_barang
    ORDER BY total_terjual DESC
    LIMIT {limit};
    """

    cursor.execute(query)
    results = cursor.fetchall()

    # Get Total Count
    cursor.execute("SELECT FOUND_ROWS();")
    total_count = cursor.fetchone()["FOUND_ROWS()"]

    cursor.close()
    conn.close()

    return {"total_count": total_count, "data": results}


# Update data barang
def update_barang(kode_lama=None, kode_barang=None, barcode=None, nama_barang=None):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Building dynamic SET clause
    updates = []
    params = []

    if kode_barang is not None:
        updates.append("kode_barang = %s")
        params.append(kode_barang)

    if barcode is not None:
        updates.append("barcode = %s")
        params.append(barcode)

    if nama_barang is not None:
        updates.append("nama_barang = %s")
        params.append(nama_barang)

    # If no valid updates, return early
    if not updates:
        # print("No valid fields to update!")
        return False

    # Add kode_barang for WHERE clause
    params.append(kode_lama)

    # SQL Query
    query = f"""
    UPDATE barang 
    SET {', '.join(updates)}
    WHERE kode_barang = %s;
    """

    # Execute Query
    cursor.execute(query, tuple(params))
    conn.commit()

    # Check if row was updated
    success = cursor.rowcount > 0
    cursor.close()
    conn.close()
    return success


# Delete barang
def delete_barang(kode_barang):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Delete barang (with ON DELETE CASCADE, no need to check detail_transaksi)
    cursor.execute("DELETE FROM barang WHERE kode_barang = %s", (kode_barang,))
    conn.commit()

    success = cursor.rowcount > 0
    cursor.close()
    conn.close()
    return success


# get detail transaksi join transaksi join barang
def get_detail_transaksi(
    # search_by_transaction_code=None,
    search_keyword=None,
    from_start_date=None,
    to_end_date=None,
    order_by=None,
    desc=False,
    offset=0,
    limit=10,
    where_id=None,
):
    conn = get_db_connection()
    if not conn:
        return
    cursor = conn.cursor(dictionary=True)

    # Base SQL query with JOINs and SQL_CALC_FOUND_ROWS to get the total count.
    query = """
        SELECT SQL_CALC_FOUND_ROWS
            dt.id,
            dt.jumlah,
            t.kode_transaksi,
            t.tanggal_transaksi,
            b.kode_barang,
            b.nama_barang
        FROM detail_transaksi dt
        JOIN transaksi t ON dt.kode_transaksi = t.kode_transaksi
        JOIN barang b ON dt.kode_barang = b.kode_barang
        
    """
    params = []
    if search_keyword:
        query += " AND t.kode_transaksi LIKE %s OR b.nama_barang LIKE %s"
        params.append(f"%{search_keyword}%")
        params.append(f"%{search_keyword}%")
    if from_start_date:
        query += " AND t.tanggal_transaksi >= %s"
        params.append(from_start_date)
    if to_end_date:
        query += " AND t.tanggal_transaksi <= %s"
        params.append(to_end_date)
    if where_id:
        query += f"WHERE dt.id = {where_id}"

    if order_by == "kode_transaksi":
        order_column = "t.kode_transaksi"
    elif order_by == "nama_barang":
        order_column = "b.nama_barang"
    elif order_by == "jumlah":
        order_column = "dt.jumlah"
    else:
        order_column = "t.tanggal_transaksi"
    order_direction = "DESC" if desc else "ASC"
    query += f" ORDER BY {order_column} {order_direction}"

    # Apply LIMIT clause if limit is provided
    if limit:
        query += " LIMIT %s, %s"
        params.append(offset)
        params.append(limit)

    # Debug: Uncomment to print the final query and parameters
    print("Final Query:", query)
    print("Params:", params)

    # Execute the query
    cursor.execute(query, tuple(params))
    results = cursor.fetchall()

    # Get the total number of matching rows (ignoring LIMIT)
    cursor.execute("SELECT FOUND_ROWS() AS total_count")
    total_count = cursor.fetchone()["total_count"]

    cursor.close()
    conn.close()

    return {"total_count": total_count, "data": results}


# Delete detail transaksi and or transaksi
def delete_detail_transaksi(id_detail, kode_transaksi):
    conn = get_db_connection()
    cursor = conn.cursor()
    success = False

    try:
        # Delete barang (with ON DELETE CASCADE, no need to check detail_transaksi)
        cursor.execute("DELETE FROM detail_transaksi WHERE id = %s", (id_detail,))
        conn.commit()

        success = cursor.rowcount > 0

        if not success:
            raise ValueError("Failed to delete detail_transaksi")

        cursor.execute(
            "SELECT * FROM detail_transaksi WHERE kode_transaksi = %s",
            (kode_transaksi,),
        )
        results = cursor.fetchall()
        # print(results)

        if len(results) < 1:
            cursor.execute(
                "DELETE FROM transaksi WHERE kode_transaksi = %s",
                (kode_transaksi,),
            )
            conn.commit()
            success = cursor.rowcount > 0
    except ValueError as ex:
        # print(ex)
        success = False
    except Exception as ex:
        # print(ex)
        success = False
    finally:
        cursor.close()
        conn.close()
        return success


# update detail transaksi
def update_detail_transaksi(id_detail, kode_barang, jumlah):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Building dynamic SET clause
    updates = []
    params = []

    if kode_barang is not None:
        updates.append("kode_barang = %s")
        params.append(kode_barang)

    if jumlah is not None:
        updates.append("jumlah = %s")
        params.append(jumlah)

    # If no valid updates, return early
    if not updates:
        # print("No valid fields to update!")
        return False

    # SQL Query
    query = f"""
    UPDATE detail_transaksi 
    SET {', '.join(updates)}
    WHERE id = {id_detail};
    """

    # Execute Query
    cursor.execute(query, tuple(params))
    conn.commit()

    # Check if row was updated
    success = cursor.rowcount > 0
    cursor.close()
    conn.close()
    return success


# Insert data barang
def insert_barang(items):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "INSERT IGNORE INTO barang (kode_barang, barcode, nama_barang) VALUES (%s, %s, %s)"
    cursor.executemany(query, items)
    conn.commit()

    # Check if row was inserted
    success = cursor.rowcount > 0
    cursor.close()
    conn.close()
    return success


# Insert data transaksi
def insert_transaksi(transactions):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "INSERT IGNORE INTO transaksi (kode_transaksi, tanggal_transaksi) VALUES (%s, %s)"
    cursor.executemany(query, transactions)
    conn.commit()

    # Check if row was inserted
    success = cursor.rowcount > 0
    cursor.close()
    conn.close()
    return success


# Insert data detail transaksi
def insert_detail_transaksi(detils):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "INSERT IGNORE INTO detail_transaksi (kode_transaksi, kode_barang, jumlah, harga, diskon, total_harga) VALUES (%s, %s, %s, %s, %s, %s)"
    cursor.executemany(query, detils)
    conn.commit()

    # Check if row was inserted
    success = cursor.rowcount > 0
    cursor.close()
    conn.close()
    return success


# Insert data analisis
def insert_analisis(time):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "INSERT IGNORE INTO analisis (waktu_pembuatan) VALUES (%s)"
    cursor.executemany(query, time)
    conn.commit()

    # Check if row was inserted
    last_row_id = cursor.lastrowid if cursor.rowcount > 0 else None
    cursor.close()
    conn.close()
    return last_row_id


# Insert data rules
def insert_aturan_asosiasi(rules):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "INSERT IGNORE INTO aturan_asosiasi (id_analisis, support, confidence, lift_ratio) VALUES (%s, %s, %s, %s)"
    cursor.executemany(query, rules)
    conn.commit()

    # Check if row was inserted
    saved_rules = None
    if cursor.rowcount > 0:
        last_row_id = cursor.lastrowid
        row_count = cursor.rowcount
        cursor.execute(
            f"""
            SELECT id_rules FROM aturan_asosiasi 
            WHERE id_rules >= {last_row_id} AND id_rules <= {last_row_id + (row_count - 1)};
            """
        )
        saved_rules = cursor.fetchall()

    cursor.close()
    conn.close()
    return saved_rules


# Insert antecedents & consequents to itemset table
def insert_itemset(itemset):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "INSERT IGNORE INTO itemset (kode_barang, kategori) VALUES (%s, %s)"
    cursor.executemany(query, itemset)
    conn.commit()

    # Check if row was inserted
    itemsets = None
    if cursor.rowcount > 0:
        last_row_id = cursor.lastrowid
        row_count = cursor.rowcount
        cursor.execute(
            f"""
            SELECT id_itemset FROM itemset 
            WHERE id_itemset >= {last_row_id} AND id_itemset <= {last_row_id + (row_count - 1)};
            """
        )
        itemsets = cursor.fetchall()

    cursor.close()
    conn.close()
    return itemsets


# Insert rule items
def insert_rule_items(rule_items):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "INSERT IGNORE INTO rule_items (id_rules, id_itemset) VALUES (%s, %s)"
    cursor.executemany(query, rule_items)
    conn.commit()

    # Check if row was inserted
    success = cursor.rowcount > 0
    cursor.close()
    conn.close()
    return success


# get analisis
def get_analisis():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # SQL Query
    query = f"""
    SELECT SQL_CALC_FOUND_ROWS a.*, (SELECT COUNT(*) FROM aturan_asosiasi r WHERE r.id_analisis = a.id_analisis) AS rules_count
    FROM analisis a;
    """

    # Execute Query
    cursor.execute(query)
    results = cursor.fetchall()

    # Get Total Count
    cursor.execute("SELECT FOUND_ROWS();")
    total_count = cursor.fetchone()["FOUND_ROWS()"]

    cursor.close()
    conn.close()

    return {"total_count": total_count, "data": results}


def get_latest_analisis():
    conn = get_db_connection()
    cursor = conn.cursor()

    # SQL Query
    query = "SELECT id_analisis FROM analisis ORDER BY id_analisis LIMIT 1;"

    # Execute Query
    cursor.execute(query)
    results = cursor.fetchone()

    # Get Total Count
    # cursor.execute("SELECT FOUND_ROWS();")
    # total_count = cursor.fetchone()["FOUND_ROWS()"]

    cursor.close()
    conn.close()

    return results[0] if results else None


# Delete hasil analisis
def delete_analisis(id_analisis):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Delete barang (with ON DELETE CASCADE, no need to check detail_transaksi)
    cursor.execute("DELETE FROM analisis WHERE id_analisis = %s", (id_analisis,))
    conn.commit()

    success = cursor.rowcount > 0
    cursor.close()
    conn.close()
    return success


# Get aturan asosiasi where by id_analisis
def get_aturan_asosiasi(id_analisis):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # SQL Query
    query = f"""
    SELECT ar.id_rules, ar.support, ar.confidence, ar.lift_ratio, i.id_itemset, i.kategori, b.kode_barang, b.nama_barang
    FROM aturan_asosiasi ar
    JOIN rule_items ri ON ar.id_rules = ri.id_rules 
    JOIN itemset i ON i.id_itemset = ri.id_itemset 
    JOIN barang b on i.kode_barang = b.kode_barang
    WHERE ar.id_analisis = {id_analisis};
    """

    # Execute Query
    cursor.execute(query)
    results = cursor.fetchall()

    # Get Total Count
    cursor.execute("SELECT FOUND_ROWS();")
    total_count = cursor.fetchone()["FOUND_ROWS()"]

    cursor.close()
    conn.close()

    return {"total_count": total_count, "data": results}
