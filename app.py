from flask import Flask, render_template, request, send_file
from crawler import generate_excel

app = Flask(__name__)

@app.route("/")
def home():

    tahun_list = list(range(2020,2031))

    return render_template(
        "index.html",
        tahun_list=tahun_list
    )


@app.route("/download", methods=["POST"])
def download():

    tahun = request.form["tahun"]

    file = generate_excel(tahun)

    return send_file(file, as_attachment=True)


if __name__ == "__main__":
    app.run()