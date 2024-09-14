from liku import HTMLElement
from liku.htm import html

from starlette.datastructures import FormData
from likulau.form import Form


def on_submit(form: FormData):
    name = form.get("name", "Ren")
    return html("""
    <div>
        <p>Hello, {{name}}!</p>
        {{html_form}}
    </div>
    """)


def page() -> HTMLElement:
    return html_form  # type: ignore


html_form = html("""
    <Form :action="on_submit" method="POST">
        <label for="name">Your name:</label>
        <input type="text" id="name" name="name" value="" autocomplete="off" />
        <input type="submit" value="Submit" />
    </Form>
""")
