import panel as pn

pn_widget = pn.pane.HTML('Name', width=75)

app = pn.Row(pn_widget, sizing_mode='stretch_both').servable()


