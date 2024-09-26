# This file is part of ncmet.
#
# https://github.com/metno/ncmet
#
# ncmet is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ncmet is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ncmet.  If not, see <http://www.gnu.org/licenses/>.

import time
import traceback
import functools
import hvplot.xarray
import xarray as xr
import panel as pn
import numpy as np
import holoviews as hv
from utility import ModelURL, pandas_frequency_offsets, get_download_link, dict_to_html_ul
from pydantic import ValidationError
from starlette.templating import Jinja2Templates
import json
import sys
from bokeh.models import Button, Div
from bokeh.layouts import column, Spacer

from jinja2 import Environment, FileSystemLoader
import gc

env = Environment(loader=FileSystemLoader('/hvplot/static'))

pn.param.ParamMethod.loading_indicator = True

# try:
#     # phase = int(pn.state.session_args.get('phase')[0])
#     nc_url = str(pn.state.session_args.get('nc_url')[0].decode("utf8"))
# except Exception:
#     # phase = 1
#     nc_url = 'https://thredds.met.no/thredds/dodsC/alertness/YOPP_supersite/obs/utqiagvik/utqiagvik_obs_timeSeriesProfile_20180701_20180930.nc'


def on_server_loaded():
    print("server loaded")
    print("")
    sys.stdout.flush()
    
def on_session_created(session_context):
    print("session created")
    print("")
    sys.stdout.flush()

def on_session_destroyed(session_context):
    print("session destroyed")
    print("")
    print(dir(session_context))
    try:
        del ds
        gc.collect()
    except UnboundLocalError:
        pass
    sys.stdout.flush()
    
    
pn.state.onload(callback=on_server_loaded)
# pn.state.on_session_created(callback=on_session_created)
pn.state.on_session_destroyed(callback=on_session_destroyed)


nc_url = None
valid_url = False

try:
    nc_url = str(pn.state.session_args.get('url')[0].decode("utf8"))
    try:
        ModelURL(url=nc_url)
        valid_url = True
    except ValidationError as e:
        print(e)
        valid_url = False
except TypeError:
    nc_url = None
    valid_url = False

error_log = Div(text=f"""<br><br> Can't load dataset from {nc_url} """)
templates = Jinja2Templates(directory="/hvplot/templates")

def show_hide_error(event):
    """docstring"""
    if error_log.visible:
        error_log.visible = False
    else:
        error_log.visible = True


print("++++++++++++++++++++++++ LOADING ++++++++++++++++++++++++++++++++++++")
print(str(nc_url))
print("++++++++++++++++++++++++ +++++++ ++++++++++++++++++++++++++++++++++++")



# TODO: add a logger and tell the user that the file is being loaded
#       and if the decoding of the time variable fails
#       keep track of the nc_url and the error message

try:
    ds = xr.open_dataset(str(nc_url).strip())
    #ds = ds_raw.where(ds_raw != 9.96921e36)  
    decoded_time=True
except ValueError as e:
    print(e)
    ds = xr.open_dataset(str(nc_url).strip(), decode_times=False)
    #ds = ds_raw.where(ds_raw != 9.96921e36) 
    decoded_time=False
except OSError as e:
    raw_data = Div(text=f"""<b>ValueError</b><br><br> Can't load dataset from {nc_url} """)
    newhtml = templates.get_template("error.html").render(
        {"error_traceback": traceback.format_exc()}
    )
    error_log.text = newhtml
    error_log.visible = False
    error_log_button = Button(
        label="",
        height=50,
        width=50,
    )  # , width_policy='fixed'
    error_log_button.on_click(show_hide_error)

    print(newhtml)
    bokeh_pane = pn.pane.Bokeh(
        column(raw_data, error_log_button, error_log),
    ).servable()


# Build a list of coordinates, give precedence to time coordinates
# if no time coordinates are found use the available coordinates

# the code below could go into a method, if time is detected as a coordinate
# then the frequency selector should be added to the sidebar
# if time is not detected as a coordinate then the frequency selector should not be added to the sidebar


if ds.attrs['featureType'] == 'timeSeries':
    var_coord = [i for i in ds.coords if ds.coords.dtypes[i] == np.dtype('<M8[ns]')]
    time_coord = True
else:
    time_coord = False
    var_coord = list(ds.coords)
# if time is detected as a coordinate then the frequency selector should be added to the sidebar
# but I also need to check if the time coordinate is a dimension for the selectred variable
# and if the time values are sorted with monotonically increasing or decreasing values

