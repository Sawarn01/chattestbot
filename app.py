from flask import Flask, request, jsonify, render_template, send_file, session
import io
from fpdf import FPDF
app = Flask(__name__)

app = Flask(__name__)
app.secret_key = "badjnidwne1iebwnd"  # Replace with a secure, random value

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    data = request.json
    user_details = {
        "name": data.get("name"),
        "email": data.get("email"),
        "phone": data.get("phone"),
        "risk_level": "Low"  # Default value or calculated risk level
    }
    # Risk calculation logic here...
    risk_score = 0
    # Determine risk level based on risk_score...
    if risk_score <= 3:
        user_details["risk_level"] = "Low"
    elif 4 <= risk_score <= 6:
        user_details["risk_level"] = "Moderate"
    else:
        user_details["risk_level"] = "High"

    # Store in session
    session['user_details'] = user_details

    return jsonify({"level": user_details["risk_level"]})


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
    pdf.set_font("Arial", style='B', size=16)
    pdf.cell(0, 10, txt="Blood Cancer Risk Assessment Results", ln=True, align='C')
    pdf.ln(20)
    

    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, txt=f"Name: {user_details.get('name', 'N/A')}", ln=True)
    pdf.cell(0, 10, txt=f"Email: {user_details.get('email', 'N/A')}", ln=True)
    pdf.cell(0, 10, txt=f"Phone: {user_details.get('phone', 'N/A')}", ln=True)
    pdf.cell(0, 10, txt=f"Risk Level: {user_details.get('risk_level', 'N/A')}", ln=True)

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
