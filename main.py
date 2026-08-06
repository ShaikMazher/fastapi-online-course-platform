from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import math
# Initialize our FastAPI backend app
app = FastAPI()

# ==========================================
# INITIAL DATABASE (Mock Data)
# ==========================================
# Q2: A list of at least 6 course dictionaries
courses = [
    {"id": 1, "title": "Full-Stack Web Dev with React", "instructor": "Shaik Mazher", "category": "Web Dev", "level": "Beginner", "price": 3999, "seats_left": 15},
    {"id": 2, "title": "Python Data Science & Pandas", "instructor": "Ananya Sharma", "category": "Data Science", "level": "Intermediate", "price": 4999, "seats_left": 8},
    {"id": 3, "title": "Unreal Engine 5 Action RPGs", "instructor": "Shaik Mazher", "category": "Design", "level": "Advanced", "price": 5999, "seats_left": 5},
    {"id": 4, "title": "DevOps & Cloud Infrastructure", "instructor": "Rahul Verma", "category": "DevOps", "level": "Intermediate", "price": 4500, "seats_left": 12},
    {"id": 5, "title": "Beginner ROS 2 & Robotics", "instructor": "Priya Singh", "category": "DevOps", "level": "Beginner", "price": 3500, "seats_left": 20},
    {"id": 6, "title": "Intro to Artificial Intelligence", "instructor": "Dr. Kumar", "category": "Data Science", "level": "Beginner", "price": 0, "seats_left": 50} # Free course!
]

# Q4: Empty list for enrollments and a tracking counter
enrollments = []
enrollment_counter = 1


# ==========================================
# Q1: HOME ROUTE
# ==========================================
@app.get("/")
def home():
    return {'message': 'Welcome to LearnHub Online Courses'}


# ==========================================
# Q2: GET ALL COURSES
# ==========================================
@app.get("/courses")
def get_all_courses():
    total_seats = sum(c["seats_left"] for c in courses)
    return {
        "total": len(courses),
        "total_seats_available": total_seats,
        "courses": courses
    }


# ==========================================
# Q5: COURSE SUMMARY
# ==========================================
@app.get("/courses/summary")
def get_course_summary():
    free_courses = sum(1 for c in courses if c["price"] == 0)
    most_expensive = max(courses, key=lambda c: c["price"])
    total_seats = sum(c["seats_left"] for c in courses)
    
    category_counts = {}
    for c in courses:
        cat = c["category"]
        category_counts[cat] = category_counts.get(cat, 0) + 1
        
    return {
        "total_courses": len(courses),
        "free_courses_count": free_courses,
        "most_expensive_course": most_expensive["title"],
        "total_seats_available": total_seats,
        "category_breakdown": category_counts
    }
# ==========================================
# Q10: FILTER ENDPOINT[cite: 4]
# Paste this ABOVE the @app.get("/courses/{course_id}") route!
# ==========================================
def filter_courses_logic(category: str = None, level: str = None, max_price: int = None, has_seats: bool = None):
    filtered = courses
    if category is not None:
        filtered = [c for c in filtered if c["category"].lower() == category.lower()]
    if level is not None:
        filtered = [c for c in filtered if c["level"].lower() == level.lower()]
    if max_price is not None:
        filtered = [c for c in filtered if c["price"] <= max_price]
    if has_seats is not None:
        if has_seats:
            filtered = [c for c in filtered if c["seats_left"] > 0]
        else:
            filtered = [c for c in filtered if c["seats_left"] == 0]
    return filtered

@app.get("/courses/filter")
def filter_courses(category: str = None, level: str = None, max_price: int = None, has_seats: bool = None):
    results = filter_courses_logic(category, level, max_price, has_seats)
    return {"total_matches": len(results), "courses": results}

# ==========================================
# Q16: GET /courses/search
# ==========================================
@app.get("/courses/search")
def search_courses(keyword: str):
    kw = keyword.lower()
    matches = [c for c in courses if kw in c["title"].lower() or kw in c["instructor"].lower() or kw in c["category"].lower()]
    return {"total_found": len(matches), "results": matches}

# ==========================================
# Q17: GET /courses/sort
# ==========================================
@app.get("/courses/sort")
def sort_courses(sort_by: str = "price", order: str = "asc"):
    if sort_by not in ["price", "title", "seats_left"]:
        return {"error": "Invalid sort_by. Choose price, title, or seats_left."}
    if order not in ["asc", "desc"]:
        return {"error": "Invalid order. Choose asc or desc."}
    
    rev = True if order == "desc" else False
    sorted_courses = sorted(courses, key=lambda x: x[sort_by], reverse=rev)
    return {"sort_by": sort_by, "order": order, "courses": sorted_courses}

# ==========================================
# Q18: GET /courses/page
# ==========================================
@app.get("/courses/page")
def paginate_courses(page: int = 1, limit: int = 3):
    if page < 1 or limit < 1:
        return {"error": "Page and limit must be 1 or greater"}
        
    start = (page - 1) * limit
    end = start + limit
    paginated = courses[start:end]
    total_pages = math.ceil(len(courses) / limit)
    
    return {"page": page, "limit": limit, "total": len(courses), "total_pages": total_pages, "courses": paginated}