# check for monotobically increasing or decreasing time values:
#
# coords_values = ds.coords['time'].values[::-1]
# is_monotonic = all(coords_values[i] <= coords_values[i + 1] for i in range(len(coords_values) - 1)) or all(coords_values[i] >= coords_values[i + 1] for i in range(len(coords_values) - 1))
# print("is_monotonic: ", is_monotonic)
# check if a selected variable has time as a index
# is_time_indexed = 'time' in ds['variable'].indexes
# print("variable {} is indexed by time: ", is_time_indexed)

# if len(var_coord) != 0:
# if time_coord:
#     frequency_selector = pn.widgets.Select(options=[
#         "--",
#         "Hourly",
#         "Calendar day",
#         "Weekly",
#         "Month end",
#         "Quarter end",
#         "Yearly",
#     ], name='Resampling Frequency')
# else:
#     frequency_selector = None


frequency_selector = pn.widgets.Select(options=[
        "--",
        "Hourly",
        "Calendar day",
        "Weekly",
        "Month end",
        "Quarter end",
        "Yearly",
    ], name='Resampling Frequency')

#if len(var_coord) == 0:
#    var_coord = list(ds.coords) # [i for i in ds.coords]

# variable that have dims and coords matching
# plottable_vars = [i for i in ds if list(ds[i].dims) == list(ds.coords)] # [j for j in ds.coords]]
# the followinf doesn't work for timesereis where we have lat.lon and time as coordinates (3,) 
# but those are not in the variables where we found only time (1,)
# need to either remove lon,lat from the available coords list or find a different approach
#
# plottable_vars = [i for i in ds if (list(ds[i].dims) == list(ds.coords) or list(ds[i].dims) == list(ds.coords)[::-1])] 
plottable_vars = [j for j in ds if len([value for value in list(ds[j].coords) if value in list(ds.dims)]) >= 1]

# build a dictionary of variables and their long names
print("plottable_vars:", plottable_vars )
mapping_var_names = {}
for i in plottable_vars:
    if int(len(list(ds[i].coords)) != 0):
        try:
            title = f"{ds[i].attrs['long_name']} [{i}]"
        except KeyError:
            title = f"{i}"
        mapping_var_names[i] = title
          
# add a select widget for variables, uses long names
variables_selector = pn.widgets.Select(options=list(mapping_var_names.values()), name='Data Variable')


def plot(var, title=None):
    try:
        del ds
        gc.collect()
    except UnboundLocalError:
        pass
    if decoded_time:
        ds = xr.open_dataset(str(nc_url).strip())
    else:
        ds = xr.open_dataset(str(nc_url).strip(), decode_times=False)
    var = var[0]
    print(f'plotting var: {var}')
    if not title:
        try:
            title = f"{ds[var].attrs['long_name']}"
        except KeyError:
            title = f"{var}"
    else:
        title=title
    if 'featureType' in ds.attrs:
        featureType = ds.attrs['featureType']
    else:
        featureType = None
    is_monotonic = False
    if featureType == 'timeSeries':
        var_coord = [i for i in ds.coords if ds.coords.dtypes[i] == np.dtype('<M8[ns]')]
        coords_values = ds.coords[var_coord[0]].values[::-1]
        is_monotonic = all(coords_values[i] <= coords_values[i + 1] for i in range(len(coords_values) - 1)) or all(coords_values[i] >= coords_values[i + 1] for i in range(len(coords_values) - 1))
        if is_monotonic:
            frequency_selector.visible = True
        else:
            frequency_selector.visible = False
        # removing 'y': ds[var], from the axis_arguments dictionary
        # to bypass the error described in the following github issue
        # https://github.com/holoviz/hvplot/issues/1325
        axis_arguments = {'grid':True, 'title': title, 'widget_location': 'bottom', 'responsive': True}
        if is_monotonic and frequency_selector.value != "--":
            print('data resampling requested')
            resampling_freq = {var_coord[0]: pandas_frequency_offsets[frequency_selector.value]}
            # .where(ds_raw != 9.96921e36)
            plot_widget = ds[var].where(ds[var] != 9.96921e36).resample(**resampling_freq).mean().hvplot.line(**axis_arguments)
        else:
            # .where(ds_raw != 9.96921e36)
            plot_widget =  ds[var].where(ds[var] != 9.96921e36).hvplot.line(**axis_arguments)
        return plot_widget
    if featureType and featureType != "timeSeries":
        frequency_selector.visible = False
        axis_arguments = {'x': ds[var], 'grid':True, 'title': title, 'widget_location': 'bottom', 'responsive': True}
    try:
        plot_widget =  ds[var].where(ds[var] != 9.96921e36).hvplot.line(**axis_arguments)
    except TypeError:
        axis_arguments = {'grid':True, 'title': title, 'widget_location': 'bottom', 'responsive': True}
        plot_widget =  ds[var].where(ds[var] != 9.96921e36).hvplot.line(**axis_arguments)
    except ValueError:
        axis_arguments = {'x': var, 'grid':True, 'title': title, 'widget_location': 'bottom', 'responsive': True}
        plot_widget =  ds[var].where(ds[var] != 9.96921e36).hvplot.line(**axis_arguments)
    return plot_widget
        
        

