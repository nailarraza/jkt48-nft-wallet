# D:\jkt48-nft-wallet\app\routes\auth.py
# File ini berisi semua rute yang terkait dengan autentikasi pengguna,
# seperti registrasi, login, dan logout.

from flask import Blueprint, render_template, redirect, url_for, flash, request
from app import db, bcrypt
from app.models import User, Wallet
from app.wallet import WalletManager
from flask_login import login_user, logout_user, current_user, login_required

# Membuat Blueprint 'auth' untuk mengelompokkan rute-rute ini.
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Rute untuk halaman registrasi pengguna baru."""
    # Jika pengguna sudah login, alihkan mereka ke halaman utama.
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        # Ambil data dari formulir yang di-submit.
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # --- Validasi Sederhana ---
        # Periksa apakah password dan konfirmasi password cocok.
        if password != confirm_password:
            flash('Password tidak cocok! Silakan coba lagi.', 'danger')
            return redirect(url_for('auth.register'))
        
        # Periksa apakah email sudah terdaftar di database.
        user_by_email = User.query.filter_by(email=email).first()
        if user_by_email:
            flash('Email sudah terdaftar. Silakan gunakan email lain.', 'danger')
            return redirect(url_for('auth.register'))

        # Periksa apakah username sudah digunakan.
        user_by_username = User.query.filter_by(username=username).first()
        if user_by_username:
            flash('Username sudah digunakan. Silakan gunakan username lain.', 'danger')
            return redirect(url_for('auth.register'))

        # --- Proses Pembuatan Akun & Wallet ---
        # Hash password sebelum disimpan ke database untuk keamanan.
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        # Buat objek User baru.
        new_user = User(username=username, email=email, password_hash=hashed_password)
        
        # Panggil WalletManager untuk membuat pasangan kunci privat dan publik baru.
        private_key, public_key = WalletManager.generate_wallet_keys()
        # Buat objek Wallet baru dan hubungkan dengan user yang baru dibuat.
        new_wallet = Wallet(user=new_user, private_key=private_key, public_key=public_key)
        
        try:
            # Tambahkan user dan wallet baru ke sesi database.
            db.session.add(new_user)
            db.session.add(new_wallet)
            # Commit sesi untuk menyimpan perubahan ke database secara atomik.
            db.session.commit()
            
            # Setelah registrasi berhasil, langsung login-kan pengguna.
            login_user(new_user)
            
            flash('Akun berhasil dibuat! Selamat datang di JKT48 NFT-Tix.', 'success')
            return redirect(url_for('main.index'))
        except Exception as e:
            # Jika terjadi error saat menyimpan, batalkan semua perubahan (rollback).
            db.session.rollback()
            flash(f'Terjadi kesalahan saat membuat akun: {e}', 'danger')
            return redirect(url_for('auth.register'))

    # Jika metodenya GET, tampilkan halaman formulir registrasi.
    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Rute untuk halaman login pengguna."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        identifier = request.form.get('identifier')
        password = request.form.get('password')
        
        # Cek apakah identifier adalah email atau username
        if '@' in identifier:
            user = User.query.filter_by(email=identifier).first()
        else:
            user = User.query.filter_by(username=identifier).first()

        # Periksa apakah pengguna ada DAN password yang dimasukkan cocok dengan hash di database.
        if user and bcrypt.check_password_hash(user.password_hash, password):
            # Jika cocok, login-kan pengguna. `remember=True` akan menyimpan sesi login.
            login_user(user, remember=True)
            flash('Login berhasil! Selamat datang kembali.', 'success')
            
            # Alihkan pengguna ke halaman yang mereka tuju sebelumnya (jika ada), atau ke halaman utama.
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        else:
            flash('Login gagal. Periksa kembali username/email dan password Anda.', 'danger')

    return render_template('login.html')

@auth_bp.route('/logout')
@login_required # Hanya pengguna yang login yang bisa logout.
def logout():
    """Rute untuk logout."""
    logout_user()
    flash('Anda telah berhasil logout.', 'info')
    return redirect(url_for('main.index'))
