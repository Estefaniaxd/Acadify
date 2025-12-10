"""Seed script: create student users and link a docente to all UNAN courses.

Usage (dry-run by default):
  python seed_students_and_link_docente_unan.py --docente-email juan@example.com --curso-id d45bc3a9-d7d2-4bb6-a461-dad2a42cd98e --count 30 --password Juanito243019@ --commit

By default the script runs in safe (no-commit) mode and prints what it would do.
Add --commit to persist changes.

This script is idempotent: it checks for existing users, estudiantes, grupos and links
before creating them.
"""

import argparse
import csv
from datetime import date
import uuid

import sys

sys.path.insert(0, "src")
import src.models  # Ensure all model modules are imported so SQLAlchemy mappers are configured

from src.db.session import SessionLocal
from src.services.auth.password_service import PasswordService
from src.models.users.usuario import Usuario
from src.models.users.estudiante import Estudiante
from src.models.users.docente import Docente
from src.models.academic.curso import Curso
from src.models.academic.grupo import Grupo
from src.models.academic.grupo_curso import GrupoCurso
from src.models.academic.estudiante_grupo import EstudianteGrupo


def find_unan_courses(db):
    # Find courses whose institucion name or sigla contains 'UNAN' (case-insensitive)
    return (
        db.query(Curso)
        .join(Curso.institucion)
        .filter(Curso.institucion.has())
        .filter("LOWER(Institucion.nombre) LIKE '%unan%' OR LOWER(Institucion.sigla) LIKE '%unan%'")
        .all()
    )


