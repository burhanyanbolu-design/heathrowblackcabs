from flask import Flask, request, jsonify
from flask_cors import CORS
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

app = Flask(__name__)
CORS(app)

# --- CONFIG ---
GMAIL_USER = os.environ.get('GMAIL_USER', 'YOUR_GMAIL@gmail.com')
GMAIL_PASS = os.environ.get('GMAIL_PASS', 'YOUR_APP_PASSWORD')
BUSINESS_EMAIL = 'info@heathrowblackcabs.co.uk'

def send_email(to, subject, html_body):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = GMAIL_USER
    msg['To'] = to
    msg.attach(MIMEText(html_body, 'html'))
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(GMAIL_USER, GMAIL_PASS)
        server.sendmail(GMAIL_USER, to, msg.as_string())

@app.route('/book', methods=['POST'])
def book():
    try:
        b = request.json

        # --- Email to CUSTOMER ---
        customer_html = f"""
        <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;background:#000;color:#fff;padding:40px;border-radius:12px">
          <div style="text-align:center;margin-bottom:30px">
            <h1 style="color:#c9a84c;font-size:28px;margin-bottom:8px">Heathrow Black Cabs</h1>
            <p style="color:#888;font-size:14px">TfL Licensed Airport Transfer Service</p>
          </div>
          <div style="background:#111;border:1px solid #333;border-radius:10px;padding:24px;margin-bottom:24px">
            <h2 style="color:#fff;font-size:20px;margin-bottom:20px">&#9989; Booking Received</h2>
            <p style="color:#aaa;font-size:14px;margin-bottom:20px">Thank you <strong style="color:#fff">{b.get('name')}</strong>. We have received your booking and will confirm within minutes.</p>
            <table style="width:100%;border-collapse:collapse">
              <tr><td style="padding:10px 0;border-bottom:1px solid #222;color:#888;font-size:13px">Pickup</td><td style="padding:10px 0;border-bottom:1px solid #222;color:#fff;font-size:13px;text-align:right">{b.get('pickup')}</td></tr>
              <tr><td style="padding:10px 0;border-bottom:1px solid #222;color:#888;font-size:13px">Drop-off</td><td style="padding:10px 0;border-bottom:1px solid #222;color:#fff;font-size:13px;text-align:right">{b.get('dropoff')}</td></tr>
              <tr><td style="padding:10px 0;border-bottom:1px solid #222;color:#888;font-size:13px">Date &amp; Time</td><td style="padding:10px 0;border-bottom:1px solid #222;color:#fff;font-size:13px;text-align:right">{b.get('date')} at {b.get('time')}</td></tr>
              <tr><td style="padding:10px 0;border-bottom:1px solid #222;color:#888;font-size:13px">Passengers</td><td style="padding:10px 0;border-bottom:1px solid #222;color:#fff;font-size:13px;text-align:right">{b.get('passengers')}</td></tr>
              {'<tr><td style="padding:10px 0;border-bottom:1px solid #222;color:#888;font-size:13px">Flight</td><td style="padding:10px 0;border-bottom:1px solid #222;color:#fff;font-size:13px;text-align:right">' + b.get('flight','') + '</td></tr>' if b.get('flight') else ''}
              <tr><td style="padding:10px 0;border-bottom:1px solid #222;color:#888;font-size:13px">Payment</td><td style="padding:10px 0;border-bottom:1px solid #222;color:#fff;font-size:13px;text-align:right">{b.get('payment')}</td></tr>
              {'<tr><td style="padding:10px 0;border-bottom:1px solid #222;color:#888;font-size:13px">Extras</td><td style="padding:10px 0;border-bottom:1px solid #222;color:#fff;font-size:13px;text-align:right">' + b.get('specials','') + '</td></tr>' if b.get('specials') else ''}
              <tr><td style="padding:10px 0;color:#888;font-size:13px">Est. Price</td><td style="padding:10px 0;color:#c9a84c;font-size:20px;font-weight:bold;text-align:right">£{b.get('price')}</td></tr>
            </table>
          </div>
          <div style="background:#111;border:1px solid #333;border-radius:10px;padding:20px;text-align:center;margin-bottom:24px">
            <p style="color:#aaa;font-size:13px;margin-bottom:12px">Questions? Contact us directly:</p>
            <a href="tel:07740304061" style="color:#c9a84c;text-decoration:none;font-weight:bold;font-size:16px">&#128222; 07740304061</a>
          </div>
          <p style="text-align:center;color:#555;font-size:11px">Heathrow Black Cabs &middot; TfL Licensed &middot; heathrowblackcabs.co.uk</p>
        </div>
        """

        # --- Email to BUSINESS ---
        business_html = f"""
        <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;background:#000;color:#fff;padding:40px;border-radius:12px">
          <h2 style="color:#c9a84c">&#128663; NEW BOOKING</h2>
          <table style="width:100%;border-collapse:collapse;margin-top:20px">
            <tr><td style="padding:8px 0;color:#888;font-size:13px">Name</td><td style="padding:8px 0;color:#fff;font-size:13px">{b.get('name')}</td></tr>
            <tr><td style="padding:8px 0;color:#888;font-size:13px">Phone</td><td style="padding:8px 0;color:#fff;font-size:13px">{b.get('phone')}</td></tr>
            <tr><td style="padding:8px 0;color:#888;font-size:13px">Email</td><td style="padding:8px 0;color:#fff;font-size:13px">{b.get('email')}</td></tr>
            <tr><td style="padding:8px 0;color:#888;font-size:13px">Pickup</td><td style="padding:8px 0;color:#fff;font-size:13px">{b.get('pickup')}</td></tr>
            <tr><td style="padding:8px 0;color:#888;font-size:13px">Drop-off</td><td style="padding:8px 0;color:#fff;font-size:13px">{b.get('dropoff')}</td></tr>
            <tr><td style="padding:8px 0;color:#888;font-size:13px">Date &amp; Time</td><td style="padding:8px 0;color:#fff;font-size:13px">{b.get('date')} at {b.get('time')}</td></tr>
            <tr><td style="padding:8px 0;color:#888;font-size:13px">Passengers</td><td style="padding:8px 0;color:#fff;font-size:13px">{b.get('passengers')}</td></tr>
            {'<tr><td style="padding:8px 0;color:#888;font-size:13px">Flight</td><td style="padding:8px 0;color:#fff;font-size:13px">' + b.get('flight','') + '</td></tr>' if b.get('flight') else ''}
            <tr><td style="padding:8px 0;color:#888;font-size:13px">Payment</td><td style="padding:8px 0;color:#fff;font-size:13px">{b.get('payment')}</td></tr>
            {'<tr><td style="padding:8px 0;color:#888;font-size:13px">Extras</td><td style="padding:8px 0;color:#fff;font-size:13px">' + b.get('specials','') + '</td></tr>' if b.get('specials') else ''}
            {'<tr><td style="padding:8px 0;color:#888;font-size:13px">Notes</td><td style="padding:8px 0;color:#fff;font-size:13px">' + b.get('notes','') + '</td></tr>' if b.get('notes') else ''}
            <tr><td style="padding:8px 0;color:#888;font-size:13px">Est. Price</td><td style="padding:8px 0;color:#c9a84c;font-size:20px;font-weight:bold">£{b.get('price')}</td></tr>
          </table>
        </div>
        """

        # Send both emails
        customer_email = b.get('email')
        if customer_email:
            send_email(customer_email, 'Booking Confirmation — Heathrow Black Cabs', customer_html)
        send_email(BUSINESS_EMAIL, f"NEW BOOKING: {b.get('name')} — {b.get('date')} {b.get('time')}", business_html)

        return jsonify({'status': 'ok', 'message': 'Booking confirmed! Check your email.'})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005)
