"""a postgres data store"""
import psycopg2


class Postgres:
    """a postgres destination"""

    def __init__(self, dbenv: dict):
        self.conn = None
        self.host = dbenv["host"]
        self.port = dbenv["port"]
        self.dbname = dbenv["dbname"]
        self.user = dbenv["user"]
        self.password = dbenv["password"]  # might be None

        if self.host is None:
            raise ValueError("host is required")
        if self.user is None:
            raise ValueError("user is required")
        if self.dbname is None:
            raise ValueError("dbname is required")

        self.verbose = False

    def open(self):
        """provide a database connection"""
        self.close()
        conn_str = (
            f"host={self.host} port={self.port} dbname={self.dbname} user={self.user}"
        )
        if self.password:
            conn_str += f" password={self.password}"
        self.conn = psycopg2.connect(conn_str)
        # self.conn.autocommit = True

    def close(self):
        """close the connection if it exists"""
        if self.conn:
            self.conn.commit()
            self.conn.close()
            self.conn = None

    def mk_insert_statement(self, visit):
        """make a SQL insert statement for the visit"""
        return f"""
        INSERT INTO visits (
            date, 
            district, 
            name, 
            gender, 
            age_group, 
            health_worker
        ) 
        VALUES (
            '{visit['date']}', 
            '{visit['district']}', 
            '{visit['name']}', 
            '{visit['gender']}', 
            '{visit['age_group']}', 
            {visit['health_worker']}
        )
        """

    def record_visit(self, visit):
        """record the visit"""
        cursor = self.conn.cursor()
        statement = self.mk_insert_statement(visit)
        if self.verbose:
            print(statement)
        cursor.execute(statement)
        cursor.close()

    def mk_create_table(self):
        """generate the CREATE TABLE statement"""
        return """
            CREATE TABLE IF NOT EXISTS public.visits
            (
                id serial primary key,
                date date NOT NULL,
                name character varying(50) COLLATE pg_catalog."default" NOT NULL,
                gender character varying(10) COLLATE pg_catalog."default" NOT NULL,
                district character varying(15) COLLATE pg_catalog."default" NOT NULL,
                age_group character varying(10) COLLATE pg_catalog."default" NOT NULL,
                health_worker smallint NOT NULL
            )
        """
