"""Seed students and link docente to UNAN courses using raw SQL (avoids ORM mapper issues).

Usage (dry-run by default):
  cd /run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify
  timeout 60s env PYTHONPATH=backend python -u backend/scripts/seed_students_and_link_docente_unan_sql.py --docente-email juan@example.com --curso-id <curso-uuid> --count 30

Add --commit to persist changes.
"""

import argparse
import csv
from datetime import date
import uuid
import sys

sys.path.insert(0, "backend")

from sqlalchemy import create_engine, text
from src.core.config import settings
from src.services.auth.password_service import PasswordService


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--docente-email", required=True)
    parser.add_argument("--curso-id")
    parser.add_argument("--count", type=int, default=30)
    parser.add_argument("--password", default="Juanito243019@")
    parser.add_argument("--commit", action="store_true")

    args = parser.parse_args()

    engine = create_engine(settings.database_url)
    pwd = PasswordService()

    created = []

    # Use a transactional context so we can commit/rollback explicitly.
    # engine.begin() opens a connection and begins a transaction which will
    # be committed on successful exit of the block, or rolled back on error.
    with engine.begin() as conn:
        # find docente usuario
        r = conn.execute(
            text('SELECT usuario_id FROM "Usuario" WHERE correo_institucional = :email'),
            {"email": args.docente_email},
        ).fetchone()

        if not r:
            print(f"❗ Docente user with email {args.docente_email} not found in Usuario table. Aborting.")
            return

        docente_id = r[0]
        print(f"Docente usuario_id: {docente_id}")

        # target course
        target_course = None
        if args.curso_id:
            r = conn.execute(
                text('SELECT curso_id FROM "Curso" WHERE curso_id = :cid'), {"cid": args.curso_id}
            ).fetchone()
            if r:
                target_course = args.curso_id
                print(f"Target curso found: {target_course}")
            else:
                print(f"⚠️ Curso id {args.curso_id} not found. Students will not be enrolled.")

        # create students
        for i in range(1, args.count + 1):
            email = f"estudiante{i:03d}@test.unan.local"
            username = f"estudiante{i:03d}"

            existing = conn.execute(
                text('SELECT usuario_id FROM "Usuario" WHERE correo_institucional = :email'), {"email": email}
            ).fetchone()

            if existing:
                usuario_id = existing[0]
                print(f"✓ Usuario already exists: {email} (id={usuario_id})")
            else:
                usuario_id = str(uuid.uuid4())
                hashed = pwd.hash_password(args.password)
                conn.execute(
                    text(
                        'INSERT INTO "Usuario" (usuario_id, correo_institucional, username, nombres, apellidos, tipo_documento, numero_documento, rol, password_hash, estado_cuenta, email_verified) VALUES (:uid, :email, :username, :nombres, :apellidos, :tipo_documento, :numero_documento, :rol, :password_hash, :estado_cuenta, :email_verified)'
                    ),
                    {
                        "uid": usuario_id,
                        "email": email,
                        "username": username,
                        "nombres": f"Estudiante {i}",
                        "apellidos": "Seed",
                        "tipo_documento": "cc",
                        "numero_documento": f"100000{i:03d}",
                        "rol": "estudiante",
                        "password_hash": hashed,
                        "estado_cuenta": "activo",
                        "email_verified": True,
                    },
                )
                print(f"✅ Created usuario: {email} (id={usuario_id})")

            # Ensure Estudiante row
            ex_est = conn.execute(
                text('SELECT estudiante_id FROM "Estudiante" WHERE estudiante_id = :uid'), {"uid": usuario_id}
            ).fetchone()
            if not ex_est:
                conn.execute(
                    text('INSERT INTO "Estudiante" (estudiante_id, fecha_ingreso) VALUES (:uid, :fecha_ingreso)'),
                    {"uid": usuario_id, "fecha_ingreso": date.today()},
                )
                print(f"  - Created Estudiante row for {email}")

            # Enroll into target course group if requested
            if target_course:
                # find existing grupo linked to course
                grp = conn.execute(
                    text('SELECT gc.grupo_id FROM "GrupoCurso" gc WHERE gc.curso_id = :cid LIMIT 1'), {"cid": target_course}
                ).fetchone()
                if grp:
                    grupo_id = grp[0]
                else:
                    grupo_id = str(uuid.uuid4())
                    conn.execute(
                        text('INSERT INTO "Grupo" (grupo_id, nombre) VALUES (:gid, :nombre)'),
                        {"gid": grupo_id, "nombre": f"Grupo_seed_{target_course[:8]}"},
                    )
                    # link grupo to course
                    conn.execute(
                        text('INSERT INTO "GrupoCurso" (grupo_id, curso_id, docente_id) VALUES (:gid, :cid, :did)'),
                        {"gid": grupo_id, "cid": target_course, "did": docente_id},
                    )
                    print(f"  - Created grupo {grupo_id} and linked to curso {target_course}")

                # ensure EstudianteGrupo
                link = conn.execute(
                    text('SELECT 1 FROM "EstudianteGrupo" WHERE grupo_id = :gid AND estudiante_id = :uid'), {"gid": grupo_id, "uid": usuario_id}
                ).fetchone()
                if link:
                    print(f"  - Student already enrolled in grupo {grupo_id}")
                else:
                    conn.execute(
                        text('INSERT INTO "EstudianteGrupo" (grupo_id, estudiante_id, fecha_vinculacion) VALUES (:gid, :uid, :fecha)'),
                        {"gid": grupo_id, "uid": usuario_id, "fecha": date.today()},
                    )
                    print(f"  - Enrolled {email} into grupo {grupo_id}")

            created.append((email, username, args.password, usuario_id))

        # Link docente to UNAN courses
        unan = conn.execute(
            text(
                'SELECT c.curso_id, c.nombre FROM "Curso" c JOIN "Institucion" i ON c.institucion_id = i.institucion_id WHERE LOWER(i.nombre) LIKE :pat OR LOWER(i.sigla) LIKE :pat'
            ),
            {"pat": "%unan%"},
        ).fetchall()

        if not unan:
            print("⚠️ No UNAN courses found. Skipping linking.")
        else:
            print(f"Found {len(unan)} UNAN course(s). Linking docente {args.docente_email}...")
            for curso_id, nombre in unan:
                # check existing GrupoCurso with this docente
                ex = conn.execute(
                    text('SELECT grupo_curso_id FROM "GrupoCurso" WHERE curso_id = :cid AND docente_id = :did'),
                    {"cid": curso_id, "did": docente_id},
                ).fetchone()
                if ex:
                    print(f"✓ Docente already linked to curso {curso_id} ({nombre})")
                    continue

                # find or create grupo
                grp = conn.execute(
                    text('SELECT gc.grupo_id FROM "GrupoCurso" gc WHERE gc.curso_id = :cid LIMIT 1'), {"cid": curso_id}
                ).fetchone()
                if grp:
                    grupo_id = grp[0]
                else:
                    grupo_id = str(uuid.uuid4())
                    conn.execute(
                        text('INSERT INTO "Grupo" (grupo_id, nombre) VALUES (:gid, :nombre)'),
                        {"gid": grupo_id, "nombre": f"Grupo_doc_{curso_id[:8]}"},
                    )
                    print(f"  - Created grupo {grupo_id} for curso {curso_id}")

                conn.execute(
                    text('INSERT INTO "GrupoCurso" (grupo_id, curso_id, docente_id) VALUES (:gid, :cid, :did)'),
                    {"gid": grupo_id, "cid": curso_id, "did": docente_id},
                )
                print(f"✅ Linked docente to curso {curso_id} ({nombre}) via grupo {grupo_id}")

        # summary
        print("\n--- CREADOS / EXISTENTES (email, username, password, usuario_id) ---")
        w = csv.writer(sys.stdout)
        w.writerow(["email", "username", "password", "usuario_id"])  # header
        for rec in created:
            w.writerow(rec)

        if not args.commit:
            print("\nNota: No se aplicaron cambios en la base de datos. Reejecute con --commit para persistir las operaciones.")
        else:
            print("\nCambios aplicados con --commit.")


if __name__ == "__main__":
    main()
