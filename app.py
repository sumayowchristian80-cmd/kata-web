from flask import Flask, render_template, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kampus_baru.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "polinusa-secret-key"

db = SQLAlchemy(app)

# ================= MODEL =================
class Berita(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    judul = db.Column(db.String(200))
    isi = db.Column(db.Text)
    foto = db.Column(db.String(200))
    breaking = db.Column(db.Boolean, default=False)
    tanggal = db.Column(db.DateTime, default=datetime.utcnow)

class Iklan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100))
    link = db.Column(db.String(200))

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))

class Jurusan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100))
    deskripsi = db.Column(db.Text)

class Prodi(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100))
    jurusan_id = db.Column(db.Integer, db.ForeignKey('jurusan.id'))

class Fasilitas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100))
    deskripsi = db.Column(db.Text)



# ================= UPLOAD =================
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ================= ROUTE =================

@app.route('/')
def home():
    berita = Berita.query.order_by(Berita.tanggal.desc()).all()
    return render_template('home.html', berita=berita)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        admin = Admin.query.filter_by(
            username=request.form['username'],
            password=request.form['password']
        ).first()

        if admin:
            session['admin'] = admin.username
            return redirect('/admin')
        else:
            flash('Login gagal')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/admin')
def admin_dashboard():
    if 'admin' not in session:
        return redirect('/login')

    total_berita = Berita.query.count()
    total_jurusan = Jurusan.query.count()
    total_prodi = Prodi.query.count()
    total_fasilitas = Fasilitas.query.count()

    return render_template(
        'admin/dashboard.html',
        total_berita=total_berita,
        total_jurusan=total_jurusan,
        total_prodi=total_prodi,
        total_fasilitas=total_fasilitas
    )


# ===== BERITA =====
@app.route('/admin/berita', methods=['GET', 'POST'])
def kelola_berita():
    if 'admin' not in session:
        return redirect('/login')

    if request.method == 'POST':
        foto = request.files['foto']
        filename = foto.filename
        foto.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        berita = Berita(
            judul=request.form['judul'],
            isi=request.form['isi'],
            foto=filename,
            breaking=True if request.form.get('breaking') else False
        )
        db.session.add(berita)
        db.session.commit()
        return redirect('/admin/berita')

    data = Berita.query.all()
    return render_template('admin/berita.html', data=data)

@app.route('/admin/berita/hapus/<int:id>')
def hapus_berita(id):
    if 'admin' not in session:
        return redirect('/login')
    b = Berita.query.get(id)
    db.session.delete(b)
    db.session.commit()
    return redirect('/admin/berita')

@app.route('/admin/berita/edit/<int:id>', methods=['GET', 'POST'])
def edit_berita(id):
    if 'admin' not in session:
        return redirect('/login')

    berita = Berita.query.get_or_404(id)

    if request.method == 'POST':
        berita.judul = request.form['judul']
        berita.isi = request.form['isi']
        berita.breaking = True if request.form.get('breaking') else False

        # jika upload foto baru
        if 'foto' in request.files:
            foto = request.files['foto']
            if foto.filename != '':
                filename = foto.filename
                foto.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                berita.foto = filename

        db.session.commit()
        flash('Berita berhasil diupdate')
        return redirect('/admin/berita')

    return render_template('admin/edit_berita.html', berita=berita)


# ===== JURUSAN / PRODI / FASILITAS =====
@app.route('/admin/jurusan', methods=['POST'])
def tambah_jurusan():
    if 'admin' not in session:
        return redirect('/login')
    db.session.add(Jurusan(
        nama=request.form['nama'],
        deskripsi=request.form['deskripsi']
    ))
    db.session.commit()
    return redirect('/admin')

@app.route('/admin/prodi', methods=['POST'])
def tambah_prodi():
    if 'admin' not in session:
        return redirect('/login')
    db.session.add(Prodi(
        nama=request.form['nama'],
        jurusan_id=request.form['jurusan_id']
    ))
    db.session.commit()
    return redirect('/admin')

@app.route('/admin/fasilitas', methods=['POST'])
def tambah_fasilitas():
    if 'admin' not in session:
        return redirect('/login')
    db.session.add(Fasilitas(
        nama=request.form['nama'],
        deskripsi=request.form['deskripsi']
    ))
    db.session.commit()
    return redirect('/admin')

# ===== PUBLIK =====

@app.route('/jurusan')
def jurusan():
    data = Jurusan.query.all()
    return render_template('jurusan.html', data=data)

@app.route('/prodi')
def prodi():
    data = Prodi.query.all()
    return render_template('prodi.html', data=data)

@app.route('/fasilitas')
def fasilitas():
    data = Fasilitas.query.all()
    return render_template('fasilitas.html', data=data)


# ================= RUN =================
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