def main():
    parser = argparse.ArgumentParser(description="Seed students and link docente to UNAN courses")
    parser.add_argument("--docente-email", required=True, help="Email of the docente to link")
    parser.add_argument("--curso-id", required=False, help="Curso id to enroll students into")
    parser.add_argument("--count", type=int, default=30, help="Number of students to create")
    parser.add_argument("--password", default="Juanito243019@", help="Plain password for created students")
    parser.add_argument("--commit", action="store_true", help="Persist changes to DB")

    args = parser.parse_args()

    db = SessionLocal()
    pwd_svc = PasswordService()

    created_accounts = []

    try:
        # 1) Locate or create docente user
        docente_user = db.query(Usuario).filter(Usuario.correo_institucional == args.docente_email).first()
        if not docente_user:
            print(f"❗ Docente user with email {args.docente_email} not found. Please create the docente Usuario first.")
            print("Exiting.")
            return

        # Ensure Docente row exists
        docente = db.query(Docente).filter(Docente.docente_id == docente_user.usuario_id).first()
        if not docente:
            print(f"Docente row missing for usuario {docente_user.usuario_id}, creating minimal Docente record.")
            docente = Docente(
                docente_id=docente_user.usuario_id,
                area_conocimiento="General",
                fecha_vinculacion=date.today(),
            )
            db.add(docente)
            if args.commit:
                db.commit()
                db.refresh(docente)

        # 2) Find target course for students
        target_course = None
        if args.curso_id:
            target_course = db.query(Curso).filter(Curso.curso_id == uuid.UUID(args.curso_id)).first()
            if not target_course:
                print(f"⚠️ Curso with id {args.curso_id} not found. Students will not be enrolled unless you provide a valid curso-id.")

        # 3) Create students and enroll into target course (if given)
        for i in range(1, args.count + 1):
            email = f"estudiante{i:03d}@test.unan.local"
            username = f"estudiante{i:03d}"

            existing = db.query(Usuario).filter(Usuario.correo_institucional == email).first()
            if existing:
                print(f"✓ Usuario already exists: {email} (id={existing.usuario_id})")
                usuario = existing
            else:
                usuario = Usuario(
                    usuario_id=uuid.uuid4(),
                    correo_institucional=email,
                    username=username,
                    nombres=f"Estudiante {i}",
                    apellidos="Seed",
                    tipo_documento="cc",
                    numero_documento=f"100000{i:03d}",
                    rol="estudiante",
                    password_hash=pwd_svc.hash_password(args.password),
                    estado_cuenta="activo",
                    email_verified=True,
                )
                db.add(usuario)
                if args.commit:
                    db.commit()
                    db.refresh(usuario)
                print(f"✅ Created usuario: {email}")

            # Ensure Estudiante row
            estudiante = db.query(Estudiante).filter(Estudiante.estudiante_id == usuario.usuario_id).first()
            if not estudiante:
                estudiante = Estudiante(estudiante_id=usuario.usuario_id, fecha_ingreso=date.today())
                db.add(estudiante)
                if args.commit:
                    db.commit()
                    db.refresh(estudiante)
                print(f"  - Created Estudiante row for {email}")

            # Enroll into course group if requested
            if target_course:
                # Find an existing GrupoCurso for target_course, else create a new Grupo and GrupoCurso
                grupo_curso = None
                # Try to find any grupo for this course
                if target_course.grupo_cursos:
                    grupo = target_course.grupo_cursos[0].grupo
                else:
                    # create a new Grupo
                    grupo = Grupo(
                        grupo_id=uuid.uuid4(),
                        nombre=f"Grupo_seed_{target_course.curso_id.hex[:6]}",
                    )
                    db.add(grupo)
                    if args.commit:
                        db.commit()
                        db.refresh(grupo)
                    # link grupo to course with a GrupoCurso (using docente if available)
                    curso_docente_id = docente.docente_id if docente else None
                    grupo_curso = GrupoCurso(grupo_id=grupo.grupo_id, curso_id=target_course.curso_id, docente_id=curso_docente_id)
                    db.add(grupo_curso)
                    if args.commit:
                        db.commit()
                        db.refresh(grupo_curso)

                # Ensure EstudianteGrupo linking
                existing_link = (
                    db.query(EstudianteGrupo)
                    .filter(EstudianteGrupo.grupo_id == grupo.grupo_id)
                    .filter(EstudianteGrupo.estudiante_id == estudiante.estudiante_id)
                    .first()
                )
                if existing_link:
                    print(f"  - Student already enrolled in grupo {grupo.grupo_id}")
                else:
                    enlace = EstudianteGrupo(grupo_id=grupo.grupo_id, estudiante_id=estudiante.estudiante_id, fecha_vinculacion=date.today())
                    db.add(enlace)
                    if args.commit:
                        db.commit()
                    print(f"  - Enrolled {email} into grupo {grupo.grupo_id}")

            created_accounts.append((email, username, args.password, str(usuario.usuario_id)))

        # 4) Link docente to all UNAN courses
        # We'll look for cursos where institucion.nombre or sigla contains 'unan'
        unan_cursos = (
            db.query(Curso)
            .join(Curso.institucion)
            .filter("LOWER(Institucion.nombre) LIKE '%unan%' OR LOWER(Institucion.sigla) LIKE '%unan%'")
            .all()
        )

        if not unan_cursos:
            print("⚠️ No se encontraron cursos para Institución UNAN (nombre/sigla). Skipping docente linking.")
        else:
            print(f"Found {len(unan_cursos)} UNAN course(s). Linking docente {docente_user.correo_institucional}...")
            for curso in unan_cursos:
                # Find any GrupoCurso where curso_id == curso.curso_id and docente_id == docente.docente_id
                existing = (
                    db.query(GrupoCurso)
                    .filter(GrupoCurso.curso_id == curso.curso_id)
                    .filter(GrupoCurso.docente_id == docente.docente_id)
                    .first()
                )
                if existing:
                    print(f"✓ Docente already linked to curso {curso.curso_id} ({curso.nombre})")
                    continue

                # If course has groups, attach to first group's grupo_id; else create a new Grupo
                if curso.grupo_cursos and len(curso.grupo_cursos) > 0:
                    grupo = curso.grupo_cursos[0].grupo
                else:
                    grupo = Grupo(grupo_id=uuid.uuid4(), nombre=f"Grupo_doc_{curso.curso_id.hex[:6]}")
                    db.add(grupo)
                    if args.commit:
                        db.commit()
                        db.refresh(grupo)

                grupo_curso = GrupoCurso(grupo_id=grupo.grupo_id, curso_id=curso.curso_id, docente_id=docente.docente_id)
                db.add(grupo_curso)
                if args.commit:
                    db.commit()
                print(f"✅ Linked docente to curso {curso.curso_id} ({curso.nombre}) via grupo {grupo.grupo_id}")

        # Print CSV summary
        print("\n--- CREADOS / EXISTENTES (email, username, password, usuario_id) ---")
        writer = csv.writer(sys.stdout)
        writer.writerow(["email", "username", "password", "usuario_id"])  # header
        for rec in created_accounts:
            writer.writerow(rec)

        if not args.commit:
            print("\nNota: No se guardaron cambios en la base de datos. Ejecute con --commit para aplicar las operaciones.")

    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
