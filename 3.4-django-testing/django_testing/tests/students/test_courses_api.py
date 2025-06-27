import pytest
from django.conf import settings
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.reverse import reverse

from students.models import Student, Course


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def course_factory():
    def factory(*args, **kwargs):
        return baker.make(Course, *args, **kwargs)
    return factory


@pytest.fixture
def student_factory():
    def factory(*args, **kwargs):
        return baker.make(Student, *args, **kwargs)
    return factory 


@pytest.mark.django_db
def test_retrieve_course(client, course_factory):
       
    #Arrange
    course = course_factory()
    url = reverse('course-detail', args=[course.id])
    #Act
    response =client.get(url)
    
    #Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.data['id'] == course.id
    assert response.data['name'] == course.name
    
    
@pytest.mark.django_db
def test_list_courses(client, course_factory):
    
    #Arrange
    courses = course_factory(_quantity=3)
    url = reverse('courses-list')
    
    #Act
    response = client.get(url)
    
    #Assert
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == len(courses)
    response_ids = {course['id'] for course in response.data}
    expected_ids = {course.id for course  in courses}
    assert response_ids == expected_ids 
        
        
@pytest.mark.django_db
def test_filter_course_by_id(client, course_factory):
    
    #Arrange
    courses = course_factory(_quantity=3)
    target_course = courses[1]
    url = reverse('courses-list') + f'?id={target_course.id}'
    
    #Act
    response = client.get(url)
    
    #Assert
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['id'] == target_course.id
    
    
@pytest.mark.django_db
def test_filter_course_by_name(client, course_factory):
    
    #Arrange
    courses = course_factory(_quantity=3)
    target_course = courses[1]
    url = reverse('courses-list') + f'?id={target_course.name}'
    
    #Act
    response = client.get(url)
    
    #Assert
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['name'] == target_course.name
    
    
@pytest.mark.django_db
def test_create_course(client):
    
    #Arrange
    url = reverse('courses-list')
    data = {'name': 'New Course'}
    
    #Act
    response = client.post(url, data=data, format='json')
    
    #Assert
    assert response.status_code == status.HTTP_201_CREATED
    assert Course.objects.count() == 1
    assert Course.objects.get().name == data['name']
    
    
@pytest.mark.django_db
def test_update_course(client, course_factory):
    
    #Arrange
    course = course_factory()
    url = reverse('courses-detail', args=[course.id])
    data = {'name': 'Updated Name'}
    
    #Act
    response = client.patch(url, data=data, format='json')
    
    #Assert
    assert response.status_code == status.HTTP_200_OK
    course.refresh_from_db()
    assert course.name == data['name']
    
    
@pytest.mark.django_db
def test_delete_course(client, course_factory):
    
    #Arrange
    course = course_factory()
    url = reverse('courses-detail', args=[course.id])
    
    #Act
    response = client.delete(url)
    
    #Assert
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Course.objects.count() == 0
    
    
@pytest.mark.django_db
def test_course_with_students(client, course_factory, student_factory):
    
    #Arrange
    students = student_factory(_quantity=3)
    course = course_factory(students=students)
    url = reverse('courses-detail', args=[course.id])
    
    #Act
    response = client.get(url)
    
    #Assert
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['students']) == len(students)
    response_student_ids = set(response.data['students'])
    expected_student_ids = {student.id for student in students}
    assert response_student_ids == expected_student_ids 
        
        
@pytest.mark.django_db
@pytest.mark.parametrize(
    'max_students,student_count,expected_status',
    [
        (5, 5, status.HTTP_201_CREATED),
        (5, 6, status.HTTP_400_BAD_REQUEST)
    ]
)
def test_max_students_per_course(
    client, student_factory, settings, max_students, student_count, expected_status
):
    settings.MAX_STUDENTS_PER_COURSE = max_students
    students = student_factory(_quantity=student_count)
    student_ids = [student.id for student in students]
    url = reverse('courses-list')
    data = {
        'name': 'Test Course',
        'students': student_ids
    }
    response = client.post(url, data=data, format='json')
    assert response.status_code == expected_status
    if expected_status == status.HTTP_201_CREATED:
        assert Course.objects.count() == 1
        assert Course.objects.first().students.count() == student_count
    else:
        assert 'На курсе не может быть больше чем' in str(response.data['students'][0])
        
        
@pytest.mark.django_db
def test_add_students_to_existing_course(client, student_factory, course_factory, settings):
    settings.MAX_STUDENTS_PER_COURSE = 3
    students = student_factory(_quantity=2)
    course = course_factory(students=students)
    new_student = student_factory()
    url = reverse('courses-detail', args=[course.id])
    data = {
        'students': [student.id for student in students] + [new_student.id]
    }
    response = client.patch(url, data=data, format='json')
    assert response.status_code == status.HTTP_200_OK
    course.refresh_from_db()
    assert course.students.count() == 3
    another_student = student_factory()
    data['students'].append(another_student.id)
    response = client.patch(url, data=data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'На курсе не может быть больше чем' in str(response.data['students'][0])
    course.refresh_from_db()
    assert course.students.count() == 3