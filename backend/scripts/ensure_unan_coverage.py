"""Asegura que el docente esté vinculado a todos los cursos UNAN y que cada curso tenga estudiantes.

Genera/añade hasta `per_course` estudiantes por curso si es necesario y guarda un CSV con las cuentas creadas
en `backend/uploads/seeded_students_UNAN_<timestamp>.csv`.

Usage:
  cd /run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify
  env DATABASE_URL="postgresql://..." python backend/scripts/ensure_unan_coverage.py --docente-email juan@example.com --per-course 5 --commit

Idempotente: no recrea usuarios o inscripciones existentes.
"""

from datetime import date, datetime
import csv
import uuid
import os
import argparse
import sys

sys.path.insert(0, "backend")

from sqlalchemy import create_engine, text
from src.core.config import settings
from src.services.auth.password_service import PasswordService


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--docente-email", required=True)
    parser.add_argument("--per-course", type=int, default=5)
    parser.add_argument("--password", default="Juanito243019@")
    parser.add_argument("--commit", action="store_true")
    args = parser.parse_args()

    engine = create_engine(settings.database_url)
    pwd = PasswordService()

    created = []

    uploads_dir = os.path.join("backend", "uploads")
    os.makedirs(uploads_dir, exist_ok=True)

    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    csv_path = os.path.join(uploads_dir, f"seeded_students_UNAN_{timestamp}.csv")

    with engine.begin() as conn:
        # find docente usuario
        r = conn.execute(text('SELECT usuario_id FROM "Usuario" WHERE correo_institucional = :email'), {"email": args.docente_email}).fetchone()
        if not r:
            print(f"❗ Docente user with email {args.docente_email} not found. Aborting.")
            return
        docente_id = r[0]
        print(f"Docente usuario_id: {docente_id}")

        # find all UNAN courses
        unan = conn.execute(
            text('SELECT c.curso_id, c.nombre FROM "Curso" c JOIN "Institucion" i ON c.institucion_id = i.institucion_id WHERE LOWER(i.nombre) LIKE :pat OR LOWER(i.sigla) LIKE :pat'),
            {"pat": "%unan%"},
        ).fetchall()

        if not unan:
            print("⚠️ No UNAN courses found. Nothing to do.")
            return

        print(f"Found {len(unan)} UNAN course(s). Ensuring docente linked and students present...")

        for curso_id, nombre in unan:
            # curso_id puede venir como UUID; convertir a str para manipulaciones
            curso_id = str(curso_id)
            # ensure grupo exists or create one
            grp = conn.execute(text('SELECT gc.grupo_id FROM "GrupoCurso" gc WHERE gc.curso_id = :cid LIMIT 1'), {"cid": curso_id}).fetchone()
            if grp:
                grupo_id = grp[0]
            else:
                grupo_id = str(uuid.uuid4())
                conn.execute(text('INSERT INTO "Grupo" (grupo_id, nombre) VALUES (:gid, :nombre)'), {"gid": grupo_id, "nombre": f"Grupo_unan_{curso_id[:8]}"})
                print(f"  - Created grupo {grupo_id} for curso {curso_id}")

            # ensure GrupoCurso link with docente
            ex = conn.execute(text('SELECT grupo_curso_id FROM "GrupoCurso" WHERE curso_id = :cid AND docente_id = :did'), {"cid": curso_id, "did": docente_id}).fetchone()
            if ex:
                print(f"✓ Docente already linked to curso {curso_id} ({nombre})")
            else:
                conn.execute(text('INSERT INTO "GrupoCurso" (grupo_id, curso_id, docente_id) VALUES (:gid, :cid, :did)'), {"gid": grupo_id, "cid": curso_id, "did": docente_id})
                print(f"✅ Linked docente to curso {curso_id} ({nombre}) via grupo {grupo_id}")

            # Count students already in this group
            cnt = conn.execute(text('SELECT count(*) FROM "EstudianteGrupo" eg WHERE eg.grupo_id = :gid'), {"gid": grupo_id}).fetchone()[0]
            need = max(0, args.per_course - int(cnt))
            if need <= 0:
                print(f"  - Curso {curso_id} already has {cnt} estudiantes (>= {args.per_course})")
                continue

            print(f"  - Curso {curso_id} has {cnt} estudiantes, creating {need} more...")

            # create 'need' students and enroll
            for i in range(need):
                # generate email unique per course/time
                base = uuid.uuid4().hex[:8]
                cid_short = str(curso_id)[:6]
                email = f"seed_{cid_short}_{base}@test.unan.local"
                username = email.split("@")[0]

                existing = conn.execute(text('SELECT usuario_id FROM "Usuario" WHERE correo_institucional = :email'), {"email": email}).fetchone()
                if existing:
                    usuario_id = existing[0]
                    print(f"    ✓ Usuario already exists: {email} (id={usuario_id})")
                else:
                    usuario_id = str(uuid.uuid4())
                    hashed = pwd.hash_password(args.password)
                    conn.execute(text('INSERT INTO "Usuario" (usuario_id, correo_institucional, username, nombres, apellidos, tipo_documento, numero_documento, rol, password_hash, estado_cuenta, email_verified) VALUES (:uid, :email, :username, :nombres, :apellidos, :tipo_documento, :numero_documento, :rol, :password_hash, :estado_cuenta, :email_verified)'), {"uid": usuario_id, "email": email, "username": username, "nombres": f"Est_{curso_id[:6]}", "apellidos": "Seed", "tipo_documento": "cc", "numero_documento": f"9{base}", "rol": "estudiante", "password_hash": hashed, "estado_cuenta": "activo", "email_verified": True})
                    print(f"    ✅ Created usuario: {email} (id={usuario_id})")

                # ensure Estudiante
                ex_est = conn.execute(text('SELECT estudiante_id FROM "Estudiante" WHERE estudiante_id = :uid'), {"uid": usuario_id}).fetchone()
                if not ex_est:
                    conn.execute(text('INSERT INTO "Estudiante" (estudiante_id, fecha_ingreso) VALUES (:uid, :fecha_ingreso)'), {"uid": usuario_id, "fecha_ingreso": date.today()})
                    print(f"      - Created Estudiante row for {email}")

                # enroll
                link = conn.execute(text('SELECT 1 FROM "EstudianteGrupo" WHERE grupo_id = :gid AND estudiante_id = :uid'), {"gid": grupo_id, "uid": usuario_id}).fetchone()
                if link:
                    print(f"      - Student already enrolled in grupo {grupo_id}")
                else:
                    conn.execute(text('INSERT INTO "EstudianteGrupo" (grupo_id, estudiante_id, fecha_vinculacion) VALUES (:gid, :uid, :fecha)'), {"gid": grupo_id, "uid": usuario_id, "fecha": date.today()})
                    print(f"      - Enrolled {email} into grupo {grupo_id}")

                created.append((email, username, args.password, usuario_id))

    # write CSV file
    with open(csv_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["email", "username", "password", "usuario_id"])
        for rec in created:
            w.writerow(rec)

    print(f"\nCSV written to: {csv_path}")
    print(f"Total cuentas nuevas creadas: {len(created)}")
    if not args.commit:
        print("Nota: no se aplicaron cambios. Reejecute con --commit para persistir.")
    else:
        print("Operación completada con --commit.")


if __name__ == '__main__':
    main()
