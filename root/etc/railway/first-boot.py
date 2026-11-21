"""Railway first-boot hardening for Calibre-Web Automated.

* Sets the "admin" password from ADMIN_PASSWORD while it is still the upstream
  default (admin123). Once the password was changed, it is left alone, so a
  restart never overwrites a password you set in the app.
* Replaces the Flask session key that ships inside upstream's template app.db
  (identical on every install) with a random one, once.

Exits 1 if the admin password is still the default afterwards.
"""
import os
import sqlite3
import sys

from werkzeug.security import check_password_hash, generate_password_hash

DB = "/config/app.db"
TEMPLATE_DB = "/app/calibre-web-automated/empty_library/app.db"
DEFAULT_PASSWORD = "admin123"
TAG = "[railway-setup]"


def shipped_session_key():
    try:
        con = sqlite3.connect(f"file:{TEMPLATE_DB}?mode=ro", uri=True)
        row = con.execute("SELECT flask_session_key FROM flask_settings LIMIT 1").fetchone()
        con.close()
        return row[0] if row else None
    except sqlite3.Error:
        return None


def main() -> int:
    if not os.path.exists(DB):
        print(f"{TAG} {DB} is missing", flush=True)
        return 1
    con = sqlite3.connect(DB, timeout=30)
    try:
        shipped = shipped_session_key()
        if shipped is not None:
            cur = con.execute("UPDATE flask_settings SET flask_session_key = ? WHERE flask_session_key = ?",
                              (os.urandom(32), shipped))
            if cur.rowcount:
                print(f"{TAG} Replaced the shared session key with a random one.", flush=True)

        row = con.execute("SELECT id, password FROM user WHERE lower(name) = 'admin'").fetchone()
        if row is None:
            con.commit()
            print(f"{TAG} No 'admin' user; nothing to do.", flush=True)
            return 0
        user_id, current = row
        if not current or not check_password_hash(str(current), DEFAULT_PASSWORD):
            con.commit()
            print(f"{TAG} Admin password already changed; leaving it alone.", flush=True)
            return 0
        new = os.environ.get("ADMIN_PASSWORD", "")
        if not new or new == DEFAULT_PASSWORD:
            con.commit()
            print(f"{TAG} ADMIN_PASSWORD is empty or the default.", flush=True)
            return 1
        con.execute("UPDATE user SET password = ? WHERE id = ?", (generate_password_hash(new), user_id))
        con.commit()
        print(f"{TAG} Admin password set from ADMIN_PASSWORD.", flush=True)
        return 0
    finally:
        con.close()


if __name__ == "__main__":
    sys.exit(main())
