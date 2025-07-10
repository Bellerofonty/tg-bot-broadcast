from flask import Flask, request, render_template, send_file, Response
from send_messages import send_messages
from io import StringIO

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/send", methods=["POST"])
def send():
    bot_token = request.form["bot_token"].strip()
    message = request.form["message"].strip()
    user_ids_raw = request.form["user_ids"].strip()

    user_ids = [uid.strip() for uid in user_ids_raw.split("\n") if uid.strip().isdigit()]

    summary, csv_data = send_messages(bot_token, user_ids, message)

    if csv_data:
        return Response(
            csv_data,
            mimetype="text/csv",
            headers={
                "Content-Disposition": "attachment; filename=failed_messages.csv",
                "X-Summary": summary
            }
        )
    else:
        return f"<p>{summary}</p><p>No failed messages</p><a href='/'>Back</a>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False)