# main plotting function
def plot_(var, title=None, plot_type='line'):
    if 'featureType' in ds.attrs:
        if ds.attrs['featureType'] == 'timeSeries':
            print("timeSeries")
            var_coord = [i for i in ds.coords if ds.coords.dtypes[i] == np.dtype('<M8[ns]')]
            frequency_selector.visible = True
            feature_type = ds.attrs['featureType']
        if ds.attrs['featureType'] == 'timeSeriesProfile':
            print("timeSeriesProfile")
            var_coord = [i for i in ds.coords if ds.coords.dtypes[i] != np.dtype('<M8[ns]')]
            # frequency_selector.visible = False
            feature_type = ds.attrs['featureType']
        if ds.attrs['featureType'] == 'profile':
            print("profile")
            var_coord = [i for i in ds.coords]
            feature_type = ds.attrs['featureType']
            # frequency_selector.visible = False
    else:
        feature_type = None
    #var_coord = [i for i in ds.coords if ds.coords.dtypes[i] == np.dtype('<M8[ns]')]
    #if var_coord[0] in ds[var].indexes:
    #    frequency_selector.visible = True
    #    #export_resampling_option.visible = False
    #else:
    #    frequency_selector.visible = False
        #export_resampling_option.visible = False
    #    print(f"The selected variable {var} is not indexed by time. The frequency selector will not be visible.")
    #if len(var_coord) == 0:
    #    # var_coord = [i for i in ds.coords]
    #    var_coord = [i for i in ds.coords if ds.coords.dtypes[i] != np.dtype('<M8[ns]')]
    if not title:
        try:
            title = f"{ds[var].attrs['long_name']}"
        except KeyError:
            title = f"{var}"
    else:
        title=title
        
    if feature_type and feature_type == "timeSeriesProfile":
        axis_arguments = {'y': list(ds[var].coords)[0], 'grid':True, 'title': title, 'widget_location': 'bottom', 'responsive': True}
    else:
        axis_arguments = {'y': ds[var], 'grid':True, 'title': title, 'widget_location': 'bottom', 'responsive': True}
    print('axis_arguments: ', axis_arguments)
    print('selected variable: ', var)
                
    if var_coord[0] in ds[var].coords:
        if frequency_selector is not None and frequency_selector.value != "--":
            print(f"user request to plot resampled dataset - using time dimension: {var_coord[0]}")
            print(f"available dimensions are: {var_coord}")
            arguments = {var_coord[0]: pandas_frequency_offsets[frequency_selector.value]}
            if plot_type == 'line':
                plot_widget =  ds[var].resample(**arguments).mean().hvplot.line(**axis_arguments)
            else:
                plot_widget =  ds[var].resample(**arguments).mean().hvplot.scatter(**axis_arguments)   
        else:
            if plot_type == 'line':
                plot_widget =  ds[var].hvplot.line(**axis_arguments)
            else:
                plot_widget =  ds[var].hvplot.scatter(**axis_arguments)
        # scatter_plot_widget = ds[var].hvplot.scatter(x=var_coord[0], grid=True, title=title, widget_location='bottom', responsive=True)
        #plot_widget = hv.Overlay(line_plot_widget, scatter_plot_widget)
        return plot_widget
    else:
        if plot_type == 'line':
            plot_widget =  ds[var].hvplot.line(**axis_arguments)
        else:
            plot_widget =  ds[var].hvplot.scatter(**axis_arguments)
        # scatter_plot_widget = ds[var].hvplot.scatter(x=list(ds[var].coords)[0], grid=True, title=title, widget_location='bottom', responsive=True)
        #plot_widget = hv.Overlay(line_plot_widget, scatter_plot_widget)
        return plot_widget

# method to update the plot when a new variable is selected    
def on_var_select(event):
    var = event.obj.value
    result = [key for key, value in mapping_var_names.items() if value == var]
    with pn.param.set_values(main_app, loading=True):
        plot_widget[-1] = plot(var=result, title=var)
        print(f'selected {result}')

