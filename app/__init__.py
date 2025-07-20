# D:\jkt48-nft-wallet\app\__init__.py
# File ini adalah "pabrik aplikasi". Ia berisi fungsi `create_app`
# yang menginisialisasi aplikasi Flask beserta semua ekstensinya.
# Pola factory ini membuat aplikasi lebih modular dan mudah diuji.

from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from .blockchain import Blockchain
from datetime import datetime

#----------------------------------------------------------------#
# Inisialisasi Ekstensi
#----------------------------------------------------------------#
# Membuat instance dari ekstensi di luar fungsi factory.
# Ini agar ekstensi-ekstensi ini bisa diimpor dan digunakan di bagian lain aplikasi (seperti di models.py).
db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
login_manager = LoginManager()

# Konfigurasi Flask-Login
# 'auth.login' adalah nama endpoint untuk halaman login (blueprint 'auth', fungsi 'login').
# Jika pengguna yang belum login mencoba mengakses halaman yang dilindungi, mereka akan diarahkan ke sini.
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info' # Kategori pesan flash untuk Bootstrap/Tailwind styling
login_manager.login_message = "Silakan login untuk mengakses halaman ini."

# Inisialisasi Blockchain
# Kita membuat satu instance tunggal dari blockchain yang akan digunakan oleh seluruh aplikasi.
blockchain = Blockchain()

#----------------------------------------------------------------#
# Factory Function Aplikasi
#----------------------------------------------------------------#
def create_app(config_class=Config):
    """
    Fungsi pabrik untuk membuat dan mengkonfigurasi instance aplikasi Flask.
    
    :param config_class: Kelas konfigurasi yang akan digunakan. Defaultnya adalah kelas Config.
    :return: Instance aplikasi Flask yang sudah terkonfigurasi.
    """
    app = Flask(__name__)
    
    # Memuat konfigurasi dari objek/kelas Config
    app.config.from_object(config_class)

    # Menghubungkan ekstensi yang sudah diinisialisasi dengan aplikasi Flask
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    #----------------------------------------------------------------#
    # Registrasi Blueprint (Rute)
    #----------------------------------------------------------------#
    # Blueprint membantu mengorganisir rute-rute aplikasi menjadi beberapa modul.
    from .routes.main import main_bp
    from .routes.auth import auth_bp
    from .routes.admin import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth') # Semua rute di auth_bp akan diawali dengan /auth
    app.register_blueprint(admin_bp, url_prefix='/admin') # Semua rute di admin_bp akan diawali dengan /admin
    
    # Mendaftarkan filter Jinja kustom dari utils.py untuk konversi zona waktu.
    from .utils import to_wib
    app.jinja_env.filters['to_wib'] = to_wib
    
    with app.app_context():
        # Mengimpor model di sini memastikan bahwa model-model diketahui oleh SQLAlchemy
        # saat aplikasi dibuat.
        from . import models
        
    return app
