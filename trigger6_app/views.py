from django.shortcuts import render, redirect
from django.db import connection
from django.db.utils import IntegrityError, InternalError
from django.contrib import messages

# Create your views here.
def tes(request):
    return render(request, 'create_stock_warehouse.html')

def create_stock_warehouse(request):
    context = {}
    if(request.method == "POST" and request.session.get('role', None) == "Admin Satgas"):
        lokasi = request.POST["id-lokasi"]
        item = request.POST["id-item-sumber-daya"]
        jumlah = request.POST["jumlah"]
        with connection.cursor() as cursor:
            try:
                cursor.execute(f"INSERT INTO STOK_WAREHOUSE_PROVINSI VALUES ('{lokasi}', '{item}', '{jumlah}');")
                return redirect("trigger6_app:read_stock_warehouse")
            except IntegrityError:
                messages.add_message(
                    request,
                    messages.WARNING,
                    "Data tidak bisa dibuat karena sudah ada. Silakan ulangi query Anda."
                )
                return redirect("trigger6_app:create_stock_warehouse")
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM LOKASI l NATURAL JOIN WAREHOUSE_PROVINSI wp WHERE wp.id_lokasi = l.id;")
        context['list_lokasi'] = [
            [id[0], id[1], id[2], id[3], id[4], id[5]] for count, id in enumerate(cursor.fetchall())
        ]
        
        cursor.execute("SELECT * FROM ITEM_SUMBER_DAYA;")
        context['list_item_sumber_daya'] = [
            [id[0], id[1], id[2], id[3], id[4], id[5]] for count, id in enumerate(cursor.fetchall())
        ]

    return render(request, 'create_stock_warehouse.html', context)

def read_stock_warehouse(request):
    context = {}
    with connection.cursor() as cursor:
        if(request.session.get('role', None) == "Admin Satgas"):
            cursor.execute("SELECT * FROM STOK_WAREHOUSE_PROVINSI;")
            context["data"] = cursor.fetchall()
        elif(request.session.get('role', None) == "Petugas Faskes"):
            username = request.session.get("username", None)
            cursor.execute(f"""SELECT *
                FROM STOK_WAREHOUSE_PROVINSI
                WHERE id_lokasi_warehouse IN (
                    SELECT id_lokasi
                    FROM FASKES f, LOKASI l
                    WHERE f.username_petugas = '{username}' AND f.id_lokasi = l.id
                );""")
            context["data"] = cursor.fetchall()

    print(context)
    return render(request, "read_stock_warehouse.html", context)

def update_stock_warehouse(request):
    context = {}
    id_lokasi = request.POST["id-lokasi"]
    kode_item = request.POST["kode-item"]
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT * FROM LOKASI WHERE id = '{id_lokasi}'")
        context["lokasi"] = cursor.fetchone()
        cursor.execute(f"SELECT * FROM ITEM_SUMBER_DAYA WHERE kode = '{kode_item}'")
        context["item"] = cursor.fetchone()
        print(context)
    return render(request, "update_stock_warehouse.html", context)

def update_stock_warehouse_2(request):
    id_lokasi = request.POST["lokasi-id"]
    kode_item = request.POST["kode-item"]
    jumlah = request.POST["jumlah"]
    with connection.cursor() as cursor:
        cursor.execute(f"""UPDATE STOK_WAREHOUSE_PROVINSI
            SET jumlah = {jumlah}
            WHERE id_lokasi_warehouse = '{id_lokasi}'
            AND kode_item_sumber_daya = '{kode_item}';""")
    return redirect("trigger6_app:read_stock_warehouse")

def delete_stock_warehouse(request):
    id_lokasi = request.POST["id-lokasi"]
    kode_item = request.POST["kode-item"]
    with connection.cursor() as cursor:
        cursor.execute(f"""DELETE FROM STOK_WAREHOUSE_PROVINSI
            WHERE id_lokasi_warehouse = '{id_lokasi}'
            AND kode_item_sumber_daya = '{kode_item}';""")
    return redirect("trigger6_app:read_stock_warehouse")

