# D:\jkt48-nft-wallet\app\routes\main.py
# File ini berisi semua rute utama aplikasi yang dapat diakses pengguna,
# seperti halaman utama, detail event, pembelian tiket, dan halaman profil pengguna.

from flask import Blueprint, render_template, abort, flash, redirect, url_for, request
from flask_login import current_user, login_required
from app.models import Event, User, Ticket
from app import db, blockchain
from datetime import datetime
import uuid
import qrcode
import os
import hashlib

# Membuat Blueprint 'main' untuk mengelompokkan rute-rute ini.
main_bp = Blueprint('main', __name__)

# Alamat dompet "sistem" atau "rumah" untuk menerima pembayaran tiket.
# Dalam aplikasi nyata, ini akan menjadi alamat publik dari dompet organisasi.
HOUSE_WALLET_ADDRESS = "0000_JKT48_OFFICIAL_TICKETING_WALLET_0000"

@main_bp.route('/')
def index():
    """Rute untuk halaman utama (homepage)."""
    # Mengambil semua event yang tanggalnya belum lewat dari database.
    # Diurutkan berdasarkan tanggal terdekat.
    upcoming_events = Event.query.filter(Event.date >= datetime.utcnow()).order_by(Event.date.asc()).all()
    return render_template('index.html', title='Home', events=upcoming_events)

@main_bp.route('/event/<int:event_id>')
def event_detail(event_id):
    """Rute untuk menampilkan halaman detail dari sebuah event."""
    # Mengambil data event berdasarkan ID, atau menampilkan error 404 jika tidak ditemukan.
    event = Event.query.get_or_404(event_id)
    return render_template('event_detail.html', title=event.name, event=event)

@main_bp.route('/buy_ticket/<int:event_id>', methods=['POST'])
@login_required # Decorator ini memastikan hanya user yang sudah login bisa mengakses rute ini.
def buy_ticket(event_id):
    """Rute yang menangani logika pembelian tiket. Ini adalah inti dari 'smart contract' kita."""
    event = Event.query.get_or_404(event_id)
    user = current_user

    # === TAHAP 1: VALIDASI (BAGIAN DARI "SMART CONTRACT") ===
    # Cek ketersediaan tiket.
    if event.tickets_available <= 0:
        flash('Maaf, tiket untuk event ini sudah habis terjual.', 'danger')
        return redirect(url_for('main.event_detail', event_id=event.id))

    # Cek kecukupan saldo pengguna.
    if user.wallet.balance < event.ticket_price:
        flash(f'Saldo Anda tidak cukup. Saldo: {user.wallet.balance:,.0f} Koin, Harga: {event.ticket_price:,.0f} Koin.', 'danger')
        return redirect(url_for('main.event_detail', event_id=event.id))
        
    # Cek apakah pengguna sudah memiliki tiket untuk event ini.
    existing_ticket = Ticket.query.filter_by(user_id=user.id, event_id=event.id).first()
    if existing_ticket:
        flash('Anda sudah memiliki tiket untuk event ini.', 'info')
        return redirect(url_for('main.ticket_detail', ticket_id=existing_ticket.id))

    try:
        # === TAHAP 2: PERSIAPAN TRANSAKSI BLOCKCHAIN ===
        # Membuat detail transaksi untuk dicatat di blockchain.
        ticket_purchase_details = {
            "user_id": user.id,
            "username": user.username,
            "event_id": event.id,
            "event_name": event.name
        }
        # Menambahkan transaksi ke daftar 'pending_transactions' di blockchain.
        blockchain.create_new_transaction(
            sender=user.wallet.public_key,
            recipient=HOUSE_WALLET_ADDRESS,
            amount=event.ticket_price,
            ticket_details=ticket_purchase_details
        )

        # === TAHAP 3: PROSES MINING (PROOF OF WORK) ===
        last_block = blockchain.get_last_block
        last_proof = last_block['proof']
        proof = blockchain.proof_of_work(last_proof) # Mencari proof baru yang valid.

        # "Menambang" blok baru yang berisi transaksi pembelian tiket.
        previous_hash = blockchain.hash(last_block)
        block = blockchain.create_new_block(proof, previous_hash)

        # === TAHAP 4: PENCETAKAN TIKET NFT & UPDATE DATABASE ===
        # Membuat ID NFT unik berdasarkan data dari blok yang baru ditambang.
        nft_id_base = f"{block['previous_hash']}-{block['timestamp']}-{user.id}-{event.id}"
        nft_id = hashlib.sha256(nft_id_base.encode()).hexdigest()
        
        # Membuat QR Code unik untuk verifikasi.
        qr_data = f"TicketID:{nft_id};Event:{event.name};Owner:{user.username};"
        qr_code_hash = hashlib.sha256(qr_data.encode()).hexdigest()
        
        qr_code_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static', 'qrcodes')
        os.makedirs(qr_code_dir, exist_ok=True)
        
        qr_code_filename = f"{qr_code_hash}.png"
        qr_code_path = os.path.join(qr_code_dir, qr_code_filename)
        
        img = qrcode.make(qr_data)
        img.save(qr_code_path)

        # Membuat entri tiket baru di tabel 'tickets'.
        new_ticket = Ticket(
            user_id=user.id,
            event_id=event.id,
            nft_id=nft_id,
            status='valid',
            qr_code_hash=qr_code_filename
        )

        # Update saldo pengguna dan jumlah tiket tersedia di database.
        user.wallet.balance -= event.ticket_price
        event.tickets_available -= 1

        db.session.add(new_ticket)
        db.session.commit() # Menyimpan semua perubahan ke database.

        flash(f"Pembelian tiket untuk '{event.name}' berhasil! Blok #{block['index']} telah ditambang.", 'success')
        return redirect(url_for('main.ticket_detail', ticket_id=new_ticket.id))

    except Exception as e:
        db.session.rollback() # Batalkan semua perubahan jika terjadi error.
        flash(f'Terjadi kesalahan saat proses pembelian: {e}', 'danger')
        return redirect(url_for('main.event_detail', event_id=event.id))

@main_bp.route('/my_tickets')
@login_required
def my_tickets():
    """Rute untuk menampilkan semua tiket yang dimiliki oleh pengguna saat ini."""
    tickets = Ticket.query.filter_by(user_id=current_user.id).order_by(Ticket.purchase_date.desc()).all()
    return render_template('my_tickets.html', tickets=tickets)

@main_bp.route('/ticket/<int:ticket_id>')
@login_required
def ticket_detail(ticket_id):
    """Rute untuk menampilkan detail dari satu tiket spesifik."""
    ticket = Ticket.query.get_or_404(ticket_id)
    # Pastikan pengguna hanya bisa melihat tiket miliknya sendiri, kecuali dia admin.
    if ticket.user_id != current_user.id and current_user.role != 'SuperAdmin':
        abort(403) # Error Forbidden.
    return render_template('ticket_detail.html', ticket=ticket)

@main_bp.route('/wallet')
@login_required
def wallet_info():
    """Rute untuk menampilkan informasi dompet pengguna saat ini."""
    return render_template('wallet.html', user=current_user)

@main_bp.route('/blockchain')
def view_chain():
    """Rute untuk melihat seluruh isi dari blockchain (Blockchain Explorer)."""
    # Kirim seluruh objek blockchain agar kita bisa menggunakan metodenya di template.
    return render_template('blockchain_viewer.html', chain=blockchain.chain, blockchain=blockchain)
