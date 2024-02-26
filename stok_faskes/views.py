from django.shortcuts import render, redirect
from django.db import connection
import json

# 8c - get auto filled data
def getSF(request):
    if (request.session["role"] == "Admin Satgas"):
        if(request.method == "GET"):
            context = {}
            dataFaskes = []
            dataISD = []

            # get all faskes and item sumber daya, do filtering later in html
            with connection.cursor() as c:
                c.execute('''
                    SELECT f.kode_faskes_nasional, l.provinsi
                    FROM faskes f, lokasi l
                    WHERE f.id_lokasi = l.id
                ''')
                data = c.fetchall()
                for i in data:
                    faskes = "Faskes khusus provinsi " + i[1]
                    dataFaskes.append((i[0], faskes))
                context["dataFaskes"] = dataFaskes
                context["dataFaskesJSON"] = json.dumps(dataFaskes)

                c.execute('''
                    SELECT i.kode, i.nama, s.kode_faskes
                    FROM item_sumber_daya i, stok_faskes s
                    WHERE i.kode = s.kode_item_sumber_daya
                ''')
                data = c.fetchall()
                for i in data:
                    dataISD.append((i[0], i[1], i[2]))
                context["dataISD"] = dataISD
                context["dataISDJSON"] = json.dumps(dataISD)
            
            return render(request, 'createSF.html', context)

    else:
        return redirect('/')
    
# 8c - create to do updating
def createSF(request):
    if (request.session["role"] == "Admin Satgas"):
        if(request.method == 'POST'):
            context = {}
            data = request.POST
            kodeFaskes = data['kodeFaskes']
            kodeItem = data['kodeItem']
            jumlah = data['jumlah']

            with connection.cursor() as c:
                c.execute('''
                    UPDATE stok_faskes
                    SET jumlah = jumlah + {}
                    WHERE kode_faskes = '{}' AND kode_item_sumber_daya = '{}'
                '''.format(jumlah, kodeFaskes, kodeItem))
            
            return redirect('stok_faskes:read')
        
    else:
        return redirect('/')

# 8d - read the data on table
def read(request):
    context = {}
    data = []
     
    # read all stock information as Admin Satgas
    if(request.session["role"] == "Admin Satgas"):
        with connection.cursor() as c:
            c.execute('''
                SELECT sf.kode_faskes, sf.kode_item_sumber_daya, l.provinsi, isd.nama, sf.jumlah
                FROM stok_faskes sf, lokasi l, item_sumber_daya isd, faskes f
                WHERE sf.kode_faskes = f.kode_faskes_nasional 
                AND f.id_lokasi = l.id
                AND sf.kode_item_sumber_daya = isd.kode
            ''')
            data = c.fetchall()
        context["data"] = data
        context["dataJSON"] = json.dumps(data)
        context["role"] = request.session["role"]

        return render(request, 'readSF.html', context)
    
    # read stock data information as Petugas Faskes
    elif(request.session["role"] == "Petugas Faskes"):
        username = request.session["username"]
        with connection.cursor() as c:
            c.execute('''
                SELECT sf.kode_faskes, sf.kode_item_sumber_daya, l.provinsi, isd.nama, sf.jumlah
                FROM stok_faskes sf, lokasi l, item_sumber_daya isd, faskes f
                WHERE sf.kode_faskes = f.kode_faskes_nasional 
                AND f.id_lokasi = l.id
                AND sf.kode_item_sumber_daya = isd.kode
                AND f.username_petugas = '{}'
            '''.format(username))
            data = c.fetchall()
        context["data"] = data
        context["dataJSON"] = json.dumps(data)
        context["role"] = request.session["role"]

        return render(request, 'readSF.html', context)

    else:
        return render('/')

# 8e - get auto filled data in form
def getUpdate(request, id_faskes, id_item):
    if (request.session["role"] == "Admin Satgas"):
        if(request.method == "GET"):
            context = {}
            data = []

            with connection.cursor() as c:
                c.execute('''
                    SELECT * FROM stok_faskes
                    WHERE kode_faskes = '{}' AND kode_item_sumber_daya = '{}'
                '''.format(id_faskes, id_item))
                dataUtama = c.fetchall()
                for i in dataUtama:
                    data.append((i))

                c.execute('''
                    SELECT l.provinsi
                    FROM lokasi l, faskes f
                    WHERE l.id = f.id_lokasi
                    AND f.kode_faskes_nasional = '{}'
                '''.format(id_faskes))
                tempData = c.fetchone()
                dataFaskes = "Faskes khusus provinsi " + tempData[0]

                c.execute('''
                    SELECT nama
                    FROM item_sumber_daya
                    WHERE kode = '{}'
                '''.format(id_item))
                tempData = c.fetchone()
                dataItem = tempData[0]

            context["data"] = data
            context["dataFaskes"] = dataFaskes
            context["dataItem"] = dataItem
            
            return render(request, 'updateSF.html', context)
    else:
        return redirect('/')

# 8e - post new jumlah
def postUpdate(request, id_faskes, id_item):
    if (request.session["role"] == "Admin Satgas"):
        if(request.method == "POST"):
            context = {}
            data = []
            jumlah = request.POST['jumlah']

            with connection.cursor() as c:
                c.execute('''
                    UPDATE stok_faskes
                    SET jumlah = {}
                    WHERE kode_faskes = '{}'
                    AND kode_item_sumber_daya = '{}'
                '''.format(jumlah, id_faskes, id_item))

            return redirect('stok_faskes:read')
    
    else:
        return redirect('/')

# 8f - delete row from table
def delete(request, id_faskes, id_item):
    if (request.session["role"] == "Admin Satgas"):
        with connection.cursor() as c:
            c.execute('''
                DELETE FROM stok_faskes
                WHERE kode_faskes = '{}'
                AND kode_item_sumber_daya = '{}'
            '''.format(id_faskes, id_item))
        
        return render(request, 'readSF.html')
    else:
        return redirect('/')