def batch_pengiriman(request):
    context = {}
    print(request.session["role"])
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT TSD.NOMOR, PSDF.USERNAME_PETUGAS_FASKES, F.KODE_FASKES_NASIONAL, TSD.TOTAL_BERAT, RSP.KODE_STATUS_PERMOHONAN, risp.kode_status_batch_pengiriman
            FROM PERMOHONAN_SUMBER_DAYA_FASKES PSDF
            JOIN TRANSAKSI_SUMBER_DAYA TSD ON PSDF.NO_TRANSAKSI_SUMBER_DAYA = TSD.NOMOR
            JOIN FASKES F ON F.USERNAME_PETUGAS = PSDF.USERNAME_PETUGAS_FASKES
            JOIN RIWAYAT_STATUS_PERMOHONAN RSP ON RSP.NOMOR_PERMOHONAN = PSDF.NO_TRANSAKSI_SUMBER_DAYA
            LEFT JOIN BATCH_PENGIRIMAN bp ON bp.nomor_transaksi_sumber_daya = tsd.nomor
            LEFT JOIN RIWAYAT_STATUS_PENGIRIMAN risp ON risp.kode_batch = bp.kode; 
        """)
        context["data_permohonan"] = cursor.fetchall()
    print(context)        
    return render(request, "batch_pengiriman.html", context)

def form_batch_pengiriman(request):
    print(request.POST)
    context = {}
    no_transaksi = request.POST["nomor-transaksi"]
    context["no_transaksi"] = no_transaksi
    context["petugas_faskes"] = request.POST["petugas-faskes"]

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT * FROM BATCH_PENGIRIMAN;
        """)
        kode_batch = "BTP" + str(len(cursor.fetchall()) + 1)
        context["kode_batch"] = kode_batch

        cursor.execute(f"""
            (SELECT * FROM KENDARAAN)
            EXCEPT
            (SELECT k.nomor, k.nama, k.jenis_kendaraan, k.berat_maksimum FROM KENDARAAN k
            JOIN BATCH_PENGIRIMAN bp ON bp.No_kendaraan = k.nomor
            JOIN RIWAYAT_STATUS_PENGIRIMAN risp ON risp.kode_batch = bp.kode
            WHERE risp.Kode_status_batch_pengiriman = 'PRO' OR risp.Kode_status_batch_pengiriman = 'OTW')
            EXCEPT
            (SELECT k.nomor, k.nama, k.jenis_kendaraan, k.berat_maksimum FROM KENDARAAN k
            JOIN BATCH_PENGIRIMAN bp ON bp.No_kendaraan = k.nomor
            WHERE nomor_transaksi_sumber_daya = {no_transaksi});
        """)
        context["kendaraan"] = cursor.fetchall()

        cursor.execute(f"""
            SELECT PENGGUNA.username, nama, no_sim
            FROM (
                (SELECT username, no_sim FROM PETUGAS_DISTRIBUSI)
                EXCEPT
                (SELECT pd.username, pd.no_sim FROM PETUGAS_DISTRIBUSI pd
                JOIN BATCH_PENGIRIMAN bp ON bp.Username_petugas_distribusi = pd.Username
                JOIN RIWAYAT_STATUS_PENGIRIMAN risp ON risp.kode_batch = bp.kode
                WHERE risp.Kode_status_batch_pengiriman = 'PRO' OR risp.Kode_status_batch_pengiriman = 'OTW')
                EXCEPT
                (SELECT pd.username, pd.no_sim FROM PETUGAS_DISTRIBUSI pd
                JOIN BATCH_PENGIRIMAN bp ON bp.Username_petugas_distribusi = pd.Username
                WHERE nomor_transaksi_sumber_daya = {no_transaksi})
                ) AS PETUGAS_DIST_SIAP_TAMPIL
            NATURAL JOIN PENGGUNA;
        """)
        context["petugas_distribusi"] = cursor.fetchall()

        cursor.execute(f"""
            SELECT kode, k.nama AS nama_kendaraan, p.nama AS nama_pengguna,
            string_agg(l.provinsi || ',' || l.kabkot || ',' || l.kecamatan || ',' || l.kelurahan || ',' || l.jalan_no, ', ') AS lokasi_asal_lengkap,
            string_agg(l2.provinsi || ',' || l2.kabkot || ',' || l2.kecamatan || ',' || l2.kelurahan || ',' || l2.jalan_no, ', ') AS lokasi_tiba_lengkap
            FROM BATCH_PENGIRIMAN bp JOIN LOKASI l
            ON bp.id_lokasi_asal = l.id
            JOIN LOKASI l2 ON bp.id_lokasi_tujuan = l2.id
            JOIN KENDARAAN k ON bp.no_kendaraan = k.nomor
            JOIN PENGGUNA p ON bp.username_petugas_distribusi = p.username
            WHERE bp.Nomor_transaksi_sumber_daya = {no_transaksi}
            GROUP BY kode, k.nama, p.nama;
        """)
        context["display_batch"] = cursor.fetchall()
    print(context)
    return render(request, "form_batch_pengiriman.html", context)

