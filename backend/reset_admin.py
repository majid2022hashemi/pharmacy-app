#!/usr/bin/env python3
"""
ابزار اضطراری برای بازنشانی رمز عبور مدیر
اجرا: python reset_admin.py
"""
import os
import sys

import bcrypt
import psycopg

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://majid:linux113@localhost:5433/pharmacy_db",
)

def main():
    print("=== بازنشانی رمز عبور مدیر ===")
    new_password = input("رمز عبور جدید برای admin: ").strip()
    if len(new_password) < 6:
        print("خطا: رمز عبور باید حداقل ۶ کاراکتر باشد")
        sys.exit(1)

    confirm = input("تکرار رمز عبور: ").strip()
    if new_password != confirm:
        print("خطا: رمزها یکسان نیستند")
        sys.exit(1)

    hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()

    try:
        conn = psycopg.connect(DATABASE_URL)
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE users SET password_hash = %s WHERE username = 'admin'",
                (hashed,),
            )
            if cur.rowcount == 0:
                print("کاربر admin یافت نشد — در حال ایجاد...")
                cur.execute(
                    """INSERT INTO users (username, password_hash, full_name, role, extra_permissions, is_active)
                       VALUES ('admin', %s, 'مدیر سیستم', 'ADMIN', '[]', true)""",
                    (hashed,),
                )
            conn.commit()
        conn.close()
        print("رمز عبور با موفقیت تغییر کرد.")
    except Exception as e:
        print(f"خطا در اتصال به پایگاه داده: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
