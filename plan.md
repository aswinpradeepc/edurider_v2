I want to design and implement the backend system for a school bus management system which has the follwing features.

1. live location sharing with parent's phone - during a trip
2. student location based fleet management - cluster the students based on nearby location and then find the optimised path between them and the school with mapbox api.

I plan to use Django as a backend and flutter as frontend. Seperate apps for driver and parent. Django admin as admin interface for school administration.

The tables I roughly planned for the project are

Student:
    Name
    class
    phone number
    email
    address text
    coordinates (Take gmaps link and then get coordinates from it - even if its shortlink)
    Guardian Name
    route_id(foreignkey - added according to the cluster he is in and there by the route he is assigned.)
    student_id

Attendance:
    Student_id:
    Date:
    presence: boolean

Driver:
    name
    licence_no
    phone_number
    email
    Bus_no
    driver_current_location:( active during trip - will be considered as live trip location.)
    driver_id

Routes:
    to_school(boolean - if the trip is to take students to school or vice versa)
    list of 40 students clustered according to their location - if they are nearby
    order of route - optimised path the bus should follow (1. student_coordinates, 2. next student_coordinates and ...... School)
    driver_id (foreignkey - id of driver who is taking the trip)
    current_location(driver_current_location)


the flow is, in the django admin, admin can enter students and drivers. When the admin click on a button in admin  page to optimise route, k-means clustering algorithm is run on all present Student's student_coordinates to make clusters of 40. Then this along with school coordinates are sent to mapbox api and optimised route is found and stored. This function is automatically run before each trip - on 7am every morning and 2pm every evening.

the API endpoints are:

GET
/students/<student_id>
    response:
        name:
        class
        Guardian_name
        email
        phone
        address
        driver
        route_id
        presence

POST
/students/presence
    request_body:
        presence: value
        student_id: value

GET
/driver/<id>
    response:
        licence_no
        email
        phone_number
        route_id

GET
/route/<id>
    response:
        list of students
        driver
        order of routes and coordinates
        
POST
/students/<student_id>/coordintates
    request_body:
        link:
        
SOCKET -
Driver - streams his live location when trip is active
Student/Parent APP - subscribes to the live location of driver

