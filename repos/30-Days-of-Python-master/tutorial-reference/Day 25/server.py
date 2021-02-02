# gunicorn
# fastapi or flask or aiohttp or sarlette
# Django

# Model -> View -> Template -> Response


def render_template(template_name='index.html', context={}):
    html_str = ""
    with open(template_name, 'r') as f:
        html_str = f.read()
        html_str = html_str.format(**context)
    return html_str

def home(environ):
    return render_template(
        template_name='index.html', 
        context={}
    )

def contact_us(environ):
    return render_template(
        template_name='contact.html', 
        context={}
    )

def app(environ, start_response):
    path = environ.get("PATH_INFO")
    if path.endswith("/"):
        path = path[:-1]
    if path == "": # index / root of the web app
        data = home(environ)
    elif path == "/contact":
        data = contact_us(environ)
    else:
        data = render_template(template_name='404.html', context={"path": path})
    data = data.encode("utf-8")
    start_response(
        f"200 OK", [
            ("Content-Type", "text/html"),
            ("Content-Length", str(len(data)))
        ]
    )
    return iter([data])