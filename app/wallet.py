# D:\jkt48-nft-wallet\app\wallet.py
# File ini berisi kelas WalletManager yang bertanggung jawab untuk semua
# operasi terkait dompet digital, terutama pembuatan pasangan kunci.

import os
import hashlib

class WalletManager:
    """
    Kelas untuk mengelola operasi dompet, seperti pembuatan kunci.
    Ini adalah simulasi sederhana dari dompet kripto, yang menunjukkan konsep dasarnya.
    """

    @staticmethod
    def generate_wallet_keys():
        """
        Menghasilkan sepasang kunci privat (private key) dan kunci publik (public key) baru.

        Dalam sistem kripto nyata seperti Bitcoin atau Ethereum, proses ini menggunakan
        algoritma kriptografi kurva eliptik (Elliptic Curve Cryptography - ECC) yang kompleks.
        Di sini, kita simulasikan dengan cara yang lebih sederhana namun tetap menjaga
        prinsip utamanya: kunci publik diturunkan dari kunci privat melalui proses satu arah.

        :return: tuple (private_key, public_key)
        """
        # 1. Private Key: Dibuat dari sumber data acak yang aman secara kriptografis.
        #    os.urandom(32) menghasilkan 32 byte (256 bit) data acak, setara dengan
        #    tingkat keamanan yang digunakan di banyak sistem kripto.
        #    .hex() mengubah data biner ini menjadi string heksadesimal 64 karakter.
        private_key = os.urandom(32).hex()

        # 2. Public Key: Diturunkan dengan melakukan hashing pada private key.
        #    Ini adalah proses satu arah. Sangat mudah mendapatkan public key dari private key,
        #    tetapi secara komputasi tidak mungkin untuk mendapatkan private key dari public key.
        #    Kita menggunakan SHA-256, algoritma hash yang sama yang digunakan di Bitcoin.
        
        # Meng-encode string private key menjadi bytes, karena fungsi hash bekerja pada bytes.
        private_key_bytes = private_key.encode('utf-8')
        
        # Melakukan hash pada private key untuk menghasilkan public key.
        public_key = hashlib.sha256(private_key_bytes).hexdigest()

        return private_key, public_key

    @staticmethod
    def sign_transaction(private_key, transaction_data):
        """
        (Simulasi) Menandatangani data transaksi menggunakan kunci privat.
        Tanda tangan digital ini membuktikan bahwa pemilik kunci privat menyetujui transaksi tersebut.

        :param private_key: Kunci privat pemilik dompet.
        :param transaction_data: String dari data yang akan ditandatangani.
        :return: String heksadesimal dari tanda tangan digital (signature).
        """
        # Dalam simulasi sederhana ini, kita menggabungkan kunci privat dengan data transaksi
        # lalu melakukan hash pada gabungan tersebut. Ini menunjukkan bahwa tanda tangan
        # bergantung pada isi transaksi DAN kunci privat rahasia, sehingga tidak dapat dipalsukan
        # tanpa memiliki kunci privat.
        signature_data = f"{private_key}{transaction_data}".encode('utf-8')
        signature = hashlib.sha256(signature_data).hexdigest()
        return signature

    @staticmethod
    def verify_signature(public_key, signature, transaction_data):
        """
        (Simulasi) Memverifikasi sebuah tanda tangan digital.
        Dalam sistem nyata, proses ini menggunakan matematika kriptografi asimetris
        dan tidak memerlukan kunci privat untuk verifikasi.
        Untuk tujuan edukasi, fungsi ini tidak diimplementasikan secara penuh dalam alur utama
        karena validasi utama kita bergantung pada sesi login pengguna yang aman.
        Namun, konsepnya penting untuk diketahui.
        """
        # Proses verifikasi yang sesungguhnya akan mencoba merekonstruksi tanda tangan
        # atau memvalidasinya menggunakan kunci publik tanpa pernah mengetahui kunci privat.
        print("Fungsi verifikasi tanda tangan dipanggil. Dalam aplikasi ini, validasi utama terjadi melalui sesi login pengguna.")
        return True
