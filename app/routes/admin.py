# D:\jkt48-nft-wallet\app\routes\admin.py
# File ini berisi semua rute yang hanya dapat diakses oleh pengguna dengan role 'SuperAdmin'.
# Mencakup dashboard, manajemen event, dan verifikasi tiket.

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from app import db
from app.models import Event, User, Ticket
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime

#----------------------------------------------------------------#
# Decorator Kustom untuk Proteksi Rute Admin
#----------------------------------------------------------------#
def admin_required(f):
    """
    Decorator untuk memastikan hanya pengguna yang diautentikasi dan memiliki
    role 'SuperAdmin' yang dapat mengakses rute yang di-wrap.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'SuperAdmin':
            abort(403) # Kirim error '403 Forbidden' jika akses ditolak.
        return f(*args, **kwargs)
    return decorated_function

# Membuat Blueprint 'admin' untuk mengelompokkan rute-rute ini.
admin_bp = Blueprint('admin', __name__)

#----------------------------------------------------------------#
# Rute-rute Admin
#----------------------------------------------------------------#

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Rute untuk halaman utama dashboard admin."""
    # --- Kalkulasi Statistik untuk Dashboard ---
    total_users = User.query.count()
    total_events = Event.query.count()
    total_tickets_sold = Ticket.query.count()
    
    # Menghitung total pendapatan (koin) dari semua tiket yang terjual.
    total_revenue = db.session.query(db.func.sum(Event.ticket_price)).join(Ticket, Ticket.event_id == Event.id).scalar() or 0

    stats = {
        'total_users': total_users,
        'total_events': total_events,
        'total_tickets_sold': total_tickets_sold,
        'total_revenue': total_revenue
    }
    
    events = Event.query.order_by(Event.date.desc()).all()
    return render_template('admin/dashboard.html', events=events, stats=stats)

@admin_bp.route('/event/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_event():
    """Rute untuk menambah event baru (Create)."""
    if request.method == 'POST':
        # Ambil data dari formulir.
        name = request.form.get('name')
        description = request.form.get('description')
        date_str = request.form.get('date')
        date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
        venue = request.form.get('venue')
        ticket_price = float(request.form.get('ticket_price'))
        tickets_available = int(request.form.get('tickets_available'))
        image_url = request.form.get('image_url')

        # Buat objek Event baru dan simpan ke database.
        new_event = Event(name=name, description=description, date=date, venue=venue, 
                          ticket_price=ticket_price, tickets_available=tickets_available, image_url=image_url)
        db.session.add(new_event)
        db.session.commit()
        flash('Event baru berhasil ditambahkan!', 'success')
        return redirect(url_for('admin.dashboard'))
    
    return render_template('admin/event_form.html', event=None)

@admin_bp.route('/event/edit/<int:event_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_event(event_id):
    """Rute untuk mengedit event yang sudah ada (Update)."""
    event = Event.query.get_or_404(event_id)
    if request.method == 'POST':
        # Update atribut objek event dengan data baru dari form.
        event.name = request.form.get('name')
        event.description = request.form.get('description')
        event.date = datetime.strptime(request.form.get('date'), '%Y-%m-%dT%H:%M')
        event.venue = request.form.get('venue')
        event.ticket_price = float(request.form.get('ticket_price'))
        event.tickets_available = int(request.form.get('tickets_available'))
        event.image_url = request.form.get('image_url')
        
        db.session.commit()
        flash('Event berhasil diperbarui!', 'success')
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/event_form.html', event=event)

@admin_bp.route('/event/delete/<int:event_id>', methods=['POST'])
@login_required
@admin_required
def delete_event(event_id):
    """Rute untuk menghapus event (Delete)."""
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    flash('Event berhasil dihapus.', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/verify-ticket', methods=['GET', 'POST'])
@login_required
@admin_required
def verify_ticket():
    """Rute untuk halaman verifikasi tiket (pencarian)."""
    ticket = None
    search_attempted = False
    if request.method == 'POST':
        search_attempted = True
        query = request.form.get('search_query', '').strip()
        
        # Coba cari tiket berdasarkan NFT ID.
        ticket = Ticket.query.filter_by(nft_id=query).first()
        
        # Jika tidak ketemu, coba cari berdasarkan email pemilik.
        if not ticket:
            user = User.query.filter_by(email=query).first()
            if user:
                # Ambil tiket pertama user (bisa disesuaikan jika perlu logika lebih kompleks).
                ticket = Ticket.query.filter_by(user_id=user.id).order_by(Ticket.purchase_date.desc()).first()

    return render_template('admin/verify_ticket.html', ticket=ticket, search_attempted=search_attempted)

@admin_bp.route('/use-ticket/<int:ticket_id>', methods=['POST'])
@login_required
@admin_required
def use_ticket(ticket_id):
    """Rute untuk mengubah status tiket menjadi 'used' (proses check-in)."""
    ticket = Ticket.query.get_or_404(ticket_id)
    if ticket.status == 'valid':
        ticket.status = 'used'
        db.session.commit()
        flash(f'Tiket untuk "{ticket.owner.username}" berhasil di-check-in.', 'success')
    else:
        flash('Tiket ini sudah tidak valid atau sudah digunakan.', 'danger')
    
    return redirect(url_for('admin.verify_ticket'))
