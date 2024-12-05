from flask import Flask, request, jsonify, session, render_template, send_file
from flask_sqlalchemy import SQLAlchemy
from fpdf import FPDF
import io
import os

# Initialize SQLAlchemy globally
db = SQLAlchemy()

# Create Flask app
app = Flask(__name__)

# Configure the app
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cancer_risk.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "your_secret_key"

# Initialize SQLAlchemy with the app
db.init_app(app)

# Define the database model
class UserRiskAssessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    risk_level = db.Column(db.String(20), nullable=False)
    risk_score = db.Column(db.Integer, nullable=False)

# Create the database within the app context
with app.app_context():
    db.create_all()

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

    # Save user details and risk assessment to the database
    user = UserRiskAssessment(
        name=data.get("name"),
        email=data.get("email"),
        phone=data.get("phone"),
        risk_level=risk_level,
        risk_score=risk_score
    )
    db.session.add(user)
    db.session.commit()

    # Store user ID in session for PDF download
    session['user_id'] = user.id

    # Response for the frontend
    color_map = {"Low": "green", "Moderate": "yellow", "High": "red"}
    return jsonify({"level": risk_level, "color": color_map[risk_level]})

@app.route('/download-pdf', methods=['GET'])
def download_pdf():
    user_id = session.get('user_id')
    if not user_id:
        return "No data available to generate PDF. Please complete the assessment first.", 400

    user = UserRiskAssessment.query.get(user_id)
    if not user:
        return "User not found.", 404

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", style='B', size=16)
    pdf.cell(0, 10, txt="Blood Cancer Risk Assessment Results", ln=True, align='C')
    pdf.ln(20)

    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, txt=f"Name: {user.name}", ln=True)
    pdf.cell(0, 10, txt=f"Email: {user.email}", ln=True)
    pdf.cell(0, 10, txt=f"Phone: {user.phone}", ln=True)
    pdf.cell(0, 10, txt=f"Risk Level: {user.risk_level}", ln=True)

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
