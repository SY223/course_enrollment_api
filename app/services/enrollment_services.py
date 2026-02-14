from fastapi import Depends, HTTPException
from uuid import uuid4, UUID
from typing import List
from app.core.db import users_db, courses_db, enrollments_db
from app.schemas.enrollment_schema import EnrollmentCreate, EnrollmentDetails, EnrollmentResponse, EnrollmentRequest
from app.api.deps import is_student_user
from app.schemas.course_schema import CourseResponse
from app.schemas.user_schema import UserRole, UserResponse
from app.services.user_services import UserService
from datetime import datetime, timezone

class EnrollmentService:
    @staticmethod
    def enroll_student(user_id: UUID, course_id: UUID):
        user = users_db.get(user_id)
        if not user:
            raise ValueError("User does not exist")
        course = courses_db.get(course_id)
        if not course:
            raise ValueError("Course does not exist")
        #prevent duplicate enrollment
        for e in enrollments_db.values():
            if e.user_id == user.id and e.course_id == course.id:
                raise ValueError("Student is already enrolled in this course")
        new_id = uuid4()
        enrollment_in_db = EnrollmentResponse(
            id=new_id,
            user_id=user.id,
            course_id=course.id,
            enrolled_on=datetime.now(timezone.utc)
        )
        enrollments_db[enrollment_in_db.id] = enrollment_in_db
        enrollment_details = EnrollmentDetails(
            id=new_id,
            student=user,
            course=course,
            enrolled_on=datetime.now(timezone.utc)
        )
        return enrollment_details

    @staticmethod
    def retrieve_student_enrollments(user_id: UUID) -> List[CourseResponse]:
        user = users_db.get(user_id)
        if not user:
            raise ValueError("User does not exist")
        if user.role != UserRole.STUDENT:
            raise ValueError("Only students can enroll in courses")
        results: List[Dict] = []
        for enrollment_id, enrollment in enrollments_db.items():
            if isinstance(enrollment, dict): 
                stored_user_id = enrollment.get("user_id") 
                stored_course_id = enrollment.get("course_id")
            else:
                stored_user_id = getattr(enrollment, "user_id", None) 
                stored_course_id = getattr(enrollment, "course_id", None)
            if stored_user_id is None or str(stored_user_id) != str(user_id):
                continue
            course = courses_db.get(stored_course_id) or courses_db.get(str(stored_course_id)) 
            if not course: 
                continue
            results.append({
                "enrollment_id": enrollment_id,
                "course": course
            })
        if not results:
            raise ValueError("No enrollments found")
        return results

    @staticmethod
    def student_deregister(
        user_id: UUID,
        course_id: UUID,
        role=Depends(is_student_user)
    ):
        user = users_db.get(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User does not exist")
        
        course = courses_db.get(course_id)
        for e in enrollments_db.values():
            if e.user_id != user_id and e.course_id!=course_id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You are not enrolled on this course")
            del enrollments_db[e.id]
            return {
                "message": "Successfully deregister from the course."
            }
        
    @staticmethod
    def admin_retrieve_enrollments() -> List[EnrollmentDetails]:
        results: List[EnrollmentDetails] = []
        for enrollment in enrollments_db.values():
            student = users_db.get(enrollment.user_id)
            course = courses_db.get(enrollment.course_id)
            if not student or not course: 
                continue 
            results.append(EnrollmentDetails(
                id=enrollment.id, 
                student=student, 
                course=course, 
                enrolled_on=enrollment.enrolled_on
            ))
        return results
    
    @staticmethod
    def admin_retrieve_course_enrollments(course_id: UUID):
        results = []
        course = courses_db.get(course_id)
        if not course:
            raise ValueError("Course does not exist")
        for enrollment in enrollments_db.values():
            if enrollment.course_id != course_id:
                continue
            student = users_db.get(enrollment.user_id)
            if not student:
                continue
            results.append(
                EnrollmentDetails(
                    id=enrollment.id,
                    student=student,
                    course=course,
                    enrolled_on=enrollment.enrolled_on
                )
            )
        return results

    @staticmethod
    def admin_force_deregister(user_id: UUID, course_id: UUID):
        student = users_db.get(user_id)
        if not student:
            raise ValueError("Student does not exist")
        course = courses_db.get(course_id)
        if not course:
            raise ValueError("Course does not exist")
        
        for enrollment in list(enrollments_db.values()):
            if enrollment.user_id == user_id and enrollment.course_id == course_id:
                del enrollments_db[enrollment.id]
                return {"message": "Student successfully deregistered by admin."}
        raise ValueError("Enrollment not found")


            
