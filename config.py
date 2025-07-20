# D:\jkt48-nft-wallet\config.py
# File ini bertanggung jawab untuk memuat semua variabel konfigurasi
# dari file .env ke dalam aplikasi Flask. Ini adalah praktik terbaik
# untuk memisahkan konfigurasi dari kode utama.

import os
from dotenv import load_dotenv


# Menentukan direktori dasar proyek
basedir = os.path.abspath(os.path.dirname(__file__))

# Memuat variabel lingkungan dari file .env yang berada di direktori dasar
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    """
    Kelas Konfigurasi Aplikasi.
    
    Atribut kelas ini akan menjadi pengaturan konfigurasi untuk aplikasi Flask.
    Nilai-nilai ini diambil dari variabel lingkungan yang telah dimuat dari file .env.
    """

    # SECRET_KEY: Kunci rahasia yang digunakan oleh Flask untuk mengamankan data sesi pengguna,
    # cookies, dan perlindungan terhadap serangan Cross-Site Request Forgery (CSRF).
    # Penting untuk menjaga kunci ini tetap rahasia.
    SECRET_KEY = os.environ.get('SECRET_KEY')

    # SQLALCHEMY_DATABASE_URI: String koneksi yang memberi tahu SQLAlchemy cara terhubung ke database.
    # Formatnya: 'dialect+driver://username:password@host:port/database_name'
    # Contoh untuk MySQL dengan driver PyMySQL: 'mysql+pymysql://root:@localhost/jkt48_nft_db'
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')

    # SQLALCHEMY_TRACK_MODIFICATIONS: Jika diatur ke True, Flask-SQLAlchemy akan melacak
    # modifikasi objek dan mengeluarkan sinyal. Fitur ini membutuhkan memori tambahan dan
    # akan dinonaktifkan (diatur ke False) untuk meningkatkan performa.
    SQLALCHEMY_TRACK_MODIFICATIONS = False
