import re
import numpy as np
import pandas as pd
import datetime
import os
import base64
import pickle

from bokeh.models.widgets import HTMLTemplateFormatter, StringFormatter, DateFormatter
from bokeh.models.widgets import DataTable, TableColumn, RadioButtonGroup, TextInput, TextAreaInput, Dropdown,\
    RangeSlider, CheckboxGroup, Div, FileInput
from bokeh.models import ColumnDataSource, Panel, Tabs
from bokeh.io import curdoc
from bokeh.layouts import gridplot, column

#manage the directories and paths
PROJECT_DIR = './web_scraping'
DB_SAVING_DIR = os.path.join(PROJECT_DIR, 'job_db')
UNION_DB_PATH = os.path.join(DB_SAVING_DIR, 'union_database.xlsx')
SKILL_WORD_COUNTER_DIR = os.path.join(PROJECT_DIR, 'skill_word_counter')
WORD_COUNTER_PATH = os.path.join(SKILL_WORD_COUNTER_DIR, 'skill_word_counter.pkl')
JOB_OFFER_SPR_MATRIX_PATH = os.path.join(SKILL_WORD_COUNTER_DIR, 'X_sim.pkl')

#import df_union
df_union = pd.read_excel(UNION_DB_PATH)

#A few "metrics" and  labels for later
site_source = ['Apec', 'Indeed']
origin_source = ['All sites'] + site_source
total_job_numbers = [len(df_union)] + [len(df_union[df_union['origin'] == origin.lower()]) for origin in site_source]
min_salary = [(np.min(df_union['avg_sal'])//5-1)*5] + \
             [(np.min(df_union.loc[df_union['origin'] == origin.lower(), 'avg_sal'])//5-1)*5 for origin in site_source]

max_salary = [(np.max(df_union['avg_sal'])//5+1)*5] + \
             [(np.max(df_union.loc[df_union['origin'] == origin.lower(), 'avg_sal'])//5+1)*5 for origin in site_source]

location_choice = ["France", "Auvergne-Rhône-Alpes", "Rhône", "Lyon"]
location_scale_col = [None, 'regionName', 'departmentName', 'city'] #usefull later for RadioGroupbutton

job_cat_labels = ["Data scientist",
                  "Data analyst & BI",
                  "Big Data (engineer, dev, archi)",
                  "IT Project Manager (data related)",
                  "Data Manager/Officer",
                  "Unclassified"]

#column to keep to display in Bokeh App
ord_kept_columnns = ['index_0', 'pub_date', 'job_title', 'company', 'location', 'pos_type',
                     'nb_pos', 'req_exp', 'salary', 'act_area', 'url', 'sim']

#names of the kept columns to display in Bokeh App (datatable)
ord_names = ['#', 'Date', 'Title', 'Company', 'Location', 'Type',
             'Nb', 'Experience', 'Salary', 'Activity area', 'URL', 'Similarity']

#respective length of each column in Bokeh datatable (in px)
ord_kept_columnns_len = [30, 60, 120, 100, 110, 30,
                         20, 80, 80, 125, 35, 55]


#Define all column format for the Bokeh datatable
date_formatter = DateFormatter(format='%d/%m/%Y')
##URL format to display origin (e.g. apec, indeed) instead of URL link
url_formatter = HTMLTemplateFormatter(template='<a href="<%= url %>"><%= origin %></a>')
##Add a "hover" tool for datatable to display long text using a HTMLTemplateFormatter
template_long_text = """<span href="#" data-toggle="tooltip" title="<%= value %>"><%= value %></span>"""
text_tooltip = HTMLTemplateFormatter(template=template_long_text)
##One more HTLMTemplateFormatter with underscore js to customise font color of Dice similarity according to its value
template_sim = """
            <div style="color: <%= 
                    (function colorfromint(){
                        if(sim>0.4){return('green')}
                        else if (sim>0.2){return('orange')}
                        else if (sim>=0) {return('red')}
                        else {return('black')}
                        }()) %>;"> 
                <%= value %>
                </font>
            </div>
            """
template_sim_formatter = HTMLTemplateFormatter(template=template_sim)

index_formatter = StringFormatter(font_style='italic', text_align='right', text_color=(142, 142, 161))

formatters = [index_formatter] + [date_formatter] + [text_tooltip]*(len(ord_names)-4) + \
             [url_formatter] + [template_sim_formatter]



#TableColumn object necessary to build the Bokeh datatable
Columns = [TableColumn(field=Ci, title=Ti, width=Wi, formatter=Fi) for Ci, Ti, Wi, Fi in zip(
    ord_kept_columnns, ord_names, ord_kept_columnns_len, formatters)]


#custom template for a Div object that will be included in the Bokeh App to display the current number of job offers
template_div = ("""
      <div class='content'>
       <div class='name'> {site_name} </div>
        <span class='number'>{number}<small>/{total}</small> </span>
      </div>
      """)


#initiate all the dict that will contain widget objects.
# One panel per job board origin and one independent database for each panel!
cv_input = {}
location_select = {}
div_job_number = {}
select_1 = {}
select_2 = {}
select_3 = {}

df_source = {}
data_table_panel = {}
source = {}
table_row_1 = {}
table_row_2 = {}
table_row_3 = {}
table_row_4 = {}
table_bloc = {}
grid = {}
tab = {}

#age max for job offer age
age_max = "100000"

#build all widget objects and aggregate them in a grid plot for each panel (according to job board origin).
for idx, origin in enumerate(origin_source):
    cv_input[origin] = FileInput(accept='.txt')
    location_select[origin] = RadioButtonGroup(labels=location_choice, active=0,
                                               css_classes=['custom_group_button_bokeh'])
    text = template_div.format(site_name=origin,
                               number=total_job_numbers[idx],
                               total=total_job_numbers[idx])
    div_job_number[origin] = Div(text=text, height=50)
    select_1[origin] = Dropdown(value=age_max, label='Publication date', css_classes=['custom_button_bokeh'],
                                menu=[("All", age_max),
                                      ("Less than 1 day", "1"),
                                      ("Less than 3 days", "3"),
                                      ("Less than 7 days", "7"),
                                      ("Less than 14 days", "14"),
                                      ("Less than 30 days", "30")
                                      ]
                                )
    # WARNING for Dropdown button, use value param. to set default value (and not default_value param. !!!)

    select_2[origin] = CheckboxGroup(labels=job_cat_labels, active=list(range(len(job_cat_labels))))

    select_3[origin] = RangeSlider(title="Salary(k€)", start=min_salary[idx], end=max_salary[idx], step=5,
                                   value=(min_salary[idx], max_salary[idx]))

    if origin == 'All sites':
        df_source[origin] = df_union
    else:
        df_source[origin] = df_union[df_union['origin'] == origin.lower()]
    source[origin] = ColumnDataSource(df_source[origin])
    data_table_panel[origin] = DataTable(columns=Columns, source=source[origin],
                                         reorderable=True, fit_columns=True, index_position=None,
                                         width=1000, height=260, row_height=23,
                                         css_classes=["my-table"])
    table_row_1[origin] = TextInput(value='', title="Job title")
    table_row_2[origin] = TextInput(value='', title="Company")
    table_row_3[origin] = TextInput(value='', title="Location")
    table_row_4[origin] = TextInput(value='', title="Recruitment responsible")
    table_bloc[origin] = TextAreaInput(value='', title="Job description", cols=1000, max_length=5000, rows=11)
    grid[origin] = gridplot([[cv_input[origin], location_select[origin]],
                             [column(select_1[origin],
                                     select_2[origin],
                                     select_3[origin],
                                     div_job_number[origin]),
                              data_table_panel[origin]],
                             [column(table_row_1[origin],
                                     table_row_2[origin],
                                     table_row_3[origin],
                                     table_row_4[origin]),
                              table_bloc[origin]]])

    tab[origin] = Panel(child=grid[origin], title=origin)

tabs = Tabs(tabs=[tab[origin] for origin in origin_source])


def function_source(attr, old, new):
    """Display information in appropriate table_row/bloc Widgets on row selection in the datatable"""
    active_panel = origin_source[tabs.active]
    try:
        selected_index = source[active_panel].selected.indices[0]
        table_row_1[active_panel].value = str(source[active_panel].data["job_title"][selected_index])
        table_row_2[active_panel].value = str(source[active_panel].data["company"][selected_index])
        table_row_3[active_panel].value = str(source[active_panel].data["location"][selected_index])
        table_row_4[active_panel].value = str(source[active_panel].data["recruit_resp"][selected_index])
        table_bloc[active_panel].value = str(source[active_panel].data["pos_descr"][selected_index])
    except IndexError:
        pass


def make_dataset(offer_age, min_sal, max_sal, job_cat, loc):
    """Make a subset of the full dataset according to filters defined by user via Bokeh widgets"""
    data = df_source[origin_source[tabs.active]]
    today = pd.Timestamp.today().floor("D")
    min_date = today - datetime.timedelta(days=int(offer_age))
    date_mask = data['pub_date'].between(min_date, today)
    salary_mask = ((data['avg_sal'] >= min_sal) & (data['avg_sal'] <= max_sal)) | (data['avg_sal'].isnull())
    cat_mask = (data[job_cat] == 1).any(axis=1)
    if loc == 0:
        loc_mask = [True] * len(data)
    elif loc < 3:
        loc_mask = data[location_scale_col[loc]] == location_choice[loc]
    else:
        loc_mask = data[location_scale_col[loc]].map(lambda x: bool(re.match(location_choice[loc],
                                                                             str(x), flags=re.IGNORECASE)))
    sub_df = data[date_mask & salary_mask & cat_mask & loc_mask]
    return sub_df


def update_dpdown_label():
    """Updata dropdown button label according to user selection"""
    active_panel = origin_source[tabs.active]
    offer_age = select_1[active_panel].value
    if offer_age == age_max:
        new_label = "Publication date : All"
    else:
        new_label = "Publication date : Less than {} day(s)".format(offer_age)
    select_1[active_panel].label = new_label


def update_div_job_numbers():
    """Update job number display in the Div object according to current activated filters"""
    new_site_name = origin_source[tabs.active]
    new_number = len(source[origin_source[tabs.active]].data['index'])
    total = total_job_numbers[tabs.active]
    new_text = template_div.format(site_name=new_site_name,
                           number=new_number,
                           total=total)
    div_job_number[origin_source[tabs.active]].update(text=new_text)


def change_data_source():
    """Update the source datatable via the make_dataset function and filters provided by user via widgets"""
    active_panel = origin_source[tabs.active]
    offer_age = select_1[active_panel].value
    min_sal = select_3[active_panel].value[0]
    max_sal = select_3[active_panel].value[1]
    job_cat = [select_2[active_panel].labels[i] for i in select_2[active_panel].active]
    loc = location_select[active_panel].active
    new_src = make_dataset(offer_age=offer_age, min_sal=min_sal, max_sal=max_sal, job_cat=job_cat, loc=loc)
    source[active_panel].data.update(ColumnDataSource(new_src).data) #if passing directly the the new src in update, issue with index


def compute_similarity(cv, word_counter_path=WORD_COUNTER_PATH, offer_spr_matrix_path=JOB_OFFER_SPR_MATRIX_PATH):
    """ Transforms a resume into a word counting sparse matrix by a word counter (restricted vocabulary) and compute
    Dice index metric with word counting sparse matrix for job offers."""
    with open(word_counter_path, 'rb') as input:
        word_counter = pickle.load(input)
    with open(offer_spr_matrix_path, 'rb') as input:
        X_sim = pickle.load(input)
    Y = word_counter.transform([cv]) #word_counter iterates over raw text document, not raw text
    Z = X_sim.multiply(Y) #element-wise multiplication for sparse matrix
    sim_mat = 2 * Z.sum(axis=1)/(X_sim.sum(axis=1)+Y.sum())
    sim_arr = np.around(np.squeeze(np.asarray(sim_mat)), decimals=2) #convert matrix object into array
    D_sim = pd.Series(sim_arr, index=df_union.index)
    return D_sim


def update_similarity(attr, old, new):
    """Compute similarity between job offers and a resume provided by the user via the InputFile widget"""
    active_panel = origin_source[tabs.active]
    cv_64_enc_str = cv_input[active_panel].value
    # Encoding the Base64 encoded string into bytes
    cv_64_enc_b = cv_64_enc_str.encode('utf-8')
    # Decoding the Base64 bytes
    cv_enc_b = base64.b64decode(cv_64_enc_b)
    # Decoding the bytes to string
    cv_str = cv_enc_b.decode('utf-8')
    D_sim = compute_similarity(cv=cv_str)
    if active_panel != 'All sites':
        mask_origin = df_source['All sites']['origin'] == active_panel.lower()
        D_sim = D_sim[mask_origin]
    df_source[active_panel]['sim'] = D_sim
    change_data_source()

#triggers the functions according to widget modifications by user
for origin in origin_source:
    cv_input[origin].on_change("value", update_similarity)
    select_1[origin].on_change("value", lambda attr, old, new: change_data_source())
    select_1[origin].on_change("value", lambda attr, old, new: update_dpdown_label())
    select_3[origin].on_change("value", lambda attr, old, new: change_data_source())
    select_2[origin].on_change("active", lambda attr, old, new: change_data_source())
    location_select[origin].on_change("active", lambda attr, old, new: change_data_source())
    source[origin].selected.on_change('indices', function_source)
    source[origin].on_change('data', lambda attr, old, new: update_div_job_numbers())

curdoc().add_root(tabs)
