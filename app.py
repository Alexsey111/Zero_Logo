# app.py
from flask import Flask, request, render_template
import logo_gen

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        forma = request.form['forma']
        style = request.form['style']
        description = request.form['description']
        result = logo_gen.generate_logo(forma, style, description)
        if "Ошибка" in result:
            return render_template('index.html', error=result)
        return render_template('index.html', image=result)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)