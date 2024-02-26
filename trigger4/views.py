from django.shortcuts import render, redirect
from django.db.utils import IntegrityError
from django.db import connection



# # register
# def tambah(request):
#     if (request.method == "POST"):
#         return tambahKendaraan(request)
#     else:
#         return showKendaraan(request)
    

# def showKendaraan(request):
#     return render(request, 'listKendaraan.html')


# #nambah kendaraan
# def tambahKendaraan(request):
#     data = request.POST
    
#     nokendaraan = data['nokendaraan']
#     nama = data['nama']
#     jeniskendaraan = data['jeniskendaraan']
#     beratmaksimum = data['beratmaksimum']



#     try:
#         with connection.cursor() as c:
#             c.execute('''
#                 INSERT INTO KENDARAAN(nomor, nama, jenis_kendaraan, berat_maksimum)
#                 VALUES ('{}', '{}', '{}', '{}')
#             '''.format(nokendaraan, nama, jeniskendaraan, beratmaksimum))
#     except IntegrityError:
#         pass

#     return redirect('/listKendaraan')

# def tambah(request):
#     if (request.method == "POST"):
#         return tambahKendaraan(request)
#     else:
#         return list_kendaraan(request)
    
def tambahKendaraan(request):
    kendaraan = {
        "nokendaraan" : request.POST.get('nokendaraan'),
        "nama" : request.POST.get("nama"),
        "jeniskendaraan" : request.POST.get("jeniskendaraan"),
        "beratmaksimum" : request.POST.get("beratmaksimum")
    }

    query = """
    INSERT INTO KENDARAAN (nomor, nama, jenis_kendaraan, berat_maksimum)
    VALUES('%s', '%s', '%s', '%s');
    """ %(kendaraan['nokendaraan'], kendaraan['nama'], kendaraan['jeniskendaraan'], kendaraan['beratmaksimum'])

    cursor = connection.cursor()
    cursor.execute("SET search_path TO SIDIA;")
    cursor.execute(query)

    return redirect('trigger4:listKendaraan')

    
# converts sql rows to a dict
def fetch(cursor):
	columns = [col[0] for col in cursor.description]
	return [dict(zip(columns, row)) for row in cursor.fetchall()]
    # return cursor.fetchall()

def form_tambah_kendaraan(request):
    return render(request, 'tambahKendaraan.html')

def get_as_dict(cursor):
    columns = [column[0] for column in cursor.description]
    results = []
    for row in cursor.fetchall():
        results.append(dict(zip(columns, row)))
    return results

def list_kendaraan(request):
    query = """
    SELECT * 
    FROM KENDARAAN;
    """
    cursor = connection.cursor()
    cursor.execute("SET search_path TO SIDIA;")
    cursor.execute(query)

    data_kendaraan = fetch(cursor)

    return render(request, 'listKendaraan.html', {'data_kendaraan':data_kendaraan})


def update_kendaraan(request,id):
    kendaraan = {
        "no-kendaraan" : request.POST.get('u-nomor-kendaraan'),
        "nama-kendaraan" : request.POST.get("u-nama-kendaraan"),
        "jenis-kendaraan" : request.POST.get("u-jenis-kendaraan"),
        "berat-maksimum" : request.POST.get("u-berat-maksimum")
    }
    query = """
        UPDATE KENDARAAN
        SET nomor='%s', nama='%s', jenis_kendaraan='%s', berat_maksimum='%s'
        WHERE nomor = '%s' AND nomor IN (SELECT no_kendaraan
        FROM BATCH_PENGIRIMAN
        WHERE kode NOT IN(
        SELECT kode 
        FROM BATCH_PENGIRIMAN JOIN RIWAYAT_STATUS_PENGIRIMAN
        ON kode = kode_batch
        WHERE (kode_status_batch_pengiriman = 'PRO' OR kode = 'OTW')
        )
        )
        ;
    """ %(kendaraan['no-kendaraan'], kendaraan['nama-kendaraan'], kendaraan['jenis-kendaraan'], kendaraan['berat-maksimum'], id)
    
    cursor = connection.cursor()
    cursor.execute("SET search_path TO SIDIA;")
    cursor.execute(query)

    return redirect('trigger4:listKendaraan')



def delete_kendaraan(request, id):
    query ="""
    DELETE FROM KENDARAAN 
    WHERE nomor = '%s' AND nomor IN (SELECT no_kendaraan
        FROM BATCH_PENGIRIMAN B JOIN KENDARAAN K ON B.no_kendaraan = K.nomor
        WHERE kode NOT IN(
        SELECT kode 
        FROM BATCH_PENGIRIMAN JOIN RIWAYAT_STATUS_PENGIRIMAN
        ON kode = kode_batch
        WHERE (kode_status_batch_pengiriman = 'PRO' OR kode = 'OTW')
        )
        )
        ;
    """ %(id)
    
    cursor = connection.cursor()
    cursor.execute("SET search_path TO SIDIA;")
    cursor.execute(query)

    return redirect('trigger4:listKendaraan')
