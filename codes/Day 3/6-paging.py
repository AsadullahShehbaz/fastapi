from typing import List
from fastapi import FastAPI, Query

app = FastAPI()

students = [
    {"id": 1, "name": "Arsal", "school_code": "SCH001"},
    {"id": 2, "name": "Ayan Ahmed", "school_code": "SCH002"},
    {"id": 3, "name": "Hafiz Muhammad Abdullah", "school_code": "SCH001"},
    {"id": 4, "name": "Zohan", "school_code": "SCH003"},
    {"id": 5, "name": "Ibrahim", "school_code": "SCH002"},
    # ... more students
]

@app.get("/students/", response_model=List[dict])
def get_students(
    skip: int = 0,
    limit: int = 3,
    q: str = Query(None, min_length=1, max_length=50)  # Optional search query
):
    filtered_students = students
    
    # If query provided, filter students by name containing q (case-insensitive)
    if q:
        filtered_students = [
            student for student in students if q.lower() in student["name"].lower()
        ]
    
    # Return paginated results
    return filtered_students[skip : skip + limit]