def on_frequency_select(event):
    frequency = event.obj.value
    var = variables_selector.value
    result = [key for key, value in mapping_var_names.items() if value == var]
    with pn.param.set_values(main_app, loading=True):
        plot_widget[-1] = plot(var=result, title=var)
        print(f'selected {result} \n with frequency {frequency}') 
    
if frequency_selector is not None:
    frequency_selector.param.watch(on_frequency_select, parameter_names=['value'])
 
def show_hide_export_widget(event):
    print(downloader.visible)
    result = [key for key, value in mapping_var_names.items() if value == variables_selector.value]
    if [i for i in ds.coords if ds.coords.dtypes[i] == np.dtype('<M8[ns]')][0] not in ds[result].indexes:
        print("this shoiuld remove the resampling data selector for raw / resampled")
        export_resampling.visible = False
    if downloader.visible:
        downloader.visible = False
    else:
        metadata_layout.visible = False
        downloader.visible = True 

        
def show_hide_metadata_widget(event):
    """docstring"""
    if metadata_layout.visible:
        metadata_layout.visible = False
    else:
        metadata_layout.visible = True
        downloader.visible = False
        
def export_selection(event):
    """docstring"""
    # print(box.values)
    # start = ds.index.searchsorted(date_time_range_slider.value[0])
    # end = ds.index.searchsorted(date_time_range_slider.value[1])
    # event_log.text = f"{str(wbx.value)} <br> {str(date_time_range_slider.value)}"
    select_output_format_mapping = {'NetCDF':'nc', 'CSV':'csv', 'Parquet':'pq'}
    with pn.param.set_values(main_app, loading=True):
        export_format = select_output_format_mapping[select_output_format.value]
        # export_format = select_output_format.value.lower()
        if export_resampling.value == 'Raw':
            resampler = False
            resampler_frequency = 'raw '
            #print(export_resampling)
            #print(export_resampling.value)
        else:
            if frequency_selector is not None and frequency_selector.value != "--":
                resampler = True
                resampler_frequency = frequency_selector.value
                #print(export_resampling)
                #print(export_resampling.value)
            else:
                resampler = False
                resampler_frequency = 'raw'
        if not frequency_selector:
            time_range = []
        else:
            time_range = date_time_range_slider.value
            selected_variables = [i.name for i in wbx if i.value == True]
        # event_log.text = f"{str(selected_variables)} <br> {time_range} <br> {export_format} <br> {resampler}"
        

        data = {
            "url": "https://thredds.met.no/thredds/dodsC/alertness/YOPP_supersite/obs/utqiagvik/utqiagvik_obs_timeSeriesProfileSonde_20180201_20180331.nc",
            "variables": [
                "ta",
                "hur",
                "wdir_refmt"
                ],
            "decoded_time": decoded_time,
            "time_range": [
                "2018-07-01T00:00:00.000000000",
                "2018-09-30T23:59:00.000000000"
                ],
            "is_resampled": resampler,
            "resampling_frequency": "raw",
            "output_format": "nc"
            }
        # download_link = get_download_link(data)
        
        # print(download_link)
        
        
        time_range = [str(i) for i in date_time_range_slider.value]
        export_dataspec = {
            "url": str(nc_url),
            "variables": selected_variables,
            "decoded_time": decoded_time,
            "time_range": time_range,
            "is_resampled": resampler,
            "resampling_frequency": resampler_frequency,
            "output_format": export_format,
        }
        json_object = json.dumps(export_dataspec)
        print(json_object)
        download_link = get_download_link(json_object)
        # event_log.text = f"{str(export_dataspec)}"
        event_log.text = str(
            f'<marquee behavior="scroll" direction="left"><b>. . .  processing . . .</b></marquee>'
        )
        pn.state.curdoc.add_next_tick_callback(
            functools.partial(
                compress_selection, download_link=download_link, output_log_widget=event_log))
        
        # print(json.dump(export_dataspec))
        #print(export_dataspec)
        #json_object = json.dumps(export_dataspec, indent = 4)
        #print(json_object)
        # slice the ds by selecting the variables fro the checkbox and slicing along the time dimension from the timerange slider (if available)
    
def compress_selection(download_link, output_log_widget):
    time.sleep(2)
    output_log_widget.text = str(
                f'<a href="{download_link}">Download</a>'
            )
    print(download_link)
    
    
