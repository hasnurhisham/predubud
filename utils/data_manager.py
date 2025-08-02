import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

def get_default_courses():
    """Return the pre-loaded course list"""
    return [
        {"code": "BSD 1323", "name": "Storytelling & Data Visualization", "carry_weight": 60, "exam_weight": 40},
        {"code": "BSD 2143", "name": "Operational Research", "carry_weight": 60, "exam_weight": 40},
        {"code": "BUM 2413", "name": "Applied Statistics", "carry_weight": 60, "exam_weight": 40},
        {"code": "BUM 2123", "name": "Applied Calculus", "carry_weight": 60, "exam_weight": 40},
        {"code": "BCU 1023", "name": "Programming Technique", "carry_weight": 60, "exam_weight": 40},
        {"code": "ULS 1312", "name": "Spanish A1", "carry_weight": 60, "exam_weight": 40},
        {"code": "UHE 3032", "name": "Introduction to Human Behaviour", "carry_weight": 60, "exam_weight": 40}
    ]

def get_sample_carry_marks():
    """Return sample carry marks data for demonstration"""
    return [
        {
            "course_code": "BSD 1323",
            "element_type": "Quiz",
            "element_name": "Quiz 1",
            "earned": 18,
            "max_possible": 20,
            "weight_percentage": 10,
            "final_contribution": 9.0,
            "percentage": 90.0,
            "date_added": "2025-01-15"
        },
        {
            "course_code": "BSD 1323",
            "element_type": "Assignment",
            "element_name": "Data Viz Project",
            "earned": 42,
            "max_possible": 50,
            "weight_percentage": 25,
            "final_contribution": 21.0,
            "percentage": 84.0,
            "date_added": "2025-01-22"
        },
        {
            "course_code": "BSD 2143",
            "element_type": "Test",
            "element_name": "Mid-term Test",
            "earned": 35,
            "max_possible": 40,
            "weight_percentage": 20,
            "final_contribution": 17.5,
            "percentage": 87.5,
            "date_added": "2025-01-20"
        },
        {
            "course_code": "BUM 2413",
            "element_type": "Lab",
            "element_name": "Statistics Lab 1",
            "earned": 28,
            "max_possible": 30,
            "weight_percentage": 15,
            "final_contribution": 14.0,
            "percentage": 93.3,
            "date_added": "2025-01-18"
        }
    ]

def get_sample_assignments():
    """Return sample assignments data for demonstration"""
    return [
        {
            "title": "Data Visualization Dashboard",
            "course_code": "BSD 1323",
            "type": "Project",
            "due_date": "2025-08-15",
            "status": "pending",
            "description": "Create an interactive dashboard using Tableau"
        },
        {
            "title": "Linear Programming Exercise",
            "course_code": "BSD 2143",
            "type": "Assignment",
            "due_date": "2025-08-10",
            "status": "completed",
            "description": "Solve optimization problems using simplex method"
        },
        {
            "title": "Hypothesis Testing Report",
            "course_code": "BUM 2413",
            "type": "Report",
            "due_date": "2025-08-20",
            "status": "pending",
            "description": "Statistical analysis of provided dataset"
        },
        {
            "title": "Calculus Problem Set 3",
            "course_code": "BUM 2123",
            "type": "Problem Set",
            "due_date": "2025-08-08",
            "status": "completed",
            "description": "Integration and differentiation problems"
        },
        {
            "title": "Python Programming Assignment",
            "course_code": "BCU 1023",
            "type": "Assignment",
            "due_date": "2025-08-25",
            "status": "in_progress",
            "description": "Implement sorting algorithms"
        }
    ]

def initialize_session_state():
    """Initialize session state variables"""
    if 'courses' not in st.session_state:
        st.session_state.courses = get_default_courses()
    
    if 'carry_marks' not in st.session_state:
        st.session_state.carry_marks = []
    
    if 'final_exams' not in st.session_state:
        st.session_state.final_exams = []
    
    if 'assignments' not in st.session_state:
        st.session_state.assignments = []
    
    if 'theme_color' not in st.session_state:
        st.session_state.theme_color = "#1f77b4"
    
    # Add a flag to track if sample data has been loaded
    if 'sample_data_loaded' not in st.session_state:
        st.session_state.sample_data_loaded = False

def load_sample_data():
    """Load sample data for demonstration"""
    if not st.session_state.sample_data_loaded:
        st.session_state.carry_marks = get_sample_carry_marks()
        st.session_state.assignments = get_sample_assignments()
        st.session_state.sample_data_loaded = True
        return True
    return False

def get_courses_df():
    """Get courses as DataFrame"""
    df = pd.DataFrame(st.session_state.courses)
    return df

def get_carry_marks_df():
    """Get carry marks as DataFrame with proper data types"""
    if st.session_state.carry_marks:
        df = pd.DataFrame(st.session_state.carry_marks)
        
        # Ensure proper data types
        numeric_columns = ['earned', 'max_possible', 'weight_percentage', 'final_contribution']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Calculate percentage if not present
        if 'percentage' not in df.columns:
            df['percentage'] = (df['earned'] / df['max_possible'] * 100).fillna(0)
        else:
            df['percentage'] = pd.to_numeric(df['percentage'], errors='coerce').fillna(0)
        
        # Ensure date column
        if 'date_added' not in df.columns:
            df['date_added'] = datetime.now().strftime("%Y-%m-%d")
        
        return df
    
    return pd.DataFrame(columns=[
        'course_code', 'element_type', 'element_name', 'earned', 
        'max_possible', 'weight_percentage', 'final_contribution', 
        'percentage', 'date_added'
    ])