def create_batch_pengiriman(request):
    print(request.POST)
    kode_batch = request.POST["kode-batch"]
    username_satgas = request.POST["admin-satgas"]
    username_distribusi = request.POST["distribusi"]
    no_transaksi = request.POST["nomor-transaksi"]
    no_kendaraan = request.POST["plat"]

    with connection.cursor() as cursor:
        try:
            cursor.execute(f"""
                INSERT INTO BATCH_PENGIRIMAN 
                (Kode, Username_satgas, Username_petugas_distribusi, Tanda_terima, Nomor_transaksi_sumber_daya, No_Kendaraan)
                VALUES
                ('{kode_batch}', '{username_satgas}', '{username_distribusi}', 'Diterima', {no_transaksi}, '{no_kendaraan}');
            """)
        except InternalError:
            messages.add_message(request, messages.INFO, f"Batch pengiriman untuk permohonan sumber daya dengan nomor transaksi {no_transaksi} ini sudah cukup")
            return redirect("trigger6_app:batch_pengiriman")

    messages.add_message(request, messages.INFO, f"Penambahan sukses!")
    return redirect("trigger6_app:batch_pengiriman")

def read_batch_pengiriman(request):
    print(request.POST)
    context = {}
    no_transaksi = request.POST["nomor-transaksi"]
    context["no_transaksi"] = no_transaksi
    with connection.cursor() as cursor:
        if(request.session["role"] == "Admin Satgas" or request.session["role"] == "Petugas Faskes"):
            cursor.execute(f"""
                SELECT kode, k.nama AS nama_kendaraan, p.nama AS nama_pengguna,
                string_agg(l.provinsi || ',' || l.kabkot || ',' || l.kecamatan || ',' || l.kelurahan || ',' || l.jalan_no, ', ') AS lokasi_asal_lengkap,
                string_agg(l2.provinsi || ',' || l2.kabkot || ',' || l2.kecamatan || ',' || l2.kelurahan || ',' || l2.jalan_no, ', ') AS lokasi_tiba_lengkap
                FROM BATCH_PENGIRIMAN bp JOIN LOKASI l
                ON bp.id_lokasi_asal = l.id
                JOIN LOKASI l2 ON bp.id_lokasi_tujuan = l2.id
                JOIN KENDARAAN k ON bp.no_kendaraan = k.nomor
                JOIN PENGGUNA p ON bp.username_petugas_distribusi = p.username
                WHERE bp.Nomor_transaksi_sumber_daya = {no_transaksi}
                GROUP BY kode, k.nama, p.nama;
            """)
            context["data_batch"] = cursor.fetchall()
            if(request.session["role"] == "Admin Satgas"):
                admin_satgas = request.session["username"]
                cursor.execute(f"""
                    SELECT * FROM PENGGUNA NATURAL JOIN ADMIN_SATGAS WHERE username = '{admin_satgas}';
                """)
                context["admin_satgas"] = cursor.fetchall()
            if(request.session["role"] == "Petugas Faskes"):
                petugas_faskes = request.POST["petugas-faskes"]
                cursor.execute(f"""
                    SELECT * FROM PENGGUNA NATURAL JOIN PETUGAS_FASKES WHERE username = '{petugas_faskes}';
                """)
                context["petugas_faskes"] = cursor.fetchall()
        elif(request.session["role"] == "Petugas Distribusi"):
            username_distribusi = request.session["username"]
            print(username_distribusi)
            cursor.execute(f"""
                SELECT kode, k.nama AS nama_kendaraan, p.nama AS nama_pengguna,
                string_agg(l.provinsi || ',' || l.kabkot || ',' || l.kecamatan || ',' || l.kelurahan || ',' || l.jalan_no, ', ') AS lokasi_asal_lengkap,
                string_agg(l2.provinsi || ',' || l2.kabkot || ',' || l2.kecamatan || ',' || l2.kelurahan || ',' || l2.jalan_no, ', ') AS lokasi_tiba_lengkap
                FROM BATCH_PENGIRIMAN bp JOIN LOKASI l
                ON bp.id_lokasi_asal = l.id
                JOIN LOKASI l2 ON bp.id_lokasi_tujuan = l2.id
                JOIN KENDARAAN k ON bp.no_kendaraan = k.nomor
                JOIN PENGGUNA p ON bp.username_petugas_distribusi = p.username
                WHERE bp.Nomor_transaksi_sumber_daya = {no_transaksi}
                AND bp.username_petugas_distribusi = '{username_distribusi}'
                GROUP BY kode, k.nama, p.nama;
            """)
            context["data_batch"] = cursor.fetchall()
            cursor.execute(f"""
                SELECT * FROM PENGGUNA NATURAL JOIN PETUGAS_DISTRIBUSI WHERE username = '{username_distribusi}';
            """)
            context["petugas_distribusi"] = cursor.fetchall()
            
    print(context)
    return render(request, "read_batch_pengiriman.html", context)

def update_riwayat_status(request):
    print(request.POST)
    context = {}
    no_transaksi = request.POST["nomor-transaksi"]
    context["no_transaksi"] = request.POST["nomor-transaksi"]
    context["petugas_faskes"] = request.POST["petugas-faskes"]
    with connection.cursor() as cursor:
        cursor.execute(f"""
            SELECT * FROM RIWAYAT_STATUS_PENGIRIMAN WHERE kode_batch IN 
            (SELECT kode FROM BATCH_PENGIRIMAN WHERE Nomor_transaksi_sumber_daya = {no_transaksi});
        """)
        context["riwayat_status"] = cursor.fetchall()

    print(context)
    return render(request, "update_riwayat_status.html", context)

def update_riwayat_status_2(request):
    print(request.POST)
    status = request.POST["status"]
    no_transaksi = request.POST["nomor-transaksi"]
    with connection.cursor() as cursor:
        cursor.execute(f"""
            UPDATE RIWAYAT_STATUS_PENGIRIMAN SET Kode_status_batch_pengiriman = '{status}' AND tanggal = now()
            WHERE kode_batch IN 
            (SELECT kode FROM BATCH_PENGIRIMAN WHERE Nomor_transaksi_sumber_daya = {no_transaksi});
        """)
    return redirect("trigger6_app:batch_pengiriman")

def read_riwayat_status(request):
    print(request.POST)
    context = {}
    no_transaksi = request.POST["nomor-transaksi"]
    context["no_transaksi"] = no_transaksi
    with connection.cursor() as cursor:
        if(request.session["role"] == "Admin Satgas"):
            cursor.execute(f"""
                SELECT rsp.kode_status_batch_pengiriman, sbp.nama, bp.username_satgas, rsp.tanggal
                FROM RIWAYAT_STATUS_PENGIRIMAN rsp
                JOIN STATUS_BATCH_PENGIRIMAN sbp ON rsp.Kode_status_batch_pengiriman = sbp.kode
                JOIN BATCH_PENGIRIMAN bp ON bp.kode = rsp.kode_batch
                WHERE kode_batch IN 
                (SELECT kode FROM BATCH_PENGIRIMAN WHERE Nomor_transaksi_sumber_daya = {no_transaksi})
                ORDER BY tanggal DESC;
            """)
            context["riwayat_status"] = cursor.fetchall()
        elif(request.session["role"] == "Petugas Distribusi"):
            username = request.session["username"]
            cursor.execute(f"""
                SELECT rsp.kode_status_batch_pengiriman, sbp.nama, bp.username_satgas, rsp.tanggal
                FROM RIWAYAT_STATUS_PENGIRIMAN rsp
                JOIN STATUS_BATCH_PENGIRIMAN sbp ON rsp.Kode_status_batch_pengiriman = sbp.kode
                JOIN BATCH_PENGIRIMAN bp ON bp.kode = rsp.kode_batch
                WHERE kode_batch IN 
                (SELECT kode FROM BATCH_PENGIRIMAN WHERE Nomor_transaksi_sumber_daya = {no_transaksi})
                AND bp.username_petugas_distribusi = '{username}'
                ORDER BY tanggal DESC;
            """)
            context["riwayat_status"] = cursor.fetchall()
    print(context)
    return render(request, "read_riwayat_status.html", context)