# D:\jkt48-nft-wallet\app\models.py
# File ini mendefinisikan semua model database menggunakan Flask-SQLAlchemy.
# Setiap kelas di sini merepresentasikan sebuah tabel di dalam database MySQL kita.

from sqlalchemy.orm import relationship
from . import db, login_manager
from flask_login import UserMixin
from datetime import datetime
import uuid

# Fungsi user_loader ini digunakan oleh Flask-Login.
# Ia dipanggil setiap kali pengguna yang sudah login meminta halaman baru.
# Fungsinya adalah untuk memuat objek User dari database berdasarkan ID yang disimpan di sesi.
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    """
    Model untuk tabel Pengguna (Users).
    Mewarisi dari UserMixin untuk mendapatkan fungsionalitas default Flask-Login
    seperti is_authenticated, is_active, dll.
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    # Public ID digunakan sebagai pengenal unik yang aman untuk dibagikan (misal di URL atau API)
    public_id = db.Column(db.String(50), unique=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    # Password disimpan dalam bentuk hash untuk keamanan, bukan teks biasa.
    password_hash = db.Column(db.String(128), nullable=False)
    # Kolom untuk verifikasi KTP (opsional, bisa dikembangkan lebih lanjut)
    nik = db.Column(db.String(16), unique=True, nullable=True) 
    # Role menentukan hak akses pengguna: 'User' (penggemar) atau 'SuperAdmin'.
    role = db.Column(db.String(20), nullable=False, default='User') 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relasi one-to-one dengan Wallet. cascade="all, delete-orphan" berarti jika User dihapus,
    # Wallet yang terhubung juga akan ikut terhapus.
    wallet = db.relationship('Wallet', backref='user', uselist=False, cascade="all, delete-orphan")
    
    # Relasi one-to-many dengan Ticket.
    tickets = relationship('Ticket', back_populates='owner')

    def __repr__(self):
        return f'<User {self.username}>'

class Wallet(db.Model):
    """Model untuk dompet crypto simulasi."""
    __tablename__ = 'wallets'

    id = db.Column(db.Integer, primary_key=True)
    # Foreign Key yang menghubungkan wallet ini ke seorang User.
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # Saldo awal 1 Miliar "JKT48 Koin" saat wallet dibuat.
    balance = db.Column(db.Float, nullable=False, default=100000000.0) 
    # Kunci privat dan publik untuk transaksi di blockchain simulasi.
    private_key = db.Column(db.String(64), unique=True, nullable=False)
    public_key = db.Column(db.String(64), unique=True, nullable=False)

    def __repr__(self):
        return f'<Wallet for User ID {self.user_id}>'

class Event(db.Model):
    """Model untuk tabel Event atau Konser."""
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    date = db.Column(db.DateTime, nullable=False)
    venue = db.Column(db.String(120), nullable=True)
    # URL ke gambar poster event.
    image_url = db.Column(db.String(255), nullable=True) 
    # Mengembalikan atribut harga dan ketersediaan tiket ke model Event
    ticket_price = db.Column(db.Float, nullable=False, default=0)
    tickets_available = db.Column(db.Integer, nullable=False, default=0)

    # Relasi ke tiket. Jika event dihapus, semua tiketnya ikut terhapus.
    tickets = relationship('Ticket', back_populates='event', cascade="all, delete-orphan")

# Menghapus model TicketClass karena tidak lagi digunakan.
# class TicketClass(db.Model):
#     ...

class Ticket(db.Model):
    """Model untuk tiket NFT."""
    __tablename__ = 'tickets'

    id = db.Column(db.Integer, primary_key=True)
    # Foreign Key ke pemilik tiket (User) dan event terkait.
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    # Hash unik sebagai ID NFT, membuktikan keunikan setiap tiket.
    nft_id = db.Column(db.String(64), unique=True, nullable=False) 
    purchase_date = db.Column(db.DateTime, default=datetime.utcnow)
    # Status tiket: 'valid' (bisa digunakan), 'used' (sudah digunakan), 'expired' (kedaluwarsa).
    status = db.Column(db.String(20), default='valid') 
    # Nama file dari gambar QR Code. Panjangnya ditambah untuk menampung hash (64) + ekstensi (.png).
    qr_code_hash = db.Column(db.String(100), nullable=True)

    owner = relationship('User', back_populates='tickets')
    event = relationship('Event', back_populates='tickets')

    def __repr__(self):
        return f'<Ticket {self.nft_id} for Event ID {self.event_id}>'

class Transaction(db.Model):
    """
    Model untuk mencatat semua transaksi yang terjadi.
    Tabel ini bersifat opsional untuk aplikasi inti, tetapi berguna untuk audit dan logging.
    Transaksi utama dicatat langsung di dalam blockchain kita.
    """
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    sender_public_key = db.Column(db.String(64), nullable=False)
    receiver_public_key = db.Column(db.String(64), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    # Tanda tangan digital dari transaksi (disimulasikan).
    signature = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'Transaction from {self.sender_public_key[:10]} to {self.receiver_public_key[:10]} for {self.amount}'