# ==========================================
# Q20: GET /courses/browse (THE MASTER ENDPOINT)
# ==========================================
@app.get("/courses/browse")
def browse_courses(keyword: Optional[str] = None, category: Optional[str] = None, level: Optional[str] = None, max_price: Optional[int] = None, sort_by: str = "price", order: str = "asc", page: int = 1, limit: int = 3):
    results = courses
    
    # 1. Search
    if keyword:
        kw = keyword.lower()
        results = [c for c in results if kw in c["title"].lower() or kw in c["instructor"].lower() or kw in c["category"].lower()]
        
    # 2. Filter
    if category:
        results = [c for c in results if c["category"].lower() == category.lower()]
    if level:
        results = [c for c in results if c["level"].lower() == level.lower()]
    if max_price is not None:
        results = [c for c in results if c["price"] <= max_price]
        
    # 3. Sort[cite: 4]
    if sort_by in ["price", "title", "seats_left"] and order in ["asc", "desc"]:
        rev = (order == "desc")
        results = sorted(results, key=lambda x: x[sort_by], reverse=rev)
        
    # 4. Paginate[cite: 4]
    total_matches = len(results)
    total_pages = math.ceil(total_matches / limit) if limit > 0 else 1
    start = (page - 1) * limit
    results = results[start:start+limit]
    
    return {
        "metadata": {
            "keyword": keyword, "category": category, "level": level, "max_price": max_price,
            "sort_by": sort_by, "order": order, "page": page, "limit": limit,
            "total_matches": total_matches, "total_pages": total_pages
        },
        "courses": results
    }

# ==========================================
# Q19: ENROLLMENTS SECONDARY ENDPOINTS[cite: 4]
# Paste this directly above your Q4: GET ALL ENROLLMENTS block!
# ==========================================
@app.get("/enrollments/search")
def search_enrollments(student_name: str):
    matches = [e for e in enrollments if student_name.lower() in e["student_name"].lower()]
    return {"total_found": len(matches), "enrollments": matches}
    
@app.get("/enrollments/sort")
def sort_enrollments(order: str = "asc"):
    rev = (order == "desc")
    sorted_e = sorted(enrollments, key=lambda x: x["final_fee"], reverse=rev)
    return {"enrollments": sorted_e}
    
@app.get("/enrollments/page")
def paginate_enrollments(page: int = 1, limit: int = 3):
    start = (page - 1) * limit
    paginated = enrollments[start:start+limit]
    return {"page": page, "enrollments": paginated}

# ==========================================
# Q3: GET COURSE BY ID (Variable Route)
# ==========================================
@app.get("/courses/{course_id}")
def get_course_by_id(course_id: int):
    for c in courses:
        if c["id"] == course_id:
            return c
    return {'error': 'Course not found'}


# ==========================================
# Q4: GET ALL ENROLLMENTS[cite: 4]
# ==========================================
@app.get("/enrollments")
def get_all_enrollments():
    return {
        "total": len(enrollments),
        "enrollments": enrollments
    }
# ==========================================
# Q6 & Q9: PYDANTIC MODEL (EnrollRequest)
# ==========================================
class EnrollRequest(BaseModel):
    student_name: str = Field(..., min_length=2)
    course_id: int = Field(..., gt=0)
    email: str = Field(..., min_length=5)
    payment_method: str = "card"
    coupon_code: str = ""
    # Q9 Additions
    gift_enrollment: bool = False
    recipient_name: str = ""

# ==========================================
# Q7: HELPER FUNCTIONS (No @app decorators)
# ==========================================
def find_course(course_id: int):
    for c in courses:
        if c["id"] == course_id:
            return c
    return None

def calculate_enrollment_fee(price: int, seats_left: int, coupon_code: str):
    final_price = float(price)
    
    # Early-bird discount: 10% off if more than 5 seats left
    if seats_left > 5:
        final_price = final_price * 0.90
        
    # Coupon discounts applied after early-bird
    if coupon_code == "STUDENT20":
        final_price = final_price * 0.80
    elif coupon_code == "FLAT500":
        final_price = max(0.0, final_price - 500.0)
        
    return int(final_price)

# ==========================================
# Q8 & Q9: POST /enrollments[cite: 4]
# ==========================================
@app.post("/enrollments")
def create_enrollment(req: EnrollRequest):
    # Q9 Validation: If it's a gift, a recipient name is mandatory[cite: 4]
    if req.gift_enrollment and not req.recipient_name:
        return {"error": "Validation failed: Recipient name is required for gift enrollments"}
        
    course = find_course(req.course_id)
    if not course:
        return {"error": "Course not found"}
        
    if course["seats_left"] <= 0:
        return {"error": "Course is full"}
        
    # Calculate fee using helper[cite: 4]
    final_fee = calculate_enrollment_fee(course["price"], course["seats_left"], req.coupon_code)
    
    # Reduce seats[cite: 4]
    course["seats_left"] -= 1
    
    global enrollment_counter
    
    new_enrollment = {
        "enrollment_id": enrollment_counter,
        "student_name": req.student_name,
        "course_title": course["title"],
        "instructor": course["instructor"],
        "original_price": course["price"],
        "final_fee": final_fee,
        "is_gift": req.gift_enrollment,
        "recipient": req.recipient_name if req.gift_enrollment else None
    }
    
    enrollments.append(new_enrollment)
    enrollment_counter += 1
    
    return {"message": "Enrollment successful", "enrollment_details": new_enrollment}
