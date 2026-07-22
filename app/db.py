import psycopg2
import pandas as pd
from app.config import (
    REDSHIFT_HOST, REDSHIFT_USER, REDSHIFT_PASSWORD, REDSHIFT_DB, REDSHIFT_PORT
)

def get_redshift_connection():
    return psycopg2.connect(
        host=REDSHIFT_HOST,
        dbname=REDSHIFT_DB,
        user=REDSHIFT_USER,
        password=REDSHIFT_PASSWORD,
        port=REDSHIFT_PORT
    )

def get_overdue_mechanics(uid_list=None):
    uid_filter = ""
    if uid_list and len(uid_list) > 0:
        uids_formatted = ', '.join([f"'{uid}'" for uid in uid_list])
        uid_filter = f"AND fep.mechanic_office_uid IN ({uids_formatted})"

    query = f"""
    select 
        fep.mechanic_office_uid,
        dm.mechanic_office_name,
        dm.cnpj,
        dm.contact_email,
        dm.address_street || ' ' || dm.address_number || ', ' || dm.address_city || ', ' || dm.address_state  as address,
        dm.address_postalcode as zip_code,
        count(*) as invoices,
        sum(amount) as overdue_amount
    from public_facts.ft_expected_payments fep 
    left join public_dimensions.dim_mechanics_v2 dm on fep.mechanic_office_uid = dm.mechanic_office_uid 
    where 
        true 
        AND DATE(fep.created_at) >= DATE('2023-07-30')
        AND fep.status NOT IN ('canceled', 'refunded', 'renegotiated')
        AND fep.status IN ('overdue', 'delinquent')
        AND fep.payment_model = 'pay_later'
        AND fep.credit_provider = 'MECANIZOU'
        --AND dm.type_of_user IN ('Mechanics BU', 'white_label', 'Multicanal')
        AND dm.mechanic_office_name NOT IN (
          'OFICINA MECANIZOU DIAMANTE',
          'Mecanizou Oficina')
        {uid_filter}
    group by 1,2,3,4,5,6
    order by 1
    """
    conn = get_redshift_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def get_mechanic_details(mechanic_office_uid):
    query = f"""
    select 
        fep.expected_payment_id,
        fep.due_date,
        fep.amount 
    from public_facts.ft_expected_payments fep 
    left join public_dimensions.dim_mechanics_v2 dm on fep.mechanic_office_uid = dm.mechanic_office_uid 
    where 
        true 
        AND DATE(fep.created_at) >= DATE('2023-07-30')
        AND fep.status NOT IN ('canceled', 'refunded', 'renegotiated')
        AND fep.status IN ('overdue', 'delinquent')
        AND fep.payment_model = 'pay_later'
        AND fep.credit_provider = 'MECANIZOU'
        AND dm.type_of_user IN ('Mechanics BU', 'white_label', 'Multicanal')
        AND dm.mechanic_office_name NOT IN (
          'OFICINA MECANIZOU DIAMANTE',
          'Mecanizou Oficina')
         and fep.mechanic_office_uid = '{mechanic_office_uid}'
    order by 2
    """
    conn = get_redshift_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    return df
