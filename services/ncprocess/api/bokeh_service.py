from bokeh.embed import server_document
import os


def get_dashboard_script(data):
    ui_host = os.environ["UI_HOST"]
    print(
        "####################################",
        ui_host,
        "##############################",
    )
    dashboard = server_document(
        f"https://{ui_host}/pybasket_ui", arguments={"data": data}
    )
    return dashboard