def build_metadata_widget():
    # dataset_metadata_keys = list(ds.attrs.keys())
    # dataset_metadata_values = list(ds.attrs.values())
    # dataset_metadata = dict(
    #     key=dataset_metadata_keys,
    #     value=dataset_metadata_values,
    # )
    # dataset_metadata_source = ColumnDataSource(dataset_metadata)

    # dataset_metadata_columns = [
    #     TableColumn(field="key", title="key"),
    #     TableColumn(field="value", title="value"),
    # ]
    # metadata_table = DataTable(
    #     source=dataset_metadata_source,
    #     columns=dataset_metadata_columns,
    # )
    metadata_text = dict_to_html_ul(ds.attrs)
    # metadata_layout = row(
    #     Spacer(width=30),
    #     column(
    #         Div(text=f'<font size = "2" color = "darkslategray" ><b>Metadata<b></font> {metadata_text}'),
    #         Spacer(height=10),
    #         #metadata_table,
    #         sizing_mode="stretch_both",
    #     ),
    # )
    # metadata_layout = Div(text=f'<font size = "2" color = "darkslategray" ><b>Metadata<b></font> {metadata_text}')
    
    
    
    metadata_layout = pn.Row(Spacer(width=10), pn.Column(Spacer(height=120),
                                                Div(text=f'<font size = "2" color = "darkslategray" ><b>Metadata<b></font> {metadata_text}'), 
                                                width=400, sizing_mode='fixed'))
    
    
    metadata_layout.visible = False

    metadata_button = Button(
        label="Metadata",
        height=30,
        width=120,
    )  # , width_policy='fixed'
    metadata_button.on_click(show_hide_metadata_widget)
    return metadata_layout, metadata_button
    
    
def build_download_widget():
    export_resampling_option = pn.widgets.RadioButtonGroup(name='Resamplig', 
                                              options=['Raw', 'Resampled'])    
    event_log = Div(text=f"""<br><br> some_log <br><br>""")
    try:
        time_dim = var_coord[0]
        date_time_range_slider = pn.widgets.DatetimeRangeSlider(
            name='Date Range',
            start=ds.coords[time_dim].values.min(), end=ds.coords[time_dim].values.max(),
            value=(ds.coords[time_dim].values.min(), ds.coords[time_dim].values.max())        )
    except:
        date_time_range_slider = Div(text=f"""<br><br> Time Dimension not available """)
    
    checkbox_group = pn.FlexBox(*[pn.widgets.Checkbox(name=str(i)) for i in mapping_var_names.keys()])
    select_output_format = pn.widgets.Select(name='Export Format', options=['NetCDF', 'CSV', 'Parquet'])
    
    select_output_format_mapping = {'NetCDF':'nc', 'CSV':'csv', 'Parquet':'pq'}
    
    export_button = Button(
        label="Export",
        height=30,
        width=120,
    )  
    export_button.on_click(show_hide_export_widget)
    
    
    export_options_button = Button(
        label="Download",
        height=30,
        width_policy='fit'
        # width=30,
    )  # , width_policy='fixed'
    export_options_button.on_click(export_selection)
    if not frequency_selector: 
        export_resampling_option.visible = False
    
    return export_button, checkbox_group, date_time_range_slider, export_options_button, event_log, select_output_format, export_resampling_option




# Export Widgets
export_button, wbx, date_time_range_slider, export_options_button, event_log, select_output_format, export_resampling = build_download_widget()
download_header = Div(text='<font size = "2" color = "darkslategray" ><b>Data Export<b></font> <br> Variable Selection')
# download_header.visible = False


# Metadata Widgets
metadata_layout, metadata_button = build_metadata_widget()


# downloader = pn.Column(download_header, wbx, date_time_range_slider, select_output_format, export_resampling, export_options_button, event_log, width=400, sizing_mode='fixed')



downloader = pn.Row(Spacer(width=10), pn.Column(Spacer(height=120),
                                                download_header, 
                                                wbx, 
                                                date_time_range_slider, 
                                                select_output_format, 
                                                export_resampling, 
                                                export_options_button, 
                                                event_log, width=400, sizing_mode='fixed'))

downloader.visible = False

variables_selector.param.watch(on_var_select, parameter_names=['value'])

selected_var = [key for key, value in mapping_var_names.items() if value == variables_selector.value]


buttons = pn.Column(export_button, metadata_button)
plot_plot = plot(selected_var, title=variables_selector.value)
plot_widget = pn.Column(pn.Row(variables_selector, frequency_selector, buttons), plot_plot, sizing_mode='scale_both') # , sizing_mode='scale_both'

# main_app = pn.Row(plot_widget, Spacer(width=10), downloader, metadata_layout).servable()


jinja_template = env.get_template('template.html')
tmpl = pn.Template(jinja_template)

# tmpl.add_variable('app_title', '<center><h1>NCMET</h1></center>')

main_app = pn.Row(plot_widget, Spacer(width=10), downloader, metadata_layout)

tmpl.add_panel('A',  main_app)
tmpl.servable()