# ==========================================
# Q11: POST /courses (CREATE)
# ==========================================
class NewCourse(BaseModel):
    title: str = Field(..., min_length=2)
    instructor: str = Field(..., min_length=2)
    category: str = Field(..., min_length=2)
    level: str = Field(..., min_length=2)
    price: int = Field(..., ge=0)
    seats_left: int = Field(..., gt=0)

@app.post("/courses", status_code=201)
def create_course(course: NewCourse):
    # Reject duplicate titles (case-insensitive)
    for c in courses:
        if c["title"].lower() == course.title.lower():
            return {"error": "A course with this title already exists"}
            
    new_id = max((c["id"] for c in courses), default=0) + 1
    new_course = course.dict()
    new_course["id"] = new_id
    courses.append(new_course)
    
    return {"message": "Course created successfully", "course": new_course}

# ==========================================
# Q12: PUT /courses/{course_id} (UPDATE)
# ==========================================
@app.put("/courses/{course_id}")
def update_course(course_id: int, price: Optional[int] = None, seats_left: Optional[int] = None):
    course = find_course(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
        
    # Apply only non-None updates
    if price is not None:
        course["price"] = price
    if seats_left is not None:
        course["seats_left"] = seats_left
        
    return {"message": "Course updated", "course": course}

# ==========================================
# Q13: DELETE /courses/{course_id} (DELETE)
# ==========================================
@app.delete("/courses/{course_id}")
def delete_course(course_id: int):
    course = find_course(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
        
    # Check if course has active enrollments
    for e in enrollments:
        if e["course_title"] == course["title"]:
            return {"error": "Cannot delete course with enrolled students"}
            
    courses.remove(course)
    return {"message": f"Course '{course['title']}' deleted successfully"}

# ==========================================
# Q14: WISHLIST SYSTEM[cite: 4]
# ==========================================
wishlist = []

@app.post("/wishlist/add")
def add_to_wishlist(student_name: str, course_id: int):
    course = find_course(course_id)
    if not course:
        return {"error": "Course not found"}
        
    # Prevent duplicate student+course combos[cite: 4]
    for w in wishlist:
        if w["student_name"].lower() == student_name.lower() and w["course"]["id"] == course_id:
            return {"error": "Course is already in your wishlist"}
            
    wishlist_item = {"student_name": student_name, "course": course}
    wishlist.append(wishlist_item)
    return {"message": "Added to wishlist", "item": wishlist_item}

@app.get("/wishlist")
def get_wishlist():
    total_value = sum(w["course"]["price"] for w in wishlist)
    return {"total_items": len(wishlist), "total_value": total_value, "wishlist": wishlist}

# ==========================================
# Q15: WISHLIST CHECKOUT & REMOVE[cite: 4]
# ==========================================
@app.delete("/wishlist/remove/{course_id}")
def remove_from_wishlist(course_id: int, student_name: str):
    global wishlist
    for w in wishlist:
        if w["student_name"].lower() == student_name.lower() and w["course"]["id"] == course_id:
            wishlist.remove(w)
            return {"message": "Course removed from wishlist"}
    return {"error": "Item not found in wishlist"}

class EnrollAllRequest(BaseModel):
    student_name: str
    payment_method: str = "card"

@app.post("/wishlist/enroll-all", status_code=201)
def enroll_all_wishlist(req: EnrollAllRequest):
    global enrollment_counter, wishlist
    
    # Find all items for this specific student[cite: 4]
    student_items = [w for w in wishlist if w["student_name"].lower() == req.student_name.lower()]
    
    if not student_items:
        return {"error": "Wishlist is empty for this student"}
        
    confirmations = []
    grand_total = 0
    
    for w in student_items:
        course = w["course"]
        if course["seats_left"] > 0:
            course["seats_left"] -= 1
            
            new_enroll = {
                "enrollment_id": enrollment_counter,
                "student_name": req.student_name,
                "course_title": course["title"],
                "instructor": course["instructor"],
                "final_fee": course["price"]
            }
            
            enrollments.append(new_enroll)
            enrollment_counter += 1
            confirmations.append(new_enroll)
            grand_total += course["price"]
            
            # Remove from master wishlist[cite: 4]
            wishlist.remove(w)
            
    return {
        "message": "Bulk enrollment successful",
        "total_enrolled": len(confirmations),
        "grand_total_fee": grand_total,
        "enrollments": confirmations
    }