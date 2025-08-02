import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
from utils.data_manager import get_courses_df, get_carry_marks_df, get_assignments_df
from utils.calculations import calculate_carry_percentage, calculate_current_grade, get_grade_letter, calculate_completion_rate

def analytics_tab():
    """Analytics and insights dashboard"""
    st.header("📊 Personal Insights & Analytics")
    
    courses_df = get_courses_df()
    carry_marks_df = get_carry_marks_df()
    assignments_df = get_assignments_df()
    
    if courses_df.empty:
        st.warning("Please add courses first to see analytics.")
        return
    
    # Overview metrics
    st.subheader("📈 Academic Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_courses = len(courses_df)
        st.metric("Total Courses", total_courses)
    
    with col2:
        if not carry_marks_df.empty:
            # Calculate average performance based on percentages
            if 'percentage' in carry_marks_df.columns:
                avg_performance = carry_marks_df['percentage'].mean()
            else:
                # Calculate percentage from earned/max_possible
                carry_marks_df['percentage'] = (carry_marks_df['earned'] / carry_marks_df['max_possible'] * 100).fillna(0)
                avg_performance = carry_marks_df['percentage'].mean()
            st.metric("Average Performance", f"{avg_performance:.1f}%")
        else:
            st.metric("Average Performance", "No data")
    
    with col3:
        if not assignments_df.empty:
            completion_rate = calculate_completion_rate(assignments_df)
            st.metric("Assignment Completion", f"{completion_rate:.1f}%")
        else:
            st.metric("Assignment Completion", "No data")
    
    with col4:
        if not assignments_df.empty:
            pending_assignments = len(assignments_df[assignments_df['status'] == 'pending'])
            st.metric("Pending Assignments", pending_assignments)
        else:
            st.metric("Pending Assignments", 0)
    
    # Initialize course_stats_df
    course_stats_df = pd.DataFrame()
    
    # Course performance analysis - BAR CHARTS
    if not carry_marks_df.empty:
        st.markdown("---")
        st.subheader("🎯 Course Performance Analysis")
        
        # Ensure percentage column exists
        if 'percentage' not in carry_marks_df.columns:
            carry_marks_df['percentage'] = (carry_marks_df['earned'] / carry_marks_df['max_possible'] * 100).fillna(0)
        
        # Calculate comprehensive course statistics
        course_stats = []
        for _, course in courses_df.iterrows():
            course_code = course['code']
            course_name = course['name']
            carry_pct = calculate_carry_percentage(course_code, carry_marks_df)
            current_grade = calculate_current_grade(course_code, carry_marks_df, courses_df)
            
            # Calculate letter grade
            course_marks = carry_marks_df[carry_marks_df['course_code'] == course_code]
            if not course_marks.empty:
                avg_percentage = course_marks['percentage'].mean()
                letter_grade = get_grade_letter(avg_percentage)
            else:
                letter_grade = "N/A"
                avg_percentage = 0
            
            # Count assignments for this course
            course_assignments = assignments_df[assignments_df['course_code'] == course_code] if not assignments_df.empty else pd.DataFrame()
            total_assignments = len(course_assignments)
            completed_assignments = len(course_assignments[course_assignments['status'] == 'completed']) if not course_assignments.empty else 0
            
            course_stats.append({
                'Course Code': course_code,
                'Course Name': course_name,
                'Carry %': carry_pct,
                'Current Grade': current_grade,
                'Average %': avg_percentage,
                'Letter Grade': letter_grade,
                'Total Assignments': total_assignments,
                'Completed Assignments': completed_assignments,
                'Carry Weight': course['carry_weight'],
                'Exam Weight': course['exam_weight']
            })
        
        course_stats_df = pd.DataFrame(course_stats)
        
        # Performance dashboard with enhanced charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Enhanced Current grades bar chart
            if not course_stats_df.empty:
                fig_grades = px.bar(
                    course_stats_df,
                    x='Course Code',
                    y='Average %',
                    color='Average %',
                    title="Average Performance by Course",
                    color_continuous_scale='RdYlGn',
                    range_color=[0, 100],
                    text='Average %'
                )
                fig_grades.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                fig_grades.update_layout(
                    showlegend=False,
                    yaxis_title="Performance (%)",
                    xaxis_title="Course Code"
                )
                st.plotly_chart(fig_grades, use_container_width=True)
        
        with col2:
            # Enhanced scatter plot
            if not course_stats_df.empty:
                fig_carry = px.scatter(
                    course_stats_df,
                    x='Carry %',
                    y='Average %',
                    size='Total Assignments',
                    color='Letter Grade',
                    hover_data=['Course Name', 'Completed Assignments'],
                    title="Carry Performance vs Average Grade",
                    size_max=20
                )
                # Add diagonal reference line
                fig_carry.add_shape(
                    type="line",
                    x0=0, y0=0, x1=100, y1=100,
                    line=dict(color="red", width=2, dash="dash"),
                )
                st.plotly_chart(fig_carry, use_container_width=True)
        
        # Letter Grade Distribution - PIE CHART
        if not course_stats_df.empty:
            st.subheader("🎓 Grade Distribution")
            col1, col2 = st.columns(2)
            
            with col1:
                grade_counts = course_stats_df['Letter Grade'].value_counts()
                fig_pie = px.pie(
                    values=grade_counts.values,
                    names=grade_counts.index,
                    title="Letter Grade Distribution",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                # Assignment completion by course - horizontal bar
                if course_stats_df['Total Assignments'].sum() > 0:
                    course_stats_df['Completion Rate'] = (course_stats_df['Completed Assignments'] / 
                                                        course_stats_df['Total Assignments'] * 100).fillna(0)
                    fig_completion = px.bar(
                        course_stats_df,
                        x='Completion Rate',
                        y='Course Code',
                        orientation='h',
                        title="Assignment Completion Rate by Course",
                        color='Completion Rate',
                        color_continuous_scale='Blues',
                        text='Completion Rate'
                    )
                    fig_completion.update_traces(texttemplate='%{text:.0f}%', textposition='auto')
                    st.plotly_chart(fig_completion, use_container_width=True)
        
        # Detailed course table
        st.subheader("📋 Detailed Course Statistics")
        display_df = course_stats_df[['Course Code', 'Course Name', 'Carry %', 'Average %', 'Letter Grade', 'Total Assignments', 'Completed Assignments']]
        st.dataframe(display_df, use_container_width=True)
        
        # Performance trends - TREND LINES
        if len(carry_marks_df) > 1:
            st.markdown("---")
            st.subheader("📈 Performance Trends Over Time")
            
            # Performance over time with enhanced styling
            carry_marks_df_sorted = carry_marks_df.copy()
            if 'date_added' not in carry_marks_df_sorted.columns:
                carry_marks_df_sorted['date_added'] = datetime.now().strftime("%Y-%m-%d")
            
            carry_marks_df_sorted['date_added'] = pd.to_datetime(carry_marks_df_sorted['date_added'])
            carry_marks_df_sorted = carry_marks_df_sorted.sort_values('date_added')
            
            fig_trend = px.line(
                carry_marks_df_sorted,
                x='date_added',
                y='percentage',
                color='course_code',
                title="Performance Trends Over Time",
                markers=True,
                line_shape='spline'
            )
            fig_trend.update_layout(
                xaxis_title="Date",
                yaxis_title="Performance (%)",
                legend_title="Course",
                hovermode='x unified'
            )
            # Add trend line
            fig_trend.add_hline(y=carry_marks_df_sorted['percentage'].mean(), 
                              line_dash="dash", line_color="red",
                              annotation_text=f"Average: {carry_marks_df_sorted['percentage'].mean():.1f}%")
            st.plotly_chart(fig_trend, use_container_width=True)
            
            # Enhanced Performance distribution and box plots
            col1, col2 = st.columns(2)
            
            with col1:
                fig_hist = px.histogram(
                    carry_marks_df,
                    x='percentage',
                    nbins=15,
                    title="Performance Distribution",
                    color_discrete_sequence=['lightblue'],
                    marginal="box"
                )
                fig_hist.add_vline(x=carry_marks_df['percentage'].mean(), 
                                 line_dash="dash", line_color="red",
                                 annotation_text=f"Mean: {carry_marks_df['percentage'].mean():.1f}%")
                st.plotly_chart(fig_hist, use_container_width=True)
            
            with col2:
                fig_box = px.box(
                    carry_marks_df,
                    x='course_code',
                    y='percentage',
                    title="Performance by Course (Box Plot)",
                    color='course_code'
                )
                fig_box.update_layout(showlegend=False)
                st.plotly_chart(fig_box, use_container_width=True)
    
    # Assignment analytics with enhanced visualizations
    if not assignments_df.empty:
        st.markdown("---")
        st.subheader("📋 Assignment Analytics")
        
        # Ensure due_date is datetime
        assignments_df_copy = assignments_df.copy()
        assignments_df_copy['due_date'] = pd.to_datetime(assignments_df_copy['due_date'])
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Enhanced Assignment status by course
            status_by_course = assignments_df.groupby(['course_code', 'status']).size().reset_index(name='count')
            fig_status = px.bar(
                status_by_course,
                x='course_code',
                y='count',
                color='status',
                title="Assignment Status by Course",
                barmode='stack',
                color_discrete_map={
                    'completed': '#2E8B57',
                    'pending': '#FF6347',
                    'in_progress': '#FFD700'
                }
            )
            fig_status.update_layout(xaxis_title="Course Code", yaxis_title="Number of Assignments")
            st.plotly_chart(fig_status, use_container_width=True)
        
        with col2:
            # Enhanced Assignment types distribution - PIE CHART
            type_counts = assignments_df['type'].value_counts()
            fig_types = px.pie(
                values=type_counts.values,
                names=type_counts.index,
                title="Assignment Types Distribution",
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_types.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_types, use_container_width=True)
        
        # Enhanced Calendar heatmap - HEAT MAP
        st.subheader("📅 Assignment Calendar Heatmap")
        
        # Create a more comprehensive heatmap
        if not assignments_df_copy.empty:
            # Create date range for current semester (adjust as needed)
            start_date = assignments_df_copy['due_date'].min().replace(day=1)
            end_date = assignments_df_copy['due_date'].max() + timedelta(days=30)
            
            # Create daily assignment counts
            daily_counts = assignments_df_copy.groupby(assignments_df_copy['due_date'].dt.date).size().reset_index(name='assignment_count')
            daily_counts['due_date'] = pd.to_datetime(daily_counts['due_date'])
            
            # Create a complete date range
            date_range = pd.date_range(start=start_date, end=end_date, freq='D')
            complete_df = pd.DataFrame({'due_date': date_range})
            complete_df = complete_df.merge(daily_counts, on='due_date', how='left')
            complete_df['assignment_count'] = complete_df['assignment_count'].fillna(0)
            
            # Add calendar components
            complete_df['day_of_week'] = complete_df['due_date'].dt.day_name()
            complete_df['week_of_year'] = complete_df['due_date'].dt.isocalendar().week
            complete_df['month'] = complete_df['due_date'].dt.strftime('%Y-%m')
            
            # Create heatmap
            fig_heatmap = px.density_heatmap(
                complete_df,
                x='week_of_year',
                y='day_of_week',
                z='assignment_count',
                title="Assignment Due Dates Heatmap",
                color_continuous_scale='Reds',
                category_orders={"day_of_week": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]}
            )
            fig_heatmap.update_layout(
                xaxis_title="Week of Year",
                yaxis_title="Day of Week"
            )
            st.plotly_chart(fig_heatmap, use_container_width=True)
        
        # Enhanced Weekly workload trends with dual axis
        assignments_df_copy['week'] = assignments_df_copy['due_date'].dt.to_period('W')
        weekly_workload = assignments_df_copy.groupby('week').agg({
            'title': 'count',
            'status': lambda x: (x == 'completed').sum()
        }).rename(columns={'title': 'total', 'status': 'completed'})
        weekly_workload['completion_rate'] = (weekly_workload['completed'] / weekly_workload['total'] * 100).fillna(0)
        
        if not weekly_workload.empty:
            st.subheader("📊 Weekly Workload and Completion Trends")
            
            fig_workload = go.Figure()
            
            weeks = [str(week) for week in weekly_workload.index]
            
            # Add bars for total assignments
            fig_workload.add_trace(go.Bar(
                x=weeks,
                y=weekly_workload['total'],
                name='Total Assignments',
                marker_color='lightblue',
                yaxis='y'
            ))
            
            # Add bars for completed assignments
            fig_workload.add_trace(go.Bar(
                x=weeks,
                y=weekly_workload['completed'],
                name='Completed Assignments',
                marker_color='darkblue',
                yaxis='y'
            ))
            
            # Add line for completion rate
            fig_workload.add_trace(go.Scatter(
                x=weeks,
                y=weekly_workload['completion_rate'],
                mode='lines+markers',
                name='Completion Rate (%)',
                line=dict(color='red', width=3),
                marker=dict(size=8),
                yaxis='y2'
            ))
            
            fig_workload.update_layout(
                title="Weekly Assignment Workload and Completion Rate",
                xaxis_title="Week",
                yaxis=dict(title="Number of Assignments", side="left"),
                yaxis2=dict(title="Completion Rate (%)", side="right", overlaying="y", range=[0, 100]),
                legend=dict(x=0.01, y=0.99),
                barmode='group'
            )
            
            st.plotly_chart(fig_workload, use_container_width=True)
        
        # Monthly assignment breakdown
        if not assignments_df_copy.empty:
            st.subheader("📅 Monthly Assignment Breakdown")
            monthly_data = assignments_df_copy.groupby([
                assignments_df_copy['due_date'].dt.to_period('M'), 
                'status'
            ]).size().reset_index(name='count')
            monthly_data['month'] = monthly_data['due_date'].astype(str)
            
            fig_monthly = px.bar(
                monthly_data,
                x='month',
                y='count',
                color='status',
                title="Monthly Assignment Distribution by Status",
                barmode='stack'
            )
            st.plotly_chart(fig_monthly, use_container_width=True)
    
    # Enhanced Insights and recommendations
    st.markdown("---")
    st.subheader("💡 Insights and Recommendations")
    
    insights = []
    
    # Performance insights
    if not carry_marks_df.empty:
        if 'percentage' not in carry_marks_df.columns:
            carry_marks_df['percentage'] = (carry_marks_df['earned'] / carry_marks_df['max_possible'] * 100).fillna(0)
        
        avg_performance = carry_marks_df['percentage'].mean()
        std_performance = carry_marks_df['percentage'].std()
        
        if avg_performance >= 85:
            insights.append("🎉 **Excellent performance!** You're maintaining high standards across your assessments.")
        elif avg_performance >= 70:
            insights.append("👍 **Good performance overall.** Consider focusing on weaker areas to boost your grades.")
        else:
            insights.append("⚠️ **Performance needs improvement.** Consider seeking help or adjusting study strategies.")
        
        if std_performance > 15:
            insights.append("📊 **Inconsistent performance detected.** Try to maintain more consistent study habits across all courses.")
        
        # Identify weakest and strongest courses
        if len(course_stats_df) > 0:
            weakest_course = course_stats_df.loc[course_stats_df['Average %'].idxmin()]
            strongest_course = course_stats_df.loc[course_stats_df['Average %'].idxmax()]
            insights.append(f"📚 **Focus area:** {weakest_course['Course Code']} has your lowest average ({weakest_course['Average %']:.1f}%).")
            insights.append(f"⭐ **Strength:** {strongest_course['Course Code']} is your best performing course ({strongest_course['Average %']:.1f}%).")
    
    # Assignment insights
    if not assignments_df.empty:
        completion_rate = calculate_completion_rate(assignments_df)
        if completion_rate >= 90:
            insights.append("✅ **Great job on assignments!** You're staying on top of your work.")
        elif completion_rate >= 70:
            insights.append("📝 **Good assignment management.** Try to improve completion rates further.")
        else:
            insights.append("⏰ **Assignment management needs attention.** Consider better time management strategies.")
        
        # Check for overdue assignments
        today = datetime.now().date()
        overdue_count = 0
        upcoming_count = 0
        
        for _, assignment in assignments_df.iterrows():
            if assignment['status'] == 'pending':
                try:
                    due_date = pd.to_datetime(assignment['due_date']).date()
                    days_diff = (due_date - today).days
                    if days_diff < 0:
                        overdue_count += 1
                    elif days_diff <= 7:
                        upcoming_count += 1
                except:
                    pass
        
        if overdue_count > 0:
            insights.append(f"🚨 **Urgent:** You have {overdue_count} overdue assignment(s). Address these immediately.")
        if upcoming_count > 0:
            insights.append(f"⏰ **Upcoming:** You have {upcoming_count} assignment(s) due within a week.")
    
    # Display insights
    for insight in insights:
        st.markdown(insight)
    
    if not insights:
        st.info("Add some courses, carry marks, and assignments to see personalized insights!")
    
    # Enhanced Data export section
    st.markdown("---")
    st.subheader("📥 Data Export")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if not carry_marks_df.empty:
            csv_carry = carry_marks_df.to_csv(index=False)
            st.download_button(
                label="📊 Download Carry Marks",
                data=csv_carry,
                file_name=f"carry_marks_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    with col2:
        if not assignments_df.empty:
            csv_assignments = assignments_df.to_csv(index=False)
            st.download_button(
                label="📋 Download Assignments",
                data=csv_assignments,
                file_name=f"assignments_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    with col3:
        if not course_stats_df.empty:
            csv_courses = course_stats_df.to_csv(index=False)
            st.download_button(
                label="📚 Download Course Stats",
                data=csv_courses,
                file_name=f"course_statistics_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )