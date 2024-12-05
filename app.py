from flask import Flask, request, jsonify, render_template, send_file, session
import io
from flask_sqlalchemy import SQLAlchemy

# Initialize Flask app
app = Flask(__name__)

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cancer_risk.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)
from fpdf import FPDF
app = Flask(__name__)


app = Flask(__name__)
app.secret_key = "badjnidwne1iebwnd"  # Replace with a secure, random value

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


class UserRiskAssessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    risk_level = db.Column(db.String(20), nullable=False)
    risk_score = db.Column(db.Integer, nullable=False)

# Create the database tables
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

    # Response for the frontend
    color_map = {"Low": "green", "Moderate": "yellow", "High": "red"}
    return jsonify({"level": risk_level, "color": color_map[risk_level]})

@app.route('/results', methods=['GET'])
def get_results():
    users = UserRiskAssessment.query.all()
    results = [
        {
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "risk_level": user.risk_level,
            "risk_score": user.risk_score,
        }
        for user in users
    ]
    return jsonify(results)


@app.route('/download', methods=['GET'])
def download():
    user_details = session.get('user_details')

    if not user_details:
        app.logger.error("No user details available for text file download.")
        return "No data available to download. Please complete the assessment first.", 400

    output = io.StringIO()
    output.write("Blood Cancer Risk Assessment Results\n\n")
    output.write(f"Name: {user_details['name']}\n")
    output.write(f"Email: {user_details['email']}\n")
    output.write(f"Phone: {user_details['phone']}\n")
    output.write(f"Risk Level: {user_details['risk_level']}\n")

    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        as_attachment=True,
        download_name="risk_assessment_results.txt",
        mimetype="text/plain"
    )



    

@app.route('/download-pdf', methods=['GET'])
def download_pdf():
    user_details = session.get('user_details')

    if not user_details:
        app.logger.error("No user details available for PDF generation.")
        return "No data available to generate PDF. Please complete the assessment first.", 400

    pdf = FPDF()
    pdf.add_page()
    logo_path = "https://i.ibb.co/R3FWq3y/logo.png"  # Replace with the actual path to your logo
    pdf.image(logo_path, x=10, y=8, w=30)  # Adjust the size and position as needed
    pdf.set_font("Arial", style='B', size=16)
    pdf.cell(0, 10, txt="Blood Cancer Risk Assessment Results", ln=True, align='C')
    pdf.ln(20)
    

    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, txt=f"Name: {user_details.get('name', 'N/A')}", ln=True)
    pdf.cell(0, 10, txt=f"Email: {user_details.get('email', 'N/A')}", ln=True)
    pdf.cell(0, 10, txt=f"Phone: {user_details.get('phone', 'N/A')}", ln=True)

    risk_level = user_details.get('risk_level', 'N/A')
    color_map = {"Low": (0, 255, 0), "Moderate": (255, 255, 0), "High": (255, 0, 0)}
    color = color_map.get(risk_level, (0, 0, 0))  # Default to black if unknown
    pdf.set_text_color(*color)
    pdf.cell(0, 10, txt=f"Risk Level: {risk_level}", ln=True)
    pdf.set_text_color(0, 0, 0)  # Reset to black

    # Footer or additional notes
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
