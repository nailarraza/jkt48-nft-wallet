# D:\jkt48-nft-wallet\app\blockchain.py
# File ini berisi kelas Blockchain yang mengimplementasikan semua logika inti
# dari sistem blockchain simulasi kita.

import hashlib
import json
from time import time
from urllib.parse import urlparse
import uuid

class Blockchain:
    def __init__(self):
        """
        Konstruktor untuk kelas Blockchain.
        Menginisialisasi chain dan transaksi yang tertunda.
        """
        self.chain = []
        self.pending_transactions = []
        
        # Membuat Genesis Block, yaitu blok pertama dalam rantai.
        # Blok ini tidak memiliki blok sebelumnya.
        self.create_new_block(previous_hash='1', proof=100)

    def create_new_block(self, proof, previous_hash=None):
        """
        Membuat blok baru dan menambahkannya ke dalam chain.

        :param proof: <int> Nilai 'proof' yang didapat dari algoritma Proof of Work.
        :param previous_hash: (Opsional) <str> Hash dari blok sebelumnya.
        :return: <dict> Blok baru yang telah dibuat.
        """
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(), # Waktu pembuatan blok (UNIX timestamp)
            'transactions': self.pending_transactions, # Memasukkan semua transaksi tertunda ke blok ini
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        # Setelah transaksi dimasukkan ke blok, kosongkan daftar transaksi tertunda.
        self.pending_transactions = []

        self.chain.append(block)
        return block

    @property
    def get_last_block(self):
        """
        Properti untuk mengembalikan blok terakhir dalam chain.
        """
        return self.chain[-1]

    def create_new_transaction(self, sender, recipient, amount, ticket_details):
        """
        Membuat transaksi baru untuk dimasukkan ke blok selanjutnya.
        Ini adalah implementasi "smart contract" kita: transaksi pembelian tiket.

        :param sender: <str> Alamat pengirim (public key wallet pengguna).
        :param recipient: <str> Alamat penerima (public key wallet sistem/penjual).
        :param amount: <float> Jumlah koin yang ditransfer.
        :param ticket_details: <dict> Informasi detail tentang tiket yang dibeli.
        :return: <int> Index dari blok yang akan menyimpan transaksi ini.
        """
        self.pending_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
            'ticket_details': ticket_details,
            'transaction_id': str(uuid.uuid4()) # ID unik untuk setiap transaksi
        })

        return self.get_last_block['index'] + 1

    @staticmethod
    def hash(block):
        """
        Membuat hash SHA-256 dari sebuah blok.

        :param block: <dict> Blok yang akan di-hash.
        :return: <str> String hash.
        """
        # Kita harus memastikan Dictionary diurutkan (sort_keys=True),
        # jika tidak, kita akan mendapatkan hash yang tidak konsisten.
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, last_proof):
        """
        Algoritma Proof of Work (PoW) sederhana:
         - Cari sebuah angka 'proof' sedemikian rupa sehingga hash dari gabungan
           (last_proof, proof) memiliki 4 angka nol di depannya.
         - 'last_proof' adalah proof dari blok sebelumnya.
         
        :param last_proof: <int> Proof dari blok sebelumnya.
        :return: <int> Proof baru yang valid.
        """
        proof = 0
        while self.is_valid_proof(last_proof, proof) is False:
            proof += 1
        
        return proof

    @staticmethod
    def is_valid_proof(last_proof, proof):
        """
        Memvalidasi sebuah proof: Apakah hash(last_proof, proof) memiliki 4 nol di depannya?
        Tingkat kesulitan ('0000') bisa diubah untuk membuat mining lebih sulit atau mudah.

        :param last_proof: <int> Proof sebelumnya.
        :param proof: <int> Proof yang sedang diuji.
        :return: <bool> True jika valid, False jika tidak.
        """
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    def is_chain_valid(self, chain):
        """
        Memeriksa apakah sebuah blockchain valid.

        :param chain: <list> Sebuah blockchain.
        :return: <bool> True jika valid, False jika tidak.
        """
        previous_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            
            # 1. Periksa apakah hash dari blok sebelumnya benar.
            # Ini memastikan integritas dan keterhubungan rantai.
            if block['previous_hash'] != self.hash(previous_block):
                return False

            # 2. Periksa apakah Proof of Work untuk blok saat ini benar.
            # Ini memastikan setiap blok ditambahkan melalui proses mining yang sah.
            if not self.is_valid_proof(previous_block['proof'], block['proof']):
                return False

            previous_block = block
            current_index += 1

        return True
