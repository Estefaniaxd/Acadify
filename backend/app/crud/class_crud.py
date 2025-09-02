# backend/app/crud/class_crud.py
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.crud.base import CRUDBase
from app.models.class_model import Class, Attendance, AttendanceStatus
from app.models.group import GroupCourse, StudentGroup, StudentGroupStatus
from app.schemas.class_schema import ClassCreate, ClassUpdate
import uuid

class CRUDClass(CRUDBase[Class, ClassCreate, ClassUpdate]):
    """CRUD para gestión de clases"""
    
    def create_with_group_course(
        self, 
        db: Session, 
        *, 
        obj_in: ClassCreate, 
        group_course_id: uuid.UUID
    ) -> Class:
        """Crea una clase y la asigna a un grupo-curso"""
        group_course = db.query(GroupCourse).filter(GroupCourse.id == group_course_id).first()
        if not group_course:
            raise ValueError("Grupo-curso no encontrado")
        
        if obj_in.start_time < datetime.utcnow():
            raise ValueError("La fecha de inicio no puede ser en el pasado")
        
        db_obj = Class(**obj_in.dict(), group_course_id=group_course_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        self._create_attendance_records(db, db_obj)
        return db_obj
    
    def _create_attendance_records(self, db: Session, class_obj: Class) -> None:
        """Crea registros de asistencia para todos los estudiantes activos del grupo"""
        student_groups = db.query(StudentGroup).filter(
            StudentGroup.group_id == class_obj.group_course.group_id,
            StudentGroup.status == StudentGroupStatus.ACTIVE
        ).all()
        
        for sg in student_groups:
            db.add(Attendance(
                class_id=class_obj.id,
                student_id=sg.student_id,
                status=AttendanceStatus.ABSENT
            ))
        db.commit()
    
    def get_by_group_course(self, db: Session, *, group_course_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Class]:
        return db.query(Class).filter(Class.group_course_id == group_course_id)\
            .order_by(Class.start_time.asc()).offset(skip).limit(limit).all()
    
    def get_by_teacher(self, db: Session, *, teacher_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Class]:
        return db.query(Class).join(GroupCourse).filter(GroupCourse.teacher_id == teacher_id)\
            .order_by(Class.start_time.asc()).offset(skip).limit(limit).all()
    
    def get_upcoming_classes(
        self, db: Session, *, teacher_id: Optional[uuid.UUID] = None, student_id: Optional[uuid.UUID] = None,
        days_ahead: int = 7, skip: int = 0, limit: int = 100
    ) -> List[Class]:
        start = datetime.utcnow()
        end = start + timedelta(days=days_ahead)
        query = db.query(Class).filter(Class.start_time.between(start, end))
        
        if teacher_id:
            query = query.join(GroupCourse).filter(GroupCourse.teacher_id == teacher_id)
        if student_id:
            query = query.join(GroupCourse).join(StudentGroup).filter(
                StudentGroup.student_id == student_id,
                StudentGroup.status == StudentGroupStatus.ACTIVE
            )
        return query.order_by(Class.start_time.asc()).offset(skip).limit(limit).all()
    
    def mark_attendance(self, db: Session, *, class_id: uuid.UUID, student_id: uuid.UUID, status: AttendanceStatus) -> Attendance:
        attendance = db.query(Attendance).filter(
            Attendance.class_id == class_id,
            Attendance.student_id == student_id
        ).first()
        if not attendance:
            raise ValueError("Registro de asistencia no encontrado")
        attendance.status = status
        db.commit()
        db.refresh(attendance)
        return attendance
    
    def get_class_attendance(self, db: Session, *, class_id: uuid.UUID) -> List[Attendance]:
        return db.query(Attendance).filter(Attendance.class_id == class_id).all()
    
    def get_student_attendance_in_course(self, db: Session, *, student_id: uuid.UUID, group_course_id: uuid.UUID) -> List[Attendance]:
        return db.query(Attendance).join(Class).filter(
            Attendance.student_id == student_id,
            Class.group_course_id == group_course_id
        ).order_by(Class.start_time.asc()).all()
    
    def calculate_attendance_percentage(self, db: Session, *, student_id: uuid.UUID, group_course_id: uuid.UUID) -> float:
        attendances = self.get_student_attendance_in_course(db, student_id=student_id, group_course_id=group_course_id)
        if not attendances:
            return 0.0
        present_count = sum(1 for a in attendances if a.status in [AttendanceStatus.PRESENT, AttendanceStatus.JUSTIFIED])
        return round((present_count / len(attendances)) * 100, 2)
    
    def get_class_statistics(self, db: Session, *, class_id: uuid.UUID) -> dict:
        class_obj = self.get(db, id=class_id)
        if not class_obj:
            raise ValueError("Clase no encontrada")
        
        attendances = self.get_class_attendance(db, class_id=class_id)
        total = len(attendances)
        present = sum(1 for a in attendances if a.status == AttendanceStatus.PRESENT)
        justified = sum(1 for a in attendances if a.status == AttendanceStatus.JUSTIFIED)
        absent = sum(1 for a in attendances if a.status == AttendanceStatus.ABSENT)
        attendance_percentage = ((present + justified) / total * 100) if total > 0 else 0
        
        return {
            "total_students": total,
            "present_students": present,
            "justified_students": justified,
            "absent_students": absent,
            "attendance_percentage": round(attendance_percentage, 2),
            "materials_count": len(class_obj.class_materials),
            "assignments_count": len(class_obj.assignments),
            "teacher_name": f"{class_obj.group_course.teacher.user.first_names} {class_obj.group_course.teacher.user.last_names}",
            "course_name": class_obj.group_course.course.name,
            "group_name": class_obj.group_course.group.name
        }
    
    def cancel_class(self, db: Session, *, class_id: uuid.UUID, reason: Optional[str] = None) -> Class:
        class_obj = self.get(db, id=class_id)
        if not class_obj:
            raise ValueError("Clase no encontrada")
        note = "CLASE CANCELADA" + (f" - Razón: {reason}" if reason else "")
        class_obj.description = f"{note}\n\n{class_obj.description}" if class_obj.description else note
        db.commit()
        db.refresh(class_obj)
        return class_obj
    
    def reschedule_class(self, db: Session, *, class_id: uuid.UUID, new_start_time: datetime, new_duration: Optional[timedelta] = None) -> Class:
        class_obj = self.get(db, id=class_id)
        if not class_obj:
            raise ValueError("Clase no encontrada")
        if new_start_time < datetime.utcnow():
            raise ValueError("La nueva fecha no puede ser en el pasado")
        class_obj.start_time = new_start_time
        if new_duration:
            class_obj.duration = new_duration
        db.commit()
        db.refresh(class_obj)
        return class_obj

# Instancia del CRUD
class_crud = CRUDClass(Class)
