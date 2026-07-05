import os
import base64
import io
import csv
import threading
import streamlit as st
from datetime import datetime
from PIL import Image
import numpy as np
import bcrypt

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, Response
import re

# Supabase database wrapper methods
from src.database.db import (
    teacher_login, create_teacher, check_teacher_exists,
    get_all_students, create_student, check_student_exists_by_name,
    create_subject, get_teacher_subjects,
    enroll_student_to_subject, unenroll_student_to_subject,
    get_student_subjects, get_student_attendance,
    create_attendance, get_attendance_for_teacher, supabase,
    resolve_subject_registry_code
)

# AI Recognition Pipelines
from src.pipelines.face_pipeline import predict_attendance, get_face_embeddings, train_classifier
from src.pipelines.voice_pipeline import get_voice_embedding

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Simple global config dictionary
system_config = {
    'face_threshold': 0.6,
    'voice_threshold': 0.7,
}

# ---------------------------------------------------------------------------
# Flask Authentication Decorator
# ---------------------------------------------------------------------------
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this section.', 'error')
            return redirect(url_for('login_route'))
        return f(*args, **kwargs)
    return decorated_function

# ---------------------------------------------------------------------------
# Flask Web Routes
# ---------------------------------------------------------------------------

@app.route('/')
def index_route():
    if 'user_id' in session:
        return redirect(url_for('dashboard_route'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login_route():
    if 'user_id' in session:
        return redirect(url_for('dashboard_route'))
        
    if request.method == 'POST':
        role = request.form.get('role', 'teacher')
        username = request.form.get('username')
        password = request.form.get('password')
        
        if role == 'teacher':
            teacher = teacher_login(username, password)
            if teacher:
                session['user_id'] = teacher['teacher_id']
                session['name'] = teacher['name']
                session['role'] = 'teacher'
                flash('Welcome back, ' + teacher['name'] + '!', 'success')
                return redirect(url_for('dashboard_route'))
            else:
                flash('Invalid teacher username or password.', 'error')
        else:
            flash('Face ID authentication is required for students.', 'error')
            
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register_route():
    if 'user_id' in session:
        return redirect(url_for('dashboard_route'))
        
    if request.method == 'POST':
        role = request.form.get('role', 'teacher')
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        name = request.form.get('name', '').strip()
        
        if role == 'teacher':
            # --- Validation ---
            if not username or not name or not password:
                flash('All fields are required.', 'error')
            elif len(username) < 3:
                flash('Username must be at least 3 characters long.', 'error')
            elif len(password) < 6:
                flash('Password must be at least 6 characters long.', 'error')
            elif password != confirm_password:
                flash('Passwords do not match. Please try again.', 'error')
            elif check_teacher_exists(username):
                flash(f'Username "{username}" is already registered. Please choose a different one or login.', 'error')
            else:
                try:
                    create_teacher(username, password, name)
                    flash(f'Teacher account created successfully! Welcome, {name}. Please login.', 'success')
                    return redirect(url_for('login_route') + '?role=teacher')
                except Exception as e:
                    flash(f'Registration failed: {str(e)}', 'error')
                    
    return render_template('register.html')

@app.route('/logout')
def logout_route():
    session.clear()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('index_route'))

@app.route('/dashboard')
@login_required
def dashboard_route():
    role = session.get('role')
    user_id = session.get('user_id')
    
    if role == 'student':
        # Student Dashboard (Image 3)
        subjects = get_student_subjects(user_id)
        logs = get_student_attendance(user_id)
        
        # Calculate subject stats
        stats_map = {}
        for log in logs:
            sid = log['subject_id']
            if sid not in stats_map:
                stats_map[sid] = {"total": 0, "attended": 0}
            stats_map[sid]['total'] += 1
            if log.get('is_present'):
                stats_map[sid]['attended'] += 1
                
        subjects_with_stats = []
        for sub_node in subjects:
            sub = sub_node['subjects']
            sid = sub['subject_id']
            stats = stats_map.get(sid, {"total": 0, "attended": 0})
            subjects_with_stats.append({
                'subject_id': sid,
                'name': sub['name'],
                'subject_code': sub['subject_code'],
                'section': sub['section'],
                'total': stats['total'],
                'attended': stats['attended'],
                'rate': round((stats['attended'] / stats['total'] * 100), 1) if stats['total'] > 0 else 0
            })
            
        return render_template('dashboard.html', active_page='dashboard', subjects=subjects_with_stats)
    else:
        # Teacher Dashboard
        subjects = get_teacher_subjects(user_id)
        students = get_all_students()
        logs = get_attendance_for_teacher(user_id)
        
        # Calculate stats
        total_students = len(students)
        total_subjects = len(subjects)
        
        # Filter for today's logs
        today_str = datetime.now().strftime("%Y-%m-%d")
        today_logs = [l for l in logs if l['timestamp'].startswith(today_str)]
        present_today = len([l for l in today_logs if l.get('is_present')])
        absent_today = len(today_logs) - present_today
        
        # Line chart data (last 7 days attendance rates)
        # Group attendance by date
        date_stats = {}
        for log in logs:
            date_part = log['timestamp'][:10]
            if date_part not in date_stats:
                date_stats[date_part] = {"total": 0, "present": 0}
            date_stats[date_part]['total'] += 1
            if log.get('is_present'):
                date_stats[date_part]['present'] += 1
                
        sorted_dates = sorted(date_stats.keys())[-7:]
        chart_labels = sorted_dates
        chart_dataset = [
            round((date_stats[d]['present'] / date_stats[d]['total'] * 100), 1) if date_stats[d]['total'] > 0 else 0
            for d in sorted_dates
        ]
        
        # Defaulter list (students with < 75% attendance)
        student_course_stats = {}
        for log in logs:
            std_id = log['student_id']
            if std_id not in student_course_stats:
                student_course_stats[std_id] = {"total": 0, "present": 0, "name": log['student_name']}
            student_course_stats[std_id]['total'] += 1
            if log.get('is_present'):
                student_course_stats[std_id]['present'] += 1
                
        defaulters = []
        for std_id, stats in student_course_stats.items():
            rate = round((stats['present'] / stats['total'] * 100), 1) if stats['total'] > 0 else 0
            if rate < 75.0:
                defaulters.append({
                    'name': stats['name'],
                    'rate': rate
                })
                
        return render_template(
            'dashboard.html',
            active_page='dashboard',
            total_students=total_students,
            total_subjects=total_subjects,
            present_today=present_today,
            absent_today=absent_today,
            chart_labels=chart_labels,
            chart_dataset=chart_dataset,
            defaulters=defaulters
        )

@app.route('/recognition')
@login_required
def recognition_route():
    if session.get('role') != 'teacher':
        return redirect(url_for('dashboard_route'))
    subjects = get_teacher_subjects(session['user_id'])
    return render_template('recognition.html', active_page='recognition', subjects=subjects)

@app.route('/students')
@login_required
def students_route():
    if session.get('role') != 'teacher':
        return redirect(url_for('dashboard_route'))
    students = get_all_students()
    return render_template('students.html', active_page='students', students=students)

@app.route('/subjects')
@login_required
def subjects_route():
    if session.get('role') != 'teacher':
        return redirect(url_for('dashboard_route'))
    subjects = get_teacher_subjects(session['user_id'])
    return render_template('subjects.html', active_page='subjects', subjects=subjects)

@app.route('/attendance')
@login_required
def attendance_route():
    if session.get('role') != 'teacher':
        return redirect(url_for('dashboard_route'))
        
    search_query = request.args.get('search', '').strip()
    selected_subject = request.args.get('subject_id', '').strip()
    
    logs = get_attendance_for_teacher(session['user_id'])
    subjects = get_teacher_subjects(session['user_id'])
    
    # Filter logs based on search and subject
    filtered_logs = []
    for log in logs:
        match_search = True
        match_subject = True
        
        if search_query:
            match_search = search_query.lower() in log['student_name'].lower()
        if selected_subject:
            match_subject = log['subject_id'] == selected_subject
            
        if match_search and match_subject:
            filtered_logs.append({
                'student_name': log['student_name'],
                'subject_name': log['subject_name'],
                'subject_code': log['subject_code'],
                'section': log['section'],
                'timestamp': log['timestamp'][:19].replace('T', ' '),
                'status': 'Present' if log['is_present'] else 'Absent'
            })
            
    return render_template(
        'attendance.html',
        active_page='attendance',
        logs=filtered_logs,
        subjects=subjects,
        search_query=search_query,
        selected_subject=selected_subject
    )

@app.route('/reports')
@login_required
def reports_route():
    if session.get('role') != 'teacher':
        return redirect(url_for('dashboard_route'))
        
    logs = get_attendance_for_teacher(session['user_id'])
    subjects = get_teacher_subjects(session['user_id'])
    
    # Subject-wise comparison data
    sub_totals = {}
    for log in logs:
        sid = log['subject_id']
        sname = log['subject_name']
        if sid not in sub_totals:
            sub_totals[sid] = {"name": sname, "total": 0, "present": 0}
        sub_totals[sid]['total'] += 1
        if log.get('is_present'):
            sub_totals[sid]['present'] += 1
            
    comparison_labels = []
    comparison_dataset = []
    for sid, stats in sub_totals.items():
        comparison_labels.append(stats['name'])
        rate = round((stats['present'] / stats['total'] * 100), 1) if stats['total'] > 0 else 0
        comparison_dataset.append(rate)
        
    return render_template(
        'reports.html',
        active_page='reports',
        comparison_labels=comparison_labels,
        comparison_dataset=comparison_dataset
    )

@app.route('/settings')
@login_required
def settings_route():
    return render_template('settings.html', active_page='settings', config=system_config)

# ---------------------------------------------------------------------------
# REST API Endpoints
# ---------------------------------------------------------------------------

@app.route('/api/login_face', methods=['POST'])
def api_login_face():
    data = request.json
    img_b64 = data.get('image')
    if not img_b64:
        return jsonify({'success': False, 'message': 'No image data provided.'}), 400
        
    try:
        # Base64 decoding
        if ',' in img_b64:
            img_b64 = img_b64.split(',')[1]
        img_bytes = base64.b64decode(img_b64)
        image = Image.open(io.BytesIO(img_bytes)).convert('RGB')
        img_arr = np.array(image)
        
        detected, all_ids, num_faces = predict_attendance(img_arr)
        
        if num_faces == 0:
            return jsonify({'success': False, 'message': 'No face detected.'})
        elif num_faces > 1:
            return jsonify({'success': False, 'message': 'Multiple faces detected.'})
            
        if detected:
            student_id = list(detected.keys())[0]
            # Fetch student info from Supabase
            all_students = get_all_students()
            student = next((s for s in all_students if s['student_id'] == student_id), None)
            
            if student:
                session['user_id'] = student['student_id']
                session['name'] = student['name']
                session['role'] = 'student'
                return jsonify({'success': True, 'name': student['name']})
                
        return jsonify({'success': False, 'message': 'Face biometrics did not match any enrolled student.'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500

@app.route('/api/register_student', methods=['POST'])
def api_register_student():
    name = request.form.get('name', '').strip()
    face_img_b64 = request.form.get('face_image')
    voice_file = request.files.get('voice_clip')
    
    # --- Validation ---
    if not name:
        return jsonify({'success': False, 'message': 'Student name is required.'}), 400
    if len(name) < 2:
        return jsonify({'success': False, 'message': 'Name must be at least 2 characters.'}), 400
    if not face_img_b64:
        return jsonify({'success': False, 'message': 'Face photo is required for biometric enrolment.'}), 400
    
    # Check if student with same name already registered
    if check_student_exists_by_name(name):
        return jsonify({
            'success': False,
            'message': f'A student named "{name}" is already registered. If this is you, please use the Student Login instead.',
            'already_registered': True
        }), 409
        
    try:
        if ',' in face_img_b64:
            face_img_b64 = face_img_b64.split(',')[1]
        img_bytes = base64.b64decode(face_img_b64)
        image = Image.open(io.BytesIO(img_bytes)).convert('RGB')
        img_arr = np.array(image)
        
        # Extract face embeddings
        encodings = get_face_embeddings(img_arr)
        if not encodings:
            return jsonify({'success': False, 'message': 'No face detected in the photo. Please ensure your face is clearly visible and well-lit.'})
            
        face_emb = encodings[0].tolist()
        
        # Optional voice embeddings
        voice_emb = None
        if voice_file:
            voice_bytes = voice_file.read()
            voice_emb = get_voice_embedding(voice_bytes)
            
        res = create_student(name, face_embedding=face_emb, voice_embedding=voice_emb)
        if res:
            # Rebuild SVM classifier
            train_classifier()
            # Log the student in
            student = res[0]
            session['user_id'] = student['student_id']
            session['name'] = student['name']
            session['role'] = 'student'
            return jsonify({'success': True, 'message': f'Welcome, {name}! Your biometric profile has been registered.'})
            
        return jsonify({'success': False, 'message': 'Database insert failed. Please try again.'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500

@app.route('/api/detect_faces', methods=['POST'])
def api_detect_faces():
    data = request.json
    img_b64 = data.get('image')
    if not img_b64:
        return jsonify({'success': False, 'message': 'No image provided.'}), 400
        
    try:
        if ',' in img_b64:
            img_b64 = img_b64.split(',')[1]
        img_bytes = base64.b64decode(img_b64)
        image = Image.open(io.BytesIO(img_bytes)).convert('RGB')
        img_arr = np.array(image)
        
        detected, all_ids, num_faces = predict_attendance(img_arr)
        
        # Fetch names for recognized student IDs
        all_students = get_all_students()
        student_map = {s['student_id']: s['name'] for s in all_students}
        
        recognized_list = []
        for sid, conf in detected.items():
            recognized_list.append({
                'student_id': sid,
                'name': student_map.get(sid, 'Unknown Student'),
                'confidence': round(conf * 100, 1)
            })
            
        return jsonify({
            'success': True,
            'num_faces': num_faces,
            'recognized': recognized_list
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/create_attendance', methods=['POST'])
@login_required
def api_create_attendance():
    data = request.json
    subject_id = data.get('subject_id')
    student_ids = data.get('student_ids', [])
    
    if not subject_id:
        return jsonify({'success': False, 'message': 'Missing subject ID.'}), 400
        
    try:
        # Get all enrolled students for this course to mark absent students
        # For simplicity, we mark the student_ids as Present (is_present=True)
        # SQLite / Supabase query wrapper for enrollment:
        # We can construct the logs list
        now_str = datetime.now().isoformat()
        
        # Call db helper to log attendance
        is_present_list = [True] * len(student_ids)
        create_attendance(subject_id, student_ids, is_present_list, now_str)
        
        return jsonify({'success': True, 'count': len(student_ids)})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/create_subject', methods=['POST'])
@login_required
def api_create_subject():
    data = request.json
    name = (data.get('name') or '').strip()
    code = (data.get('code') or '').strip()
    section = (data.get('section') or '').strip()
    
    if not name or not code or not section:
        return jsonify({'success': False, 'message': 'Missing parameters.'}), 400
    if len(name) < 2:
        return jsonify({'success': False, 'message': 'Subject name must be at least 2 characters.'}), 400
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9 _/-]{1,39}', code):
        return jsonify({'success': False, 'message': 'Subject code must use letters, numbers, spaces, dashes, or slashes.'}), 400
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9 _/-]{0,39}', section):
        return jsonify({'success': False, 'message': 'Section must use letters, numbers, spaces, dashes, or slashes.'}), 400
        
    try:
        create_subject(code, name, section, session['user_id'])
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/enroll_subject', methods=['POST'])
@login_required
def api_enroll_subject():
    data = request.json
    subject_id = resolve_subject_registry_code(data.get('subject_id'))
    
    if not subject_id:
        return jsonify({'success': False, 'message': 'Enter a valid subject registry code.'}), 400
        
    try:
        enroll_student_to_subject(session['user_id'], subject_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/unenroll_subject', methods=['POST'])
@login_required
def api_unenroll_subject():
    data = request.json
    subject_id = resolve_subject_registry_code(data.get('subject_id'))
    
    if not subject_id:
        return jsonify({'success': False, 'message': 'Enter a valid subject registry code.'}), 400
        
    try:
        unenroll_student_to_subject(session['user_id'], subject_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/delete_student', methods=['POST'])
@login_required
def api_delete_student():
    data = request.json
    student_id = data.get('student_id')
    
    if not student_id:
        return jsonify({'success': False, 'message': 'Missing student ID.'}), 400
        
    try:
        # Delete from Supabase student profiles
        supabase.table('students').delete().eq('student_id', student_id).execute()
        # Re-train face classifier to clear deleted student features
        train_classifier()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/save_settings', methods=['POST'])
@login_required
def api_save_settings():
    data = request.json
    face_th = data.get('face_threshold')
    voice_th = data.get('voice_threshold')
    
    try:
        if face_th:
            system_config['face_threshold'] = float(face_th)
        if voice_th:
            system_config['voice_threshold'] = float(voice_th)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/attendance/export')
@login_required
def attendance_export_route():
    logs = get_attendance_for_teacher(session['user_id'])
    
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['Student Name', 'Subject Name', 'Subject Code', 'Section', 'Timestamp', 'Status'])
    
    for log in logs:
        cw.writerow([
            log['student_name'],
            log['subject_name'],
            log['subject_code'],
            log['section'],
            log['timestamp'][:19].replace('T', ' '),
            'Present' if log['is_present'] else 'Absent'
        ])
        
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=attendance_logs.csv"
    output.headers["Content-type"] = "text/csv"
    return output

def make_response(data):
    return Response(data, mimetype='text/csv')

# ---------------------------------------------------------------------------
# Swagger UI Endpoints
# ---------------------------------------------------------------------------

@app.route('/swagger.json')
def swagger_json_route():
    return app.send_static_file('swagger.json')

@app.route('/swagger')
def swagger_ui_route():
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>Fluentia API Documentation</title>
  <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css" />
  <link rel="icon" type="image/png" href="https://i.ibb.co/YTYGn5qV/logo.png" />
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <style>
    /* Premium customization for Swagger UI */
    body {
      font-family: 'Outfit', sans-serif !important;
      background-color: #0f172a; /* Slate 900 background */
      color: #f1f5f9;
      margin: 0;
    }
    .swagger-ui {
      font-family: 'Outfit', sans-serif !important;
    }
    /* Brand Header */
    .brand-header {
      background: linear-gradient(135deg, #1e1b4b 0%, #311042 100%);
      padding: 16px 24px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    .brand-header .logo-container {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .brand-header img {
      height: 40px;
      width: auto;
    }
    .brand-header h1 {
      color: #ffffff;
      margin: 0;
      font-size: 22px;
      font-weight: 700;
      letter-spacing: 0.5px;
    }
    .brand-header .badge {
      background: rgba(255, 255, 255, 0.1);
      color: #e2e8f0;
      padding: 4px 10px;
      border-radius: 9999px;
      font-size: 12px;
      font-weight: 500;
      border: 1px solid rgba(255, 255, 255, 0.15);
    }
    .brand-header .back-btn {
      color: #94a3b8;
      text-decoration: none;
      font-size: 14px;
      font-weight: 500;
      padding: 8px 16px;
      border-radius: 8px;
      transition: all 0.2s;
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.05);
    }
    .brand-header .back-btn:hover {
      color: #ffffff;
      background: rgba(255, 255, 255, 0.1);
      border-color: rgba(255, 255, 255, 0.2);
    }
    /* Dark Mode Overrides for Swagger UI elements */
    .swagger-ui .info .title, 
    .swagger-ui .info h1, 
    .swagger-ui .info h2, 
    .swagger-ui .info h3, 
    .swagger-ui .info h4, 
    .swagger-ui .info h5, 
    .swagger-ui .info p, 
    .swagger-ui .info li,
    .swagger-ui .info table {
      color: #f1f5f9 !important;
    }
    .swagger-ui .info .description {
      color: #94a3b8 !important;
      font-size: 15px;
      line-height: 1.6;
    }
    .swagger-ui .scheme-container {
      background-color: #1e293b !important;
      box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2) !important;
      border-radius: 12px;
      margin: 20px 0;
      padding: 20px !important;
      border: 1px solid rgba(255, 255, 255, 0.05);
    }
    .swagger-ui select {
      background-color: #0f172a !important;
      color: #f1f5f9 !important;
      border: 1px solid rgba(255, 255, 255, 0.1) !important;
      border-radius: 6px !important;
    }
    .swagger-ui .opblock {
      background-color: #1e293b !important;
      border: 1px solid rgba(255, 255, 255, 0.05) !important;
      border-radius: 12px !important;
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
      overflow: hidden;
    }
    .swagger-ui .opblock .opblock-summary {
      border-bottom: 1px solid rgba(255, 255, 255, 0.05) !important;
      padding: 12px 20px !important;
    }
    .swagger-ui .opblock .opblock-summary-path {
      color: #f1f5f9 !important;
      font-weight: 600 !important;
    }
    .swagger-ui .opblock-description-wrapper p, 
    .swagger-ui .opblock-external-docs-wrapper p, 
    .swagger-ui .opblock-title_normal p {
      color: #cbd5e1 !important;
    }
    .swagger-ui .tabli button {
      color: #94a3b8 !important;
    }
    .swagger-ui .tabli.active button {
      color: #38bdf8 !important;
    }
    .swagger-ui .opblock .opblock-section-header {
      background-color: rgba(255, 255, 255, 0.02) !important;
      border-bottom: 1px solid rgba(255, 255, 255, 0.05) !important;
      border-top: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    .swagger-ui .opblock .opblock-section-header h4 {
      color: #f1f5f9 !important;
    }
    .swagger-ui .table-container,
    .swagger-ui table.headers {
      padding: 10px 20px !important;
    }
    .swagger-ui table tbody tr td {
      color: #cbd5e1 !important;
    }
    .swagger-ui .parameter__name {
      color: #f1f5f9 !important;
      font-weight: 600 !important;
    }
    .swagger-ui .parameter__type {
      color: #38bdf8 !important;
    }
    .swagger-ui input[type=text] {
      background-color: #0f172a !important;
      color: #f1f5f9 !important;
      border: 1px solid rgba(255, 255, 255, 0.1) !important;
      border-radius: 6px !important;
      padding: 8px 12px !important;
    }
    .swagger-ui .btn {
      border-radius: 8px !important;
      font-weight: 600 !important;
      transition: all 0.2s !important;
      border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    .swagger-ui .btn.execute {
      background-color: #3b82f6 !important;
      color: #ffffff !important;
      border-color: #3b82f6 !important;
    }
    .swagger-ui .btn.execute:hover {
      background-color: #2563eb !important;
    }
    .swagger-ui .btn.cancel {
      background-color: #ef4444 !important;
      color: #ffffff !important;
      border-color: #ef4444 !important;
    }
    .swagger-ui .btn.cancel:hover {
      background-color: #dc2626 !important;
    }
    .swagger-ui .response-col_status {
      color: #f1f5f9 !important;
    }
    .swagger-ui .response-col_links {
      color: #cbd5e1 !important;
    }
    .swagger-ui .opblock-body pre.microlight {
      background-color: #0f172a !important;
      border: 1px solid rgba(255, 255, 255, 0.05) !important;
      border-radius: 8px !important;
      color: #34d399 !important;
      padding: 16px !important;
    }
    .swagger-ui .opblock-body pre.microlight code {
      font-family: monospace !important;
    }
    .swagger-ui .model-box {
      background-color: #0f172a !important;
      border: 1px solid rgba(255, 255, 255, 0.05) !important;
      border-radius: 8px !important;
      padding: 12px !important;
    }
    .swagger-ui .model-title {
      color: #f1f5f9 !important;
    }
    .swagger-ui .model {
      color: #cbd5e1 !important;
    }
    .swagger-ui .prop-type {
      color: #38bdf8 !important;
    }
    .swagger-ui .prop-format {
      color: #94a3b8 !important;
    }
    /* Specific styling for HTTP methods badge */
    .swagger-ui .opblock.opblock-post {
      background-color: #1e293b !important;
      border-color: rgba(16, 185, 129, 0.2) !important;
    }
    .swagger-ui .opblock.opblock-post .opblock-summary-method {
      background-color: #10b981 !important;
      color: #ffffff !important;
      border-radius: 6px !important;
    }
    .swagger-ui .opblock.opblock-get {
      background-color: #1e293b !important;
      border-color: rgba(59, 130, 246, 0.2) !important;
    }
    .swagger-ui .opblock.opblock-get .opblock-summary-method {
      background-color: #3b82f6 !important;
      color: #ffffff !important;
      border-radius: 6px !important;
    }
    /* Hide topbar since we have our custom premium header */
    .swagger-ui .topbar {
      display: none !important;
    }
  </style>
</head>
<body>
  <header class="brand-header">
    <div class="logo-container">
      <img src="https://i.ibb.co/YTYGn5qV/logo.png" alt="Fluentia Logo" />
      <h1>Fluentia Portal</h1>
      <span class="badge">API Playground</span>
    </div>
    <a href="/" class="back-btn">&#8592; Back to Portal</a>
  </header>
  <div id="swagger-ui"></div>
  <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js" charset="UTF-8"></script>
  <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-standalone-preset.js" charset="UTF-8"></script>
  <script>
    window.onload = () => {
      window.ui = SwaggerUIBundle({
        url: '/swagger.json',
        dom_id: '#swagger-ui',
        presets: [
          SwaggerUIBundle.presets.apis,
          SwaggerUIStandalonePreset
        ],
        layout: "BaseLayout",
        deepLinking: true,
        persistAuthorization: true
      });
    };
  </script>
</body>
</html>"""

# ---------------------------------------------------------------------------
# Streamlit & Background Thread Initialization
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    # Detect if run under Streamlit
    try:
        is_streamlit = st.runtime.exists()
    except (ImportError, AttributeError):
        is_streamlit = False
    
    if is_streamlit:
        # Start Flask in a background thread once per server process
        if not hasattr(app, '_flask_started'):
            app._flask_started = True
            def run_flask():
                app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
            
            t = threading.Thread(target=run_flask, daemon=True)
            t.start()

        # Streamlit Page Config & Redirect Reroute
        st.set_page_config(
            page_title="Fluentia Portal",
            page_icon="https://i.ibb.co/YTYGn5qV/logo.png",
            layout="centered"
        )

        st.markdown('<meta http-equiv="refresh" content="0;URL=\'http://localhost:5000/\'" />', unsafe_allow_html=True)

        st.title("Launching Fluentia Portal...")
        st.write("Connecting to the premium Fluent UI Attendance portal at http://localhost:5000...")
        st.markdown("[Click here to open the portal directly](http://localhost:5000)")
    else:
        # Running Flask in foreground (direct script execution)
        app.run(host="0.0.0.0", port=5000, debug=True)
