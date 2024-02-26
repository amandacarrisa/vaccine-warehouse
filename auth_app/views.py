from django.shortcuts import render, redirect
from django.db.utils import IntegrityError
from django.db import connection

# login
def login(request):
    if (request.method == 'POST'):
        return loginUser(request)
    else:
        return showLogin(request)

# login page
def showLogin(request):
    return render(request, 'login.html')

# login logic
def loginUser(request):
    username = request.POST['username']
    password = request.POST['password']
    role = None
    try:
        with connection.cursor() as c:
            c.execute('''
                SELECT * FROM pengguna WHERE username = '{}' AND password = '{}'
            '''.format(username, password))
            data_user = c.fetchone()
            print(data_user)
            if (data_user != None):
                c.execute(f"SELECT * FROM admin_satgas WHERE username = '{username}'")
                admin = c.fetchone()
                c.execute(f"SELECT * FROM petugas_faskes WHERE username = '{username}'")
                faskes = c.fetchone()
                c.execute(f"SELECT * FROM supplier WHERE username = '{username}'")
                supplier = c.fetchone()
                c.execute(f"SELECT * FROM petugas_distribusi WHERE username = '{username}'")
                distribusi = c.fetchone()

                if (admin):
                    role = 'Admin Satgas'
                elif (faskes):
                    role = 'Petugas Faskes'
                elif (supplier):
                    role = 'Supplier'
                elif (distribusi):
                    role = 'Petugas Distribusi'

                request.session['username'] = username
                request.session['role'] = role
                
                return redirect('/')
    except:
        pass

    return render(request, 'login.html')

# register
def register(request):
    if (request.method == "POST"):
        return registerUser(request)
    else:
        return showRegister(request)
    
# register page
def showRegister(request):
    return render(request, 'register.html')

# register logic
def registerUser(request):
    data = request.POST
    tipe = data['tipe']
    username = data['username']
    password = data['password']
    fullname = data['fullname']
    kelurahan = data['alamat-kelurahan']
    kecamatan = data['alamat-kecamatan']
    kabupaten = data['alamat-kabupaten']
    provinsi = data['alamat-provinsi']
    notelp = data['no-telp']
    organisasi = data['organisasi']
    nosim = data['no-sim']

    try:
        with connection.cursor() as c:
            c.execute('''
                INSERT INTO PENGGUNA(Username, Nama, Password, Alamat_Kel, Alamat_Kec, Alamat_KabKot, Alamat_Prov, No_telepon)
                VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')
            '''.format(username, fullname, password, kelurahan, kecamatan, kabupaten, provinsi, notelp))
            if (tipe == 'admin'):
                c.execute('''
                    INSERT INTO ADMIN_SATGAS(Username)
                    VALUES ('{}')
                '''.format(username))   
            elif (tipe == 'faskes'):
                c.execute('''
                    INSERT INTO PETUGAS_FASKES(Username)
                    VALUES ('{}')
                '''.format(username)) 
            elif (tipe == 'supplier'):
                c.execute('''
                    INSERT INTO SUPPLIER(Username, Nama_organisasi)
                    VALUES ('{}', '{}')
                '''.format(username, organisasi)) 
            elif (tipe == 'distribusi'):
                c.execute('''
                    INSERT INTO PETUGAS_DISTRIBUSI(Username, NO_SIM)
                    VALUES ('{}', '{}')
                '''.format(username, nosim))
    except IntegrityError:
        pass

    return redirect('/')

# logout -> redirect to login page
def logout(request):
    request.session['username'] = ''
    request.session['role'] = ''
    return redirect('auth_app:login')
