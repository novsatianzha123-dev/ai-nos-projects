import getpass
import os
import subprocess
import sys



# =========================
# DATA LOGIN ADMIN
# =========================

USERNAME_ADMIN = os.environ.get("ASRAMA_ADMIN_USERNAME")
PASSWORD_ADMIN = os.environ.get("ASRAMA_ADMIN_PASSWORD")





# =========================
# LOGIN SYSTEM
# =========================

if not USERNAME_ADMIN or not PASSWORD_ADMIN:
    raise SystemExit("Atur ASRAMA_ADMIN_USERNAME dan ASRAMA_ADMIN_PASSWORD sebelum membuka login admin.")

print("="*45)
print("          LOGIN ADMIN ASRAMA")
print("="*45)



username = input(
    "Username : "
)


password = getpass.getpass(
    "Password : "
)



if username == USERNAME_ADMIN and password == PASSWORD_ADMIN:


    print("\nLogin berhasil!")

    print(
        "Membuka dashboard admin..."
    )


    # menjalankan admin.py

    subprocess.run([sys.executable, "admin.py"], check=False)



else:


    print(
        "\nUsername atau password salah!"
    )
