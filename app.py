from flask import Flask, request, jsonify, session, render_template, send_file, Response
from fpdf import FPDF
from supabase import create_client, Client
import os
import io

# Flask app setup
app = Flask(__name__)
app.secret_key = "ZEcB6qbSM6dkNFpSnbKynEI8Y92sj9Xm@dpg-ct8mfqaj1k6c73e8i1mg-a"

# Supabase configuration
SUPABASE_URL = "https://konguabcywwajjjsgzwx.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtvbmd1YWJjeXd3YWpqanNnend4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzMzOTIyNTEsImV4cCI6MjA0ODk2ODI1MX0.ImsMYqqxrLojCSP_uJvHOWUbrcoOOT9OHm5_ZvlXZ5g"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    data = request.json
    risk_score = 0

    # Risk scoring logic
    if data.get("q1") == "Yes":
        risk_score += 2
    if data.get("q2") == "Yes":
        risk_score += 1
    if data.get("q3") == "Yes":
        risk_score += 1
    if data.get("q4") == "Yes":
        risk_score += 2
    if data.get("q5") == "Yes":
        risk_score += 3
    if data.get("q6") == "Yes":
        risk_score += 2
    if data.get("q7") == "30-50":
        risk_score += 1
    elif data.get("q7") == "Over 50":
        risk_score += 2
    if data.get("q8") == "Yes":
        risk_score += 2
    if data.get("q9") == "Yes":
        risk_score += 2

    # Determine risk level
    if risk_score <= 3:
        risk_level = "Low"
    elif 4 <= risk_score <= 6:
        risk_level = "Moderate"
    else:
        risk_level = "High"

    # Save user details and risk assessment to Supabase
    response = supabase.table("user_risk_assessment").insert({
        "name": data.get("name"),
        "email": data.get("email"),
        "phone": data.get("phone"),
        "risk_level": risk_level,
        "risk_score": risk_score
    }).execute()

    try:
        # Get the JSON data from the request
        data = request.get_json()
        
        # Example: process the data (you can save it to the database here)
        name = data.get("name")
        email = data.get("email")
        phone = data.get("phone")
        risk_level = data.get("risk_level")
        risk_score = data.get("risk_score")

        # Here, you can process the data or store it in the database

        # For now, return a success message
        return jsonify({"message": "Form submitted successfully!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    if response.status_code == 201:
        session['user_id'] = response.data[0]['id']
        color_map = {"Low": "green", "Moderate": "yellow", "High": "red"}
        return jsonify({"level": risk_level, "color": color_map[risk_level]})
    else:
        return jsonify({"error": "Failed to save data"}), 500

@app.route('/download-pdf', methods=['GET'])
def download_pdf():
    user_id = session.get('user_id')
    if not user_id:
        return "No data available to generate PDF. Please complete the assessment first.", 400

    response = supabase.table("user_risk_assessment").select("*").eq("id", user_id).execute()
    if response.status_code != 200 or len(response.data) == 0:
        return "User not found.", 404

    user = response.data[0]

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", style='B', size=16)
    pdf.cell(0, 10, txt="Blood Cancer Risk Assessment Results", ln=True, align='C')
    pdf.ln(20)

    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, txt=f"Name: {user['name']}", ln=True)
    pdf.cell(0, 10, txt=f"Email: {user['email']}", ln=True)
    pdf.cell(0, 10, txt=f"Phone: {user['phone']}", ln=True)
    pdf.cell(0, 10, txt=f"Risk Level: {user['risk_level']}", ln=True)

    pdf.ln(10)
    pdf.cell(0, 10, txt="This assessment is not a definitive diagnosis. Please consult a healthcare professional.", ln=True, align='C')

    pdf_output = io.BytesIO()
    pdf_data = pdf.output(dest='S').encode('latin1')
    pdf_output.write(pdf_data)
    pdf_output.seek(0)

    return send_file(
        pdf_output,
        as_attachment=True,
        download_name="risk_assessment_results.pdf",
        mimetype="application/pdf"
    )

if __name__ == "__main__":
    app.run(debug=True)
