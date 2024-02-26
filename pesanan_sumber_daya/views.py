from django.shortcuts import render, redirect
from django.db import connection
from datetime import datetime
import json

# 6c - create to get auto filled data
def getPSD(request):
    if(request.session["role"] == "Admin Satgas"):
        if(request.method == 'GET'):
            context = {}
            
            # get Nomor transaksi
            currentId = 0
            with connection.cursor() as c:
                c.execute("SELECT * FROM transaksi_sumber_daya")
                transaksi = c.fetchall()
                for t in transaksi:
                    if (t[0] > currentId):
                        currentId = t[0]
            currentId += 1

            # get Supplier
            suppliers = []
            with connection.cursor() as c :
                c.execute("SELECT * FROM supplier")
                suppliers = c.fetchall()

            # get Item Sumber Daya
            items = []
            with connection.cursor() as c :
                c.execute("SELECT * FROM item_sumber_daya")
                tempData = c.fetchall()
            for i in tempData:
                items.append(list(i))

            # return
            context = {
                'noTransaksi' : currentId,
                'suppliers' : suppliers,
                'items' : items
            }

            return render(request, 'createPSD.html', context)
    else:
        return redirect('/')

# 6c - create logic to insert
def createPSD(request):
    if(request.session["role"] == "Admin Satgas"):
        if (request.method == 'POST'):
            
            # get all data to do insert to database
            data = request.POST
            nomorTransaksi = data['nomorTransaksi']
            petugas = request.session['username']
            supplier = data['supplier']
            items = json.loads(data['datas'])
            tanggal = datetime.today().strftime('%Y-%m-%d')
            noUrut = data['noUrut']
            jumlahItem = data['jumlahItem']
            kodeISD = data['kodeISD']

            # inserting section
            with connection.cursor() as c:
                c.execute('''
                    INSERT INTO transaksi_sumber_daya(nomor, tanggal, total_berat, total_item)
                    VALUES ({}, '{}', {}, {})
                '''.format(nomorTransaksi, tanggal, 0, 0))

                c.execute('''
                    INSERT INTO pesanan_sumber_daya(nomor_pesanan, username_admin_satgas, total_harga)
                    VALUES ({}, '{}', {})
                '''.format(nomorTransaksi, petugas, 0))

                c.execute('''
                    INSERT INTO riwayat_status_pesanan(kode_status_pesanan, no_pesanan, username_supplier, tanggal)
                    VALUES ('{}', {}, '{}', '{}')
                '''.format('REQ-SUP', nomorTransaksi, supplier, tanggal))

                for i in items :
                    c.execute('''
                    INSERT INTO daftar_item(nomor_transaksi_sumber_daya, no_urut, jumlah_item, kode_item_sumber_daya)
                    VALUES ({}, {}, {}, '{}')
                    '''.format(nomorTransaksi, noUrut, jumlahItem, kodeISD))

            return redirect('pesanan_sumber_daya:read')
    else:
        return redirect('/')

#6d - read the data on table
def read(request):
    context = {}
    role = request.session['role']
    username = request.session['username']
    
    if(role == ''):
        return redirect('/')
    else:
        if(role == 'Admin Satgas'):
            with connection.cursor() as c:
                c.execute('''
                    SELECT *
                    FROM pesanan_sumber_daya psd
                    LEFT JOIN transaksi_sumber_daya tsd
                    ON psd.nomor_pesanan = tsd.nomor
                    WHERE psd.username_admin_satgas = '{}'
                '''.format(username))
                pesananAdmin = c.fetchall()
            data = []
            for i in pesananAdmin:
                status = None
                with connection.cursor() as c:
                    c.execute('''
                        SELECT kode_status_pesanan
                        FROM riwayat_status_pesanan
                        WHERE no_pesanan = {}
                    '''.format(i[0]))
                    status = c.fetchone()
                    print(status)
                tempPesananAdmin = list(i)
                tempPesananAdmin.extend(status)
                data.append(tempPesananAdmin)
            context['pesanan'] = data
            return render(request, 'readPSD.html', context)

        elif(role == 'Supplier'):
            with connection.cursor() as c:
                c.execute('''
                    SELECT DISTINCT psd.*, tsd.*
                    FROM riwayat_status_pesanan rsp
                    LEFT JOIN pesanan_sumber_daya psd
                    ON rsp.no_pesanan = psd.nomor_pesanan
                    LEFT JOIN transaksi_sumber_daya tsd
                    ON psd.nomor_pesanan = tsd.nomor
                    WHERE rsp.username_supplier = '{}'
                '''.format(username))
                pesananSupplier = c.fetchall()
            data = []
            for i in pesananSupplier:
                status = None
                with connection.cursor() as c:
                    c.execute('''
                        SELECT kode_status_pesanan
                        FROM riwayat_status_pesanan
                        WHERE no_pesanan = {}
                    '''.format(pesanan[0]))
                    status = c.fetchall()
                tempPesananSupplier = list(i)
                tempPesananSupplier.extend(status)
                data.append(tempPesananSupplier)
            context['pesanan'] = data
            return render(request, 'readPSD.html', context)

        return render(request, 'readPSD.html', context)

# 6d - detail
def detail(request, id):
    context = {}
    with connection.cursor() as c:
        c.execute('''
            SELECT *
            FROM pesanan_sumber_daya psd
            LEFT JOIN transaksi_sumber_daya tsd
            ON psd.nomor_pesanan = tsd.nomor
            LEFT JOIN daftar_item di
            ON di.nomor_transaksi_sumber_daya = tsd.nomor
            LEFT JOIN item_sumber_daya isd
            ON isd.kode = di.kode_item_sumber_daya
            WHERE tsd.nomor = {}
        '''.format(int(id)))
        context['pesanan'] = c.fetchall()
    return render(request, 'detailPSD.html', context)

# 6e - get auto filled data for update
def getUpdate(request, id):
    if(request.method == 'GET'):
        context = {}
        with connection.cursor() as c:
            c.execute('''
                SELECT *
                FROM pesanan_sumber_daya psd
                LEFT JOIN transaksi_sumber_daya tsd
                ON psd.nomor_pesanan = tsd.nomor
                LEFT JOIN daftar_item di
                ON di.nomor_transaksi_sumber_daya = tsd.nomor
                LEFT JOIN item_sumber_daya isd
                ON isd.kode = di.kode_item_sumber_daya
                WHERE tsd.nomor = {}
            '''.format(int(id)))
            context['pesanan'] = c.fetchall()

            c.execute('''
                SELECT no_urut
                FROM daftar_item
                WHERE nomor_transaksi_sumber_daya = {}
            '''.format(int(id)))
            tempId = 0
            for i in c.fetchall():
                if(i[0] > tempId):
                    tempId = i[0]
            context['noUrutNext'] = tempId + 1

            c.execute('''
                SELECT kode_item_sumber_daya
                FROM daftar_item
                WHERE nomor_transaksi_sumber_daya = {}
            '''.format(int(id)))
            tempKode = []
            for i in c.fetchall():
                tempKode.append(list(i))
            context['kodeISD'] = tempKode
            
            c.execute('''
                SELECT *
                FROM daftar_item
                WHERE nomor_transaksi_sumber_daya = {}
            '''.format(int(id)))
            tempData = []
            for i in c.fetchall():
                tempData.append(list(i))
            context['items'] = tempData

            c.execute('''
                SELECT *
                FROM item_sumber_daya
            ''')
            tempAllData = []
            for i in c.fetchall():
                tempAllData.append(list(i))
            context['allItems'] = tempAllData
        
        return render(request, 'updatePSD.html', context)

# 6e - updating the data (the script isn't implemented yet)
def postUpdate(request, id):
    data = request.POST
    items = json.loads(data['datas'])
    with connection.cursor() as c:
        c.execute('''
            DELETE FROM daftar_item
            WHERE nomor_transaksi_sumber_daya = {}
        '''.format(int(id)))

        # for i in items:
        # insert query here

    return render(request, 'updatePSD.html')

# 6f - delete data
def delete(request, id):
    with connection.cursor() as c:
        c.execute('''
            DELETE FROM riwayat_status_pesanan
            WHERE no_pesanan = {}
        '''.format(int(id)))

        c.execute('''
            DELETE FROM daftar_item
            WHERE nomor_transaksi_sumber_daya = {}
        '''.format(int(id)))

        c.execute('''
            DELETE FROM pesanan_sumber_daya
            WHERE nomor_pesanan = {}
        '''.format(int(id)))

        c.execute('''
            DELETE FROM transaksi_sumber_daya
            WHERE nomor = {}
        '''.format(int(id)))
    
    return render(request, 'readPSD.html')

# 7c - change status
def postStatus(request, id):
    print("posted")
    username = request.session['username']
    print(request.POST)
    tempStatus = request.POST['status']
    date = datetime.today().strftime('%Y-%m-%d')

    with connection.cursor() as c:
        c.execute('''
            UPDATE riwayat_status_pesanan
            SET kode_status_pesanan = '{}'
            WHERE no_pesanan = {}
            AND username_supplier = '{}'
            AND tanggal = '{}'
        '''.format(tempStatus, int(id), username, date))
    
    return render(request, 'readPSD.html')

# 7d - read status
def getStatus(request, id):
    context = {}
    with connection.cursor() as c:
        c.execute('''
            SELECT * FROM riwayat_status_pesanan rsp
            LEFT JOIN status_pesanan sp
            ON rsp.kode_status_pesanan = sp.kode
            WHERE no_pesanan = {}
        '''.format(int(id)))
        dataTemp = []
        for i in c.fetchall():
            dataTemp.append(list(i))
        context['status2'] = dataTemp
        print(context['status2'])
        context['id'] = id
    
    return render(request, 'statusPSD.html', context)