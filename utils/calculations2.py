import pandas as pd
from datetime import datetime
import numpy as np

def calculate_carry_percentage(course_code, carry_marks_df):
    """Calculate carry percentage for a specific course"""
    if carry_marks_df.empty:
        return 0
    
    course_marks = carry_marks_df[carry_marks_df['course_code'] == course_code]
    if course_marks.empty:
        return 0
    
    # If percentage column exists, use average
    if 'percentage' in course_marks.columns:
        return course_marks['percentage'].mean()
    
    # Otherwise calculate from earned/max_possible
    total_earned = course_marks['earned'].sum()
    total_max = course_marks['max_possible'].sum()
    
    if total_max == 0:
        return 0
    
    return (total_earned / total_max) * 100

def calculate_final_exam_requirement(target_grade, carry_percentage, carry_weight, exam_weight):
    """Calculate minimum final exam mark needed to achieve target grade"""
    if exam_weight == 0:
        return 0
    
    carry_contribution = (carry_percentage / 100) * (carry_weight / 100) * 100
    required_exam_contribution = target_grade - carry_contribution
    required_exam_percentage = (required_exam_contribution / exam_weight) * 100
    
    return max(0, min(100, required_exam_percentage))  # Ensure it's between 0-100

def calculate_current_grade(course_code, carry_marks_df, courses_df):
    """Calculate current grade based on carry marks"""
    course_info = courses_df[courses_df['code'] == course_code]
    if course_info.empty:
        return 0
    
    course_marks = carry_marks_df[carry_marks_df['course_code'] == course_code]
    if course_marks.empty:
        return 0
    
    # If we have weighted contributions, use those
    if 'final_contribution' in course_marks.columns:
        return course_marks['final_contribution'].sum()
    
    # Fallback to percentage-based calculation
    carry_weight = course_info.iloc[0]['carry_weight']
    
    # Calculate percentage
    if 'percentage' in course_marks.columns:
        avg_percentage = course_marks['percentage'].mean()
    else:
        # Calculate from earned/max_possible
        total_earned = course_marks['earned'].sum()
        total_max = course_marks['max_possible'].sum()
        avg_percentage = (total_earned / total_max * 100) if total_max > 0 else 0
    
    # Return the contribution to final grade
    return (avg_percentage / 100) * carry_weight

def get_grade_letter(percentage):
    """Convert percentage to letter grade"""
    if pd.isna(percentage) or percentage < 0:
        return "F"
    elif percentage >= 90:
        return "A+"
    elif percentage >= 85:
        return "A"
    elif percentage >= 80:
        return "A-"
    elif percentage >= 75:
        return "B+"
    elif percentage >= 70:
        return "B"
    elif percentage >= 65:
        return "B-"
    elif percentage >= 60:
        return "C+"
    elif percentage >= 55:
        return "C"
    elif percentage >= 50:
        return "C-"
    else:
        return "F"

def calculate_days_until_due(due_date_str):
    """Calculate days until due date"""
    try:
        due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
        today = datetime.now()
        delta = due_date - today
        return delta.days
    except:
        return 0

def get_weekly_workload(assignments_df):
    """Calculate weekly workload summary"""
    if assignments_df.empty:
        return pd.DataFrame()
    
    assignments_df = assignments_df.copy()
    assignments_df['due_date'] = pd.to_datetime(assignments_df['due_date'])
    assignments_df['week'] = assignments_df['due_date'].dt.to_period('W')
    
    weekly_summary = assignments_df.groupby('week').agg({
        'title': 'count',
        'status': lambda x: (x == 'pending').sum()
    }).rename(columns={'title': 'total_assignments', 'status': 'pending_assignments'})
    
    return weekly_summary.reset_index()

def calculate_completion_rate(assignments_df):
    """Calculate assignment completion rate"""
    if assignments_df.empty:
        return 0
    
    completed = len(assignments_df[assignments_df['status'] == 'completed'])
    total = len(assignments_df)
    
    return (completed / total) * 100 if total > 0 else 0

def calculate_weighted_gpa(course_stats_df):
    """Calculate weighted GPA based on course credits/weights"""
    if course_stats_df.empty:
        return 0
    
    # Convert letter grades to GPA points
    grade_points = {
        'A+': 4.0, 'A': 4.0, 'A-': 3.7,
        'B+': 3.3, 'B': 3.0, 'B-': 2.7,
        'C+': 2.3, 'C': 2.0, 'C-': 1.7,
        'F': 0.0, 'N/A': 0.0
    }
    
    total_points = 0
    total_weight = 0
    
    for _, row in course_stats_df.iterrows():
        if 'Letter Grade' in row and 'Carry Weight' in row:
            points = grade_points.get(row['Letter Grade'], 0.0)
            weight = row['Carry Weight']
            total_points += points * weight
            total_weight += weight
    
    return (total_points / total_weight) if total_weight > 0 else 0

def get_performance_trend(carry_marks_df):
    """Calculate performance trend (improving, declining, stable)"""
    if carry_marks_df.empty or len(carry_marks_df) < 2:
        return "Insufficient data"
    
    # Ensure we have percentage and date columns
    df = carry_marks_df.copy()
    if 'percentage' not in df.columns:
        df['percentage'] = (df['earned'] / df['max_possible'] * 100).fillna(0)
    
    if 'date_added' not in df.columns:
        return "No date information"
    
    df['date_added'] = pd.to_datetime(df['date_added'])
    df = df.sort_values('date_added')
    
    # Calculate trend using linear regression
    x = np.arange(len(df))
    y = df['percentage'].values
    
    if len(x) < 2:
        return "Insufficient data"
    
    slope = np.polyfit(x, y, 1)[0]
    
    if slope > 2:
        return "Improving"
    elif slope < -2:
        return "Declining"
    else:
        return "Stable"

def calculate_study_recommendations(course_stats_df, assignments_df):
    """Generate study recommendations based on performance data"""
    recommendations = []
    
    if course_stats_df.empty:
        return ["Add some carry marks to get personalized recommendations!"]
    
    # Find courses that need attention
    low_performing_courses = course_stats_df[course_stats_df['Average %'] < 70]
    if not low_performing_courses.empty:
        for _, course in low_performing_courses.iterrows():
            recommendations.append(f"📚 Focus more study time on {course['Course Code']} (current: {course['
