from django.shortcuts import render, redirect
from django.db import connection


# ini buat liatin semua lokasi
def daftar_lokasi_view(request):
    query = """
	SELECT *
	FROM LOKASI
    ORDER BY CAST(id AS integer);
	"""
    cursor = connection.cursor()
    cursor.execute("SET search_path TO SIDIA;")
    cursor.execute(query)

    data_lokasi = fetch(cursor)

    return render(request, 'listlokasi.html', {'data_lokasi':data_lokasi})

# converts sql rows to a dict
def fetch(cursor):
	columns = [col[0] for col in cursor.description]
	return [dict(zip(columns, row)) for row in cursor.fetchall()]
    # return cursor.fetchall()


def form_buat_lokasi_view(request):
    query = """
	SELECT provinsi
	FROM LOKASI;
	"""
    cursor = connection.cursor()
    cursor.execute("SET search_path TO SIDIA;")
    cursor.execute(query)

    data_provinsi = fetch(cursor)
    return render(request, 'createlokasi.html', {'data_provinsi':data_provinsi})



def buat_lokasi(request):
    lokasi = {
            "id-lokasi" : get_id_lokasi(),
            "lokasi-provinsi" : request.POST.get('lokasi-provinsi'),
            "lokasi-kabkot" : request.POST.get('lokasi-kabkot'),
            "lokasi-kecamatan" : request.POST.get('lokasi-kecamatan'),
            "lokasi-kelurahan" : request.POST.get('lokasi-kelurahan'),
            "jalan-no" : request.POST.get('jalan-no')
    }

    query =  """
    INSERT INTO LOKASI (id, provinsi, kabkot, kecamatan, kelurahan, jalan_no)
    VALUES ('%s', '%s', '%s', '%s', '%s', '%s');
    """ %(lokasi['id-lokasi'], lokasi['lokasi-provinsi'], lokasi['lokasi-kabkot'], lokasi['lokasi-kecamatan'], lokasi['lokasi-kelurahan'], lokasi['jalan-no'])
    
    cursor = connection.cursor()
    cursor.execute("SET search_path TO SIDIA;")
    cursor.execute(query)
    
    return redirect('crulokasi:daftarlokasi')


def get_id_lokasi():
    query = """
    SELECT MAX(CAST(id AS integer))+1
    FROM LOKASI;
	"""
    cursor = connection.cursor()
    cursor.execute("SET search_path TO SIDIA;")
    cursor.execute(query)

    id_lokasi_baru = int(cursor.fetchone()[0])
    return id_lokasi_baru


def get_as_dict(cursor):
    columns = [column[0] for column in cursor.description]
    results = []
    for row in cursor.fetchall():
        results.append(dict(zip(columns, row)))
    return results


def update_lokasi(request, id):
    lokasi = {
            "id-lokasi" : request.POST.get('u-id-lokasi'),
            "lokasi-provinsi" : request.POST.get('u-lokasi-provinsi'),
            "lokasi-kabkot" : request.POST.get('u-lokasi-kabkot'),
            "lokasi-kecamatan" : request.POST.get('u-lokasi-kecamatan'),
            "lokasi-kelurahan" : request.POST.get('u-lokasi-kelurahan'),
            "jalan-no" : request.POST.get('u-jalan-no')
    }
   
    query = """
    UPDATE LOKASI
    SET provinsi='%s', kabkot='%s', kecamatan='%s', kelurahan='%s', jalan_no='%s'
    WHERE id = '%s';
    """%(lokasi['lokasi-provinsi'], lokasi['lokasi-kabkot'], lokasi['lokasi-kecamatan'], lokasi['lokasi-kelurahan'], lokasi['jalan-no'], id)

    cursor = connection.cursor()
    cursor.execute("SET search_path TO SIDIA;")
    cursor.execute(query)
    
    return redirect('crulokasi:daftarlokasi')


# def delete_lokasi(request, id):
#     query ="""
#     DELETE FROM LOKASI 
#     WHERE id = '%s';
#     """ %(id)
    
#     cursor = connection.cursor()
#     cursor.execute("SET search_path TO SIDIA;")
#     cursor.execute(query)

#     return redirect('crulokasi:daftarlokasi')
