from core.di import app, jinja


@app.route("/")
@jinja.template('index.html')
async def main(request):
    return {
        'main': 'hello'
    }
