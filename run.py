# D:\jkt48-nft-wallet\run.py
# File ini adalah titik masuk utama (entry point) untuk menjalankan aplikasi Flask.
# Ia juga berisi perintah command-line kustom untuk mengelola aplikasi, seperti membuat admin.

from app import create_app, db
from app.models import User
from flask_migrate import Migrate
import click
import datetime


# Membuat instance aplikasi menggunakan factory function `create_app` dari paket 'app'
app = create_app()

# Menghubungkan Flask-Migrate untuk menangani migrasi skema database
migrate = Migrate(app, db)

#----------------------------------------------------------------#
# Context Processor
# Menyuntikkan variabel/fungsi ke semua template Jinja2
#----------------------------------------------------------------#

@app.context_processor
def inject_now():
    """
    Membuat objek 'now' yang berisi waktu saat ini (UTC) tersedia
    di semua template.
    """
    return {'now': datetime.datetime.utcnow()}

#----------------------------------------------------------------#
# Perintah Command-Line Kustom (CLI)
# Perintah ini dapat dijalankan dari terminal menggunakan "flask <nama_perintah>"
#----------------------------------------------------------------#

@app.cli.command("create-admin")
@click.argument("email")
def create_admin(email):
    """
    Perintah untuk mempromosikan seorang pengguna menjadi 'SuperAdmin' berdasarkan email.
    Cara penggunaan: flask create-admin namaemail@contoh.com
    """
    # Mencari pengguna di database berdasarkan email yang diberikan
    user = User.query.filter_by(email=email).first()
    if user:
        # Jika pengguna ditemukan, ubah rolenya menjadi 'SuperAdmin'
        user.role = 'SuperAdmin'
        db.session.commit()
        print(f"Pengguna {user.username} dengan email {email} telah dipromosikan menjadi SuperAdmin.")
    else:
        # Jika pengguna tidak ditemukan, tampilkan pesan error
        print(f"Pengguna dengan email {email} tidak ditemukan.")

#----------------------------------------------------------------#
# Eksekusi Aplikasi
#----------------------------------------------------------------#

# Blok ini akan dieksekusi hanya jika file 'run.py' dijalankan secara langsung
if __name__ == '__main__':
    # Menjalankan server pengembangan Flask
    # debug=True: Server akan otomatis restart jika ada perubahan kode, dan memberikan debugger interaktif.
    # port=5500: Menjalankan aplikasi di port 5500 sesuai permintaan.
    app.run(debug=True, port=5001)
