from django.http import request
from django.shortcuts import render, redirect
from django.db.utils import IntegrityError
from django.db import connection

# Create your views here.

# landing page
def land(request):
    return render(request, "landing.html")

#splitter fir creating warehouse
def trig5(request):
    if (request.method == 'POST'):
        return insertdb(request)
    else:
        return create(request)

# splitter for showing warehouses
def trig5forshow(request):
    if (request.method == 'POST'):
        return deletedb(request)
    else:
        return showwarehouse(request)

#splitter for creating faskes
def trig5fas(request):
    if (request.method == 'POST'):
        return insertfask(request)
    else:
        return formfask(request)

#splitter for showing daskes
def trig5fasshow(request):
    if (request.method == 'POST'):
        return actfask(request)
    else:
        return showfask(request)

#warehouse create form
def create(request):
    c = connection.cursor()
    c.execute("SET search_path TO sidia")
    c.execute("SELECT l.id, l.provinsi FROM lokasi l WHERE (l.id NOT IN (SELECT wp.id_lokasi FROM warehouse_provinsi wp)) ORDER BY l.provinsi ASC;")
    
    provs = fetch(c)

    return render(request, "createwares.html", {'provs':provs})

def insertdb(request):

    id_lokasi = request.POST.get('provinsi')

    try:
        c = connection.cursor()
        c.execute("SET search_path TO sidia")
        c.execute("INSERT INTO warehouse_provinsi VALUES ('%s');" %(id_lokasi))
    except IntegrityError:
        pass

    return redirect("/trig5/showwares/")

def showwarehouse(request):
    c = connection.cursor()
    c.execute("SET search_path TO sidia")
    c.execute('''SELECT l.id, l.provinsi, l.kabkot, l.kecamatan, l.kelurahan, l.jalan_no FROM lokasi l WHERE 
    (l.id IN (SELECT wp.id_lokasi FROM warehouse_provinsi wp)) ORDER BY l.provinsi ASC;''')

    wares = fetch(c)

    return render(request, "show-warehouse-pr.html", {'wares':wares})

def deletedb(request):

    aksi = request.POST.get('action')
    target = request.POST.get('id_loc')

    if (aksi == "delete"):
        try:
            c = connection.cursor()
            c.execute("SET search_path TO sidia")
            c.execute("DELETE FROM warehouse_provinsi WHERE id_lokasi = '%s'" %(target))
        except IntegrityError:
            pass
        return showwarehouse(request) 
    elif (aksi == "update"):
        return redirect('/trig5/updatewares')

# update warehouse forms
def updatewares(request, kode):
    if (request.method == 'POST'):
        return doupdatewares(request)
    else:
        return formupdatewares(request, kode)

def formupdatewares(request, kode):
    c = connection.cursor()
    c.execute("SET search_path TO sidia")

    # c.execute("SELECT l.id, l.provinsi FROM lokasi l WHERE (l.id IN (SELECT wp.id_lokasi FROM warehouse_provinsi wp)) ORDER BY l.provinsi ASC;")
    # targets = fetch(c)
    target = kode

    c.execute("select id, provinsi from lokasi where provinsi in ( select provinsi from lokasi where id = '%s' ) ORDER BY id ASC;" %(target))
    updates = fetch(c)

    return render(request, "updatewares.html", {'target':target, 'updates' : updates})

def doupdatewares(request):

    target = request.POST.get('target')
    update = request.POST.get('update')

    c = connection.cursor()
    c.execute("SET search_path TO sidia")
    c.execute('''UPDATE warehouse_provinsi SET id_lokasi = '%s' 
    WHERE id_lokasi = '%s' ''' %(update, target))

    return redirect('/trig5/showwares')

# faskes create form
def formfask(request):

    c = connection.cursor()
    c.execute("SET search_path TO sidia")

    c.execute("SELECT id, provinsi FROM lokasi")
    ids = fetch(c)

    c.execute("SELECT username FROM petugas_faskes")
    usernames = fetch(c)

    c.execute("SELECT kode FROM tipe_faskes")
    codes = fetch(c)

    return render(request, "createfaskes.html", {"ids" : ids, "usernames" : usernames, "codes" : codes})

def insertfask(request):

    kode_faskes_nasional = request.POST.get('kode_faskes_nasional')
    id_lokasi = request.POST.get('id_lokasi')
    username_petugas  = request.POST.get('username_petugas')
    kode_tipe_faskes  = request.POST.get('kode_tipe_faskes')

    try:
        c = connection.cursor()
        c.execute("SET search_path TO sidia")
        c.execute("INSERT INTO faskes VALUES ('%s', '%s', '%s', '%s');" %(kode_faskes_nasional, id_lokasi, username_petugas, kode_tipe_faskes))
    except IntegrityError:
        pass

    return redirect("/trig5/showfask/")

def showfask(request):
    c = connection.cursor()
    c.execute("SET search_path TO sidia")
    c.execute('''SELECT * FROM faskes f JOIN lokasi l ON f.id_lokasi = l.id;''')

    fasks = fetch(c)

    return render(request, "show-faskes.html", {"fasks" : fasks})

def actfask(request):

    aksi = request.POST.get('action')
    target = request.POST.get('kode_faskes_nasional')

    if (aksi == "delete"):
        try:
            c = connection.cursor()
            c.execute("SET search_path TO sidia")
            c.execute("DELETE FROM faskes WHERE kode_faskes_nasional = '%s'" %(target))
        except IntegrityError:
            print("integrity error")
            pass
        return showfask(request) 
    elif (aksi == "update"):
        return redirect('/trig5/updatefask')

# update faskes
def updatefask(request, kode):
    if (request.method == 'POST'):
        return doupdatefask(request)
    else:
        return formupdatefask(request, kode)

def formupdatefask(request, kode):

    c = connection.cursor()
    c.execute("SET search_path TO sidia")

    # c.execute("SELECT kode_faskes_nasional FROM faskes")
    # targets = fetch(c)

    target = kode

    c.execute("SELECT id, provinsi FROM lokasi")
    new_ids = fetch(c)

    c.execute("SELECT username FROM petugas_faskes")
    new_usernames = fetch(c)

    c.execute("SELECT kode FROM tipe_faskes")
    new_codes = fetch(c)

    return render(request, "updatefaskes.html", {"target":target , "ids" : new_ids, "usernames" : new_usernames, "codes" : new_codes})

def doupdatefask(request):

    kode_faskes_nasional = request.POST.get('target')
    id_lokasi = request.POST.get('id_lokasi')
    username_petugas  = request.POST.get('username_petugas')
    kode_tipe_faskes  = request.POST.get('kode_tipe_faskes')

    try:
        c = connection.cursor()
        c.execute("SET search_path TO sidia")
        c.execute('''UPDATE faskes SET 
            id_lokasi = '%s',
            username_petugas = '%s',
            kode_tipe_faskes = '%s'
            WHERE kode_faskes_nasional = '%s';''' %(id_lokasi, username_petugas, kode_tipe_faskes, kode_faskes_nasional))
    except IntegrityError:
        pass

    return redirect('/trig5/showfask/')

# dictionary-fier
def fetch(cursor):
	columns = [col[0] for col in cursor.description]
	return [dict(zip(columns, row)) for row in cursor.fetchall()]
