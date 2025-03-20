# 🚌 **School Bus Management System - Backend Plan**

## 🎯 **AIM:**

To design and implement a Django-based backend system for managing school bus trips, enabling:
- **Student location-based fleet optimization.**
- **Live driver location streaming to parents.**
- **Attendance tracking per trip.**
- **Google OAuth login for drivers, parents, and admins.**
- **Admin interface for managing students, drivers, and trip routes.**

---

## 📑 **TABLES:**

### 1. **Student**
| Field              | Type        | Description                                       |
|--------------------|------------|---------------------------------------------------|
| student_id         | UUID/PK    | Unique ID                                         |
| name               | Text       |                                                   |
| class              | Text/Enum  |                                                   |
| phone_number       | Text       |                                                   |
| email              | Text       |                                                   |
| address_text       | Text       |                                                   |
| coordinates        | PointField | Collected manually (via Google Maps link)         |
| guardian_name      | Text       |                                                   |
| route_plan_id      | FK         | FK to RoutePlan (nullable, assigned dynamically)  |

---

### 2. **Driver**
| Field                    | Type        | Description                  |
|-------------------------|------------|------------------------------|
| driver_id               | UUID/PK    | Unique ID                    |
| name                    | Text       |                              |
| licence_no              | Text       |                              |
| phone_number            | Text       |                              |
| email                   | Text       |                              |
| bus_no                  | Text       |                              |
| driver_current_location | PointField | Updated via WebSocket        |

---

### 3. **RoutePlan (Trip)**
| Field            | Type        | Description                                    |
|------------------|------------|------------------------------------------------|
| route_plan_id    | UUID/PK    | Unique ID                                      |
| trip_date        | Date       | Date of the trip                               |
| start_time       | Time       | Trip start time                                |
| end_time         | Time       | Trip end time                                  |
| status           | Enum       | Pending / Active / Completed / Cancelled       |
| to_school        | Boolean    | True (to school) / False (from school)         |
| total_distance   | Float      | Distance from Mapbox API                       |
| driver_id        | FK         | FK to Driver                                   |
| student_list     | Array of FK| List of assigned Students                      |
| route_order      | JSON/Text  | Ordered stops (coordinates) from Mapbox API    |

---

### 4. **Attendance**
| Field        | Type    | Description                               |
|-------------|--------|-------------------------------------------|
| attendance_id| UUID/PK| Primary Key                               |
| student_id   | FK     | FK to Student                             |
| trip_id      | FK     | FK to RoutePlan                           |
| date         | Date   |                                           |
| presence     | Boolean|                                           |

---

---

## 🌐 **ENDPOINTS:**

Here’s a cleaned up & corrected **Authentication section** of your doc, addressing the parent/driver Google OAuth check logic, adding clarity on security, and aligning endpoints properly:

---

## 🌐 **Authentication Endpoints**

| Endpoint                                 | Method | Description                                                             |
|------------------------------------------|--------|-------------------------------------------------------------------------|
| `/auth/parent/google-login/`             | POST   | Google OAuth login for Parents. Checks if email exists in Student DB.   |
| `/auth/driver/google-login/`             | POST   | Google OAuth login for Drivers. Checks if email exists in Driver DB.    |
| `/auth/google/callback/`                 | GET    | OAuth callback endpoint, handles token generation post verification.    |
| `/auth/logout/`                          | POST   | Logout & revoke token/session.                                          |

---

## 🔒 **Authentication Flow:**

### **1. Google OAuth Initiation:**
- **Parents →** `/auth/parent/google-login/`
- **Drivers →** `/auth/driver/google-login/`

Both trigger standard Google OAuth authentication.

---

### **2. Verification & Authorization:**

| Step | Action |
|------|-------|
| 1    | Receive authenticated Google email after OAuth. |
| 2    | **Parents Endpoint:** Check if email exists in pre-registered **Student's guardian email field**. |
| 3    | **Drivers Endpoint:** Check if email exists in **Driver table**. |
| 4    | If exists → Issue token/session. |
| 5    | If not found → Reject login with `403 Forbidden`. |

**➤ No auto-user creation allowed. Only pre-registered users (added by admin) can log in.**

---

### **4. Logout:**
- `/auth/logout/` → Blacklists token / clears session.

---

### **Student**
| Endpoint                   | Method | Description                              |
|----------------------------|--------|------------------------------------------|
| `/students/<student_id>`    | GET    | Get student details                      |
| `/students/presence/`       | POST   | Mark presence/absence (by guardian/student app only)  |

---

### **Driver**
| Endpoint               | Method | Description                          |
|------------------------|--------|--------------------------------------|
| `/driver/<id>`          | GET    | Get driver details                   |

---

### **RoutePlan (Trip)**
| Endpoint            | Method | Description                                         |
|---------------------|--------|-----------------------------------------------------|
| `/route/<id>`        | GET    | Get route plan details                              |
| `/route/optimize/`   | POST   | Trigger route optimization (admin-only)             |

---

### **WebSocket:**
| WebSocket Endpoint                            | Description                                         |
|-----------------------------------------------|-----------------------------------------------------|
| `/ws/driver-location/<trip_id>/`              | Driver streams location                             |
| `/ws/parent-subscribe/<student_id>/`          | Parent subscribes to bus location                   |

---

---

## 🧩 **DJANGO MODULES (Apps):**

1. **authapp**  
   - Handles Google OAuth login for student/parents and drivers
   - Manages user roles and permissions.

2. **students**
   - CRUD operations for students.
   - Address, coordinates storage.

3. **drivers**
   - CRUD for drivers.
   - WebSocket streaming endpoint for live location.

4. **routes**
   - RoutePlan management.
   - Route optimization logic using clustering + Mapbox API.

5. **attendance**
   - Attendance tracking per trip.

6. **notifications (V2)**
   - Notify parents when bus is near (via Firebase/OneSignal).

7. **live_tracking**
   - WebSocket integration using Django Channels.
   - Authentication checks for location streams.

8. **admin_interface**
   - Custom admin map interface (optional, can extend existing Django admin).

---

---

## 📋 **TODO LIST (Order of Implementation):**

### **Phase 1 (Core Models & Auth)**

1. **Set up Django project, PostgreSQL database.**
2. Create **users app**:
   - Implement Google OAuth.
   - User roles (parent, driver, admin).

3. Create **students app**:
   - Student model with coordinates.
   - Admin CRUD.

4. Create **drivers app**:
   - Driver model.
   - Admin CRUD.

---

### **Phase 2 (Trips & Attendance)**

5. Create **RoutePlan (routes app)**:
   - Trip creation.
   - Assign students, drivers.

6. Create **Attendance app**:
   - Attendance model + endpoints.

---

### **Phase 3 (WebSocket & Real-time Tracking)**

7. Integrate **Django Channels.**
8. Implement **live_tracking app**:
   - Driver streams live location.
   - Parent subscribes to driver’s trip.

---

### **Phase 4 (Route Optimization)**

9. Implement clustering (K-Means).
10. Integrate **Mapbox API**:
    - Fetch optimized route.
    - Store route order, total distance.

11. Schedule **automatic optimization (7 AM, 2 PM)** using Celery or Cron.

---

### **Phase 5 (Admin UX & Parent Notifications - V2)**

12. Enhance **Django Admin interface**:
    - Visual map (Leaflet) for student clusters & routes.

13. Implement **Parent Notification system**:
    - Notify when bus is near.

---