def get_assignments_df():
    """Get assignments as DataFrame with proper data types"""
    if st.session_state.assignments:
        df = pd.DataFrame(st.session_state.assignments)
        
        # Ensure due_date is in proper format
        if 'due_date' in df.columns:
            df['due_date'] = pd.to_datetime(df['due_date'], errors='coerce')
            # Convert back to string format for consistency
            df['due_date'] = df['due_date'].dt.strftime('%Y-%m-%d')
        
        return df
    
    return pd.DataFrame(columns=[
        'title', 'course_code', 'type', 'due_date', 'status', 'description'
    ])

def add_course(course_data):
    """Add a new course"""
    st.session_state.courses.append(course_data)

def update_course(index, course_data):
    """Update an existing course"""
    if 0 <= index < len(st.session_state.courses):
        st.session_state.courses[index] = course_data

def delete_course(index):
    """Delete a course"""
    if 0 <= index < len(st.session_state.courses):
        course_code = st.session_state.courses[index]['code']
        # Remove associated carry marks and assignments
        st.session_state.carry_marks = [cm for cm in st.session_state.carry_marks if cm.get('course_code') != course_code]
        st.session_state.assignments = [a for a in st.session_state.assignments if a.get('course_code') != course_code]
        st.session_state.final_exams = [fe for fe in st.session_state.final_exams if fe.get('course_code') != course_code]
        del st.session_state.courses[index]

def add_carry_mark(carry_data):
    """Add a new carry mark entry"""
    # Calculate percentage if not provided
    if 'percentage' not in carry_data and 'earned' in carry_data and 'max_possible' in carry_data:
        max_possible = float(carry_data['max_possible']) if carry_data['max_possible'] else 1
        carry_data['percentage'] = (float(carry_data['earned']) / max_possible * 100) if max_possible > 0 else 0
    
    # Calculate final contribution if weight is provided
    if 'weight_percentage' in carry_data and 'percentage' in carry_data:
        weight = float(carry_data['weight_percentage']) if carry_data['weight_percentage'] else 0
        percentage = float(carry_data['percentage']) if carry_data['percentage'] else 0
        carry_data['final_contribution'] = (percentage / 100) * weight
    
    carry_data['date_added'] = datetime.now().strftime("%Y-%m-%d")
    st.session_state.carry_marks.append(carry_data)

def add_assignment(assignment_data):
    """Add a new assignment"""
    st.session_state.assignments.append(assignment_data)

def update_assignment_status(index, new_status):
    """Update assignment status"""
    if 0 <= index < len(st.session_state.assignments):
        st.session_state.assignments[index]['status'] = new_status

def delete_assignment(index):
    """Delete an assignment"""
    if 0 <= index < len(st.session_state.assignments):
        del st.session_state.assignments[index]

def update_carry_mark(index, carry_data):
    """Update an existing carry mark"""
    if 0 <= index < len(st.session_state.carry_marks):
        # Recalculate percentage and contribution
        if 'percentage' not in carry_data and 'earned' in carry_data and 'max_possible' in carry_data:
            max_possible = float(carry_data['max_possible']) if carry_data['max_possible'] else 1
            carry_data['percentage'] = (float(carry_data['earned']) / max_possible * 100) if max_possible > 0 else 0
        
        if 'weight_percentage' in carry_data and 'percentage' in carry_data:
            weight = float(carry_data['weight_percentage']) if carry_data['weight_percentage'] else 0
            percentage = float(carry_data['percentage']) if carry_data['percentage'] else 0
            carry_data['final_contribution'] = (percentage / 100) * weight
        
        st.session_state.carry_marks[index] = carry_data

def delete_carry_mark(index):
    """Delete a carry mark"""
    if 0 <= index < len(st.session_state.carry_marks):
        del st.session_state.carry_marks[index]

def export_data_to_csv():
    """Export all data to CSV format"""
    data = {
        'courses': get_courses_df(),
        'carry_marks': get_carry_marks_df(),
        'assignments': get_assignments_df()
    }
    return data

def import_data_from_dict(data_dict):
    """Import data from dictionary"""
    try:
        if 'courses' in data_dict:
            st.session_state.courses = data_dict['courses'].to_dict('records') if isinstance(data_dict['courses'], pd.DataFrame) else data_dict['courses']
        
        if 'carry_marks' in data_dict:
            st.session_state.carry_marks = data_dict['carry_marks'].to_dict('records') if isinstance(data_dict['carry_marks'], pd.DataFrame) else data_dict['carry_marks']
        
        if 'assignments' in data_dict:
            st.session_state.assignments = data_dict['assignments'].to_dict('records') if isinstance(data_dict['assignments'], pd.DataFrame) else data_dict['assignments']
        
        return True
    except Exception as e:
        st.error(f"Error importing data: {str(e)}")
        return False

def get_course_summary():
    """Get summary statistics for all courses"""
    courses_df = get_courses_df()
    carry_marks_df = get_carry_marks_df()
    assignments_df = get_assignments_df()
    
    summary = {
        'total_courses': len(courses_df),
        'total_assessments': len(carry_marks_df),
        'total_assignments': len(assignments_df),
        'avg_performance': carry_marks_df['percentage'].mean() if not carry_marks_df.empty else 0,
        'completion_rate': (len(assignments_df[assignments_df['status'] == 'completed']) / len(assignments_df) * 100) if not assignments_df.empty else 0
    }
    
    return summary
