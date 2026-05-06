from flask import Flask, request, jsonify
from flask_cors import CORS
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import stripe

app = Flask(__name__)
CORS(app)

# --- CONFIG ---
IONOS_USER = os.environ.get('IONOS_USER', 'info@heathrowblackcabs.co.uk')
IONOS_PASS = os.environ.get('IONOS_PASS', 'Yanbolu1973@')
BUSINESS_EMAIL = 'info@heathrowblackcabs.co.uk'

# Stripe configuration
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY', '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')

def send_email(to, subject, html_body):
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = IONOS_USER
        msg['To'] = to
        msg.attach(MIMEText(html_body, 'html'))
        
        # Try SMTP_SSL on port 465
        try:
            with smtplib.SMTP_SSL('smtp.ionos.co.uk', 465, timeout=10) as server:
                server.set_debuglevel(1)  # Enable debug output
                server.login(IONOS_USER, IONOS_PASS)
                server.sendmail(IONOS_USER, to, msg.as_string())
                print(f"Email sent successfully to {to}")
        except Exception as e:
            print(f"SMTP_SSL failed: {e}, trying SMTP with STARTTLS...")
            # Fallback to SMTP with STARTTLS on port 587
            with smtplib.SMTP('smtp.ionos.co.uk', 587, timeout=10) as server:
                server.set_debuglevel(1)
                server.starttls()
                server.login(IONOS_USER, IONOS_PASS)
                server.sendmail(IONOS_USER, to, msg.as_string())
                print(f"Email sent successfully to {to} via STARTTLS")
    except Exception as e:
        print(f"Failed to send email to {to}: {str(e)}")
        raise

@app.route('/create-payment-intent', methods=['POST'])
def create_payment_intent():
    try:
        data = request.json
        amount = data.get('amount')  # Amount in cents
        currency = data.get('currency', 'gbp')
        
        # Create a PaymentIntent with the order amount and currency
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            automatic_payment_methods={'enabled': True},
            metadata={
                'service': 'Heathrow Black Cabs',
                'business_email': BUSINESS_EMAIL
            }
        )
        
        print(f"Payment intent created: {intent.id} for £{amount/100}")
        
        return jsonify({
            'clientSecret': intent.client_secret
        })
    except Exception as e:
        print(f"Payment intent error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/book', methods=['POST'])
def book():
    try:
        b = request.json
        print(f"Received booking request: {b}")

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
              {'<tr><td style="padding:10px 0;border-bottom:1px solid #222;color:#888;font-size:13px">Special Requests</td><td style="padding:10px 0;border-bottom:1px solid #222;color:#fff;font-size:13px;text-align:right">' + b.get('specialRequests','') + '</td></tr>' if b.get('specialRequests') else ''}
              {'<tr><td style="padding:10px 0;border-bottom:1px solid #222;color:#888;font-size:13px">Notes</td><td style="padding:10px 0;border-bottom:1px solid #222;color:#fff;font-size:13px;text-align:right">' + b.get('notes','') + '</td></tr>' if b.get('notes') else ''}
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
            {'<tr><td style="padding:8px 0;color:#888;font-size:13px">Special Requests</td><td style="padding:8px 0;color:#fff;font-size:13px">' + b.get('specialRequests','') + '</td></tr>' if b.get('specialRequests') else ''}
            {'<tr><td style="padding:8px 0;color:#888;font-size:13px">Notes</td><td style="padding:8px 0;color:#fff;font-size:13px">' + b.get('notes','') + '</td></tr>' if b.get('notes') else ''}
            <tr><td style="padding:8px 0;color:#888;font-size:13px">Est. Price</td><td style="padding:8px 0;color:#c9a84c;font-size:20px;font-weight:bold">£{b.get('price')}</td></tr>
          </table>
        </div>
        """

        # Send both emails
        customer_email = b.get('email')
        email_errors = []
        
        if customer_email:
            try:
                send_email(customer_email, 'Booking Confirmation — Heathrow Black Cabs', customer_html)
                print(f"Customer email sent to {customer_email}")
            except Exception as e:
                error_msg = f"Failed to send customer email: {str(e)}"
                print(error_msg)
                email_errors.append(error_msg)
        
        try:
            send_email(BUSINESS_EMAIL, f"NEW BOOKING: {b.get('name')} — {b.get('date')} {b.get('time')}", business_html)
            print(f"Business email sent to {BUSINESS_EMAIL}")
        except Exception as e:
            error_msg = f"Failed to send business email: {str(e)}"
            print(error_msg)
            email_errors.append(error_msg)

        if email_errors:
            return jsonify({
                'status': 'partial', 
                'message': 'Booking received but email delivery failed. Please contact us directly.',
                'errors': email_errors
            }), 200
        
        return jsonify({'status': 'ok', 'message': 'Booking confirmed! Check your email.'})

    except Exception as e:
        print(f"Booking error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005)
