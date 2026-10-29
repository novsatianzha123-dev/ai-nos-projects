import sqlite3



# =========================
# DATABASE
# =========================

conn = sqlite3.connect(
    "asrama.db"
)

cursor = conn.cursor()



# =========================
# TAMPIL SEMUA LAPORAN
# =========================

def lihat_laporan():

    print("\n")
    print("="*50)
    print("          DATA LAPORAN ASRAMA")
    print("="*50)


    cursor.execute(
        """
        SELECT * FROM laporan
        """
    )


    data = cursor.fetchall()



    if not data:

        print("Belum ada laporan.")

        return



    for laporan in data:

        print("\n----------------------------")

        print("ID        :", laporan[0])
        print("Tanggal   :", laporan[1])
        print("Nama      :", laporan[2])
        print("Kamar     :", laporan[3])
        print("Masalah   :", laporan[4])
        print("Kategori  :", laporan[5])
        print("Prioritas :", laporan[6])
        print("Status    :", laporan[7])




# =========================
# UPDATE STATUS
# =========================

def update_status():


    lihat_laporan()



    id_laporan = input(
        "\nMasukkan ID laporan : "
    )



    print("""
=================
STATUS BARU
=================

1. Menunggu
2. Diproses
3. Selesai
""")


    pilihan=input(
        "Pilih : "
    )



    status = {

        "1":"Menunggu",
        "2":"Diproses",
        "3":"Selesai"

    }



    if pilihan in status:


        cursor.execute(
            """
            UPDATE laporan
            SET status=?
            WHERE id=?
            """,

            (
                status[pilihan],
                id_laporan
            )

        )


        conn.commit()



        print(
            "\nStatus berhasil diperbarui!"
        )


    else:

        print(
            "Pilihan tidak ada."
        )





# =========================
# STATISTIK
# =========================

def statistik():

    print("\n")
    print("="*40)
    print("       STATISTIK ASRAMA")
    print("="*40)



    cursor.execute(
        """
        SELECT COUNT(*) FROM laporan
        """
    )


    total = cursor.fetchone()[0]


    print(
        "Total laporan :",
        total
    )



    kategori = [

        "fasilitas",
        "jaringan",
        "kebersihan",
        "keamanan",
        "perizinan",
        "peraturan",
        "kehilangan",
        "administrasi",
        "pengaduan"

    ]



    print("\nKategori:")



    for k in kategori:


        cursor.execute(
            """
            SELECT COUNT(*)
            FROM laporan
            WHERE kategori=?
            """,

            (k,)

        )


        jumlah = cursor.fetchone()[0]


        print(
            k,
            ":",
            jumlah
        )





    print("\nStatus:")



    for s in [

        "Menunggu",
        "Diproses",
        "Selesai"

    ]:


        cursor.execute(
            """
            SELECT COUNT(*)
            FROM laporan
            WHERE status=?
            """,

            (s,)

        )


        jumlah = cursor.fetchone()[0]


        print(
            s,
            ":",
            jumlah
        )






# =========================
# FILTER KATEGORI
# =========================

def filter_kategori():


    kategori=input(
        "\nMasukkan kategori : "
    )


    cursor.execute(
        """
        SELECT * FROM laporan
        WHERE kategori=?
        """,

        (kategori,)

    )


    data=cursor.fetchall()



    if not data:

        print(
            "Tidak ada laporan."
        )

        return



    for laporan in data:

        print("\n----------------")

        print(
            "ID:",
            laporan[0]
        )

        print(
            "Masalah:",
            laporan[4]
        )

        print(
            "Status:",
            laporan[7]
        )





# =========================
# MENU ADMIN
# =========================


while True:


    print("\n")
    print("="*45)
    print("          ADMIN ASRAMA")
    print("="*45)


    print("""
1. Lihat semua laporan
2. Update status laporan
3. Statistik laporan
4. Filter kategori
5. Keluar
""")


    menu=input(
        "Pilih menu : "
    )



    if menu=="1":

        lihat_laporan()



    elif menu=="2":

        update_status()



    elif menu=="3":

        statistik()



    elif menu=="4":

        filter_kategori()



    elif menu=="5":

        print(
            "Keluar admin..."
        )

        break



    else:

        print(
            "Menu tidak tersedia."
        )