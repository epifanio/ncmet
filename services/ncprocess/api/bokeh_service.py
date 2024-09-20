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