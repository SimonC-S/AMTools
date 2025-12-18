import psycopg2
import pandas as pd
from datetime import datetime
from icecream import ic

CSV_SUFFIX = '.csv'
CONNECT_ERROR = 'Unable to connect to the database'
CSV_CREATION_ERROR = 'Creating csv failed, check if it is in use'
NOT_A_DATE="Not a valid release date could not retrieve any jobs"
ODOO_MATERIAL_IDS=["0033-0491-077"]

def odoo_import(material_id:iter=ODOO_MATERIAL_IDS)->list: 
	"""import """

	id_tuple = tuple(material_id)

	# Generate placeholders for each item in the list
	placeholders = ','.join(['%s'] * len(material_id))
	# Establish a connection to the database
	try:
		conn = psycopg2.connect(
			dbname='Medifab',
			user='medifab',
			password='iBGokEXYUzzR62pvYZWrgtkC',
			host='192.168.0.5',
			port='5432'
		)
	except psycopg2.Error as e:
		print(CONNECT_ERROR)
		print(e)

	# Create a cursor object
	cur = conn.cursor()

	# SQL Query
#//pp.default_code AS "Product Variant/Internal Reference"
#	//, pt.default_code AS "Product Template/Internal Reference"
	query = f"""
	SELECT
	
	COALESCE(pt.name->>'en_US', pt.name->>'en_AU') AS "Odoo Name"
	, ps.product_code AS "Vendor Code"
	, uom.name->>'en_US' AS "UOM"
	, rp.complete_name  AS "Vendor Name"

	FROM
	product_product pp
	JOIN product_template pt ON
	pt.id = pp.product_tmpl_id
	LEFT JOIN product_supplierinfo ps ON
	ps.product_id = pp.id
	OR ps.product_tmpl_id = pt.id
	LEFT JOIN uom_uom uom ON
	uom.id = pt.uom_id
	LEFT JOIN res_partner rp ON
	rp.id = ps.partner_id

	WHERE pt.default_code IN ({placeholders});
	
	"""

	# Execute the query
	cur.execute(query, id_tuple)
	# Fetch all the rows
	rows = cur.fetchall()
	headers=([desc[0] for desc in cur.description])
	#rows=[r[0]for r in rows]
	# convert rows to list
	#print(rows)

	cur.close()
	conn.close()
	dict_rows=[{headers[i]:data for i,data in enumerate(r)} for r in rows]
	
	#c(dict_rows)
	return rows


ic(odoo_import(["0033-0491-090"]))