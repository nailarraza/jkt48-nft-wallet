# D:\jkt48-nft-wallet\app\utils.py
# File ini berisi fungsi-fungsi utilitas yang dapat digunakan di seluruh aplikasi.

from datetime import datetime
import pytz

def to_wib(dt_or_timestamp):
    """
    Sebuah filter Jinja2 kustom untuk mengonversi datetime UTC atau UNIX timestamp
    ke zona waktu Waktu Indonesia Barat (WIB).
    """
    if not dt_or_timestamp:
        return None

    # Tentukan zona waktu WIB (Asia/Jakarta)
    wib = pytz.timezone('Asia/Jakarta')

    # Jika input adalah UNIX timestamp (dari blockchain)
    if isinstance(dt_or_timestamp, (int, float)):
        dt_utc = datetime.fromtimestamp(dt_or_timestamp, tz=pytz.utc)
    # Jika input adalah objek datetime 'naive' (dari database, seperti datetime.utcnow())
    else:
        dt_utc = pytz.utc.localize(dt_or_timestamp)
    
    # Konversi dari UTC ke WIB
    return dt_utc.astimezone(wib)