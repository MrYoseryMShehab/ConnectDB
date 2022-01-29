import os
import mysql.connector as sql
from mysql.connector import Error
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import plotly.express as px
import requests

# Current working directory
os.chdir('G:\Panorama\Data_Visualization_with_Python_Coursera\dash_dolibarr')
# Create a dash application
app = dash.Dash(__name__)

# REVIEW1: Clear the layout and do not display exception till callback gets executed
app.config.suppress_callback_exceptions = True

try:
    #    connection = sql.connect(host='10.10.12.116',
    connection = sql.connect(host='localhost',
                                         database='dolibarr3',
                                         user='root',
                                         password='')
    if connection.is_connected():

        '''db_Info = connection.get_server_info()
        print("Connected to MySQL Server version ", db_Info)
        cursor = connection.cursor()
        cursor.execute("select database();")
        record = cursor.fetchone()
        print("You're connected to database: ", record)
        '''
        mycursor = connection.cursor()

        #factureالربط مع فاتورة البيع
        db_connection_sql_facture = """SELECT s.name_alias name_consumer, MONTH(f.datec) MONTH,YEAR(f.datec) YEAR,
                                              DAY(f.datec) DAY,QUARTER(f.datec) QUARTER,f.multicurrency_total_ttc
                                        FROM llx_facture as f
                                        INNER JOIN llx_societe AS s ON f.fk_soc = s.rowid"""

        db_connection_sql_facturedet = """SELECT p.label name_product, fd.qty, fd.total_ht, MONTH(f.datec) MONTH,YEAR(f.datec) YEAR,
                                                DAY(f.datec) DAY,QUARTER(f.datec) QUARTER
                                            FROM llx_facturedet as fd
                                            INNER JOIN llx_product AS p ON p.rowid = fd.fk_product
                                            INNER JOIN llx_facture AS f ON f.rowid = fd.fk_facture"""


        #llx_facture_fourn مع فاتورة الشراء
        db_connection_sql_fourn = """SELECT s.name_alias name_supplier, MONTH(f.datec) MONTH,YEAR(f.datec) YEAR,
                                     DAY(f.datec) DAY,QUARTER(f.datec) QUARTER,f.multicurrency_total_ttc
                                    FROM llx_facture_fourn as f
                                    INNER JOIN llx_societe AS s ON f.fk_soc = s.rowid"""

        db_connection_sql_fourndet = """SELECT c.label name_country ,p.label name_product, fd.qty, fd.total_ht, MONTH(f.datec) MONTH,YEAR(f.datec) YEAR,
                                                DAY(f.datec) DAY,QUARTER(f.datec) QUARTER
                                    FROM llx_facture_fourn_det as fd
                                    INNER JOIN llx_product AS p ON p.rowid = fd.fk_product
                                    INNER JOIN llx_facture_fourn AS f ON f.rowid = fd.fk_facture_fourn
                                    INNER JOIN llx_c_country AS c ON c.rowid = p.fk_country"""

         # llx_product مع المخزون
        db_connection_sql_product = """SELECT p.label name_product ,p.stock ,p.cost_price,p.stock*p.cost_price total_value,c.label name_country
                                           FROM llx_product as p
                                           INNER JOIN llx_c_country AS c ON c.rowid = p.fk_country
                                                where stock > 0"""

        #get facture data from db راس فاتورة البيع
        mycursor.execute(db_connection_sql_facture)
        myresult = mycursor.fetchall()
        df_all = pd.DataFrame(myresult)
        #rename columnens
        df_all.rename({0: 'name_consumer', 1: 'MONTH', 2: 'YEAR', 3:'DAY', 4:'QUARTER', 5: 'multicurrency_total_ttc'}, axis=1, inplace=True)

        #get facturedet data from db تفاصيل فاتروة البيع
        mycursor.execute(db_connection_sql_facturedet)
        myresult1 = mycursor.fetchall()
        df_all_facturedet = pd.DataFrame(myresult1)
        #rename columnens
        df_all_facturedet.rename({0: 'name_product', 1: 'qty', 2: 'total_ht', 3: 'MONTH', 4:'YEAR', 5:'DAY', 6:'QUARTER'}, axis=1, inplace=True)


        #get fourn data from db راس فارتورة الشراء
        mycursor.execute(db_connection_sql_fourn)
        myresult2 = mycursor.fetchall()
        df_all_fourn = pd.DataFrame(myresult2)
        #rename columnens
        df_all_fourn.rename({0: 'name_supplier', 1: 'MONTH', 2: 'YEAR', 3:'DAY', 4:'QUARTER', 5: 'multicurrency_total_ttc'}, axis=1, inplace=True)

        #get fourndet data from db تفاصيل فاتورة الشراء
        mycursor.execute(db_connection_sql_fourndet)
        myresult3 = mycursor.fetchall()
        df_all_fourndet = pd.DataFrame(myresult3)
        #rename columnens
        df_all_fourndet.rename({0:'name_country', 1: 'name_product', 2: 'qty', 3: 'total_ht', 4: 'MONTH', 5:'YEAR', 6:'DAY', 7:'QUARTER'}, axis=1, inplace=True)


        #get llx_product data from db تفاصيل حركة مخزون
        mycursor.execute(db_connection_sql_product)
        myresult4 = mycursor.fetchall()
        df_all_product = pd.DataFrame(myresult4)
        #rename columnens
        df_all_product.rename({0:'name_product', 1: 'stock', 2: 'cost_price', 3:'total_value', 4:'name_country'}, axis=1, inplace=True)


except Error as e:
    print("Error while connecting to MySQL", e)

finally:
    if connection.is_connected():
        mycursor.close()
        connection.close()
        print("MySQL connection is closed")
year_list = [i for i in range(2021, 2005, -1)]

#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
#app = JupyterDash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
                                html.Div([
                                        html.H2("Tafra Company"),
                                        html.Img(src="/assets/tafra_1.png")
                                            ], className="banner"),

                                 # Add an division
                                html.Div([
                                        # Create an division for adding dropdown helper text for report type
                                    dcc.Dropdown(id='input-type',
                                            options=[
                                                {'label': 'تفاصيل المشتريات', 'value': 'OPT1'},
                                                {'label': 'تفاصيل المبيعات', 'value': 'OPT2'},
                                                {'label': 'حركة صنف', 'value': 'OPT3'}
                                            ],
                                            placeholder='Select a report type',
                                            style={'width': '100%', 'padding': '2px', 'font size': '10px', 'text-align-last': 'center'}),
                                       html.Div(
                                            [
                                            html.H2(' نوع التقرير:', style={'margin-right': '2em','font-size': 11,'text-align': 'right'}),
                                            ]
                                        ),
                                    # Create an division for adding dropdown helper text for choosing year
                                       dcc.Dropdown(id='input-year',
                                                     # Update dropdown values using list comphrehension
                                                     options=[{'label': i, 'value': i} for i in year_list],
                                                     placeholder="Select a year",
                                                     style={'width':'100%', 'padding':'2px', 'font-size': '10px', 'text-align-last' : 'center'}),
                                         html.Div(
                                            [
                                            html.H2(' سنة التقرير:', style={'margin-right': '2em','font-size': 11})
                                            ]
                                        )], style={'display': 'flex'}),

                                html.Div([
                                # make spaces
                                html.Div(children=[html.H5(''), html.H5(id='label11')],
                                             style={'width': '19%', 'display': 'inline-block', 'border': 'none', 'text-align': 'center', 'font-family': 'Century Gothic'}),
                                #'border': '1px solid black' , 'text-align': 'right'
                                html.Div(children=[html.H5(''), html.H5(id='label')],
                                             style={'width': '30%', 'display': 'inline-block', 'border': 'none', 'text-align': 'center', 'font-family': 'Century Gothic'}),
                                html.Div(children=[html.H5(''), html.H5(id='confirmed')],
                                             style={'width': '30%', 'display': 'inline-block', 'border': 'none', 'text-align': 'center', 'font-family': 'Century Gothic'}),
                                 ], style={'display': 'flex'}),

                                #style={'display': 'flex'}
                                html.Div([
                                        html.Div([ ], id='plot1'),
                                        html.Div([ ], id='plot2')
                                ], style={'display': 'flex'}),

                                html.Div([
                                        html.Div([ ], id='plot3'),
                                        html.Div([ ], id='plot4'),
                                        html.Div([ ], id='plot5'),
                                ], style={'display': 'flex'}),
                                # TASK3: Add a division with two empty divisions inside. See above disvision for example.
                                # Enter your code below. Make sure you have correct formatting.
#                                 html.Div([
#                                         html.Div([ ], id='plot6'),
#                                         html.Div([ ], id='plot7')
#                                 ], style={'display': 'flex'}),
                                ])

#function to grouping   فاتورة الشراء
def compute_info1(df_fourn, df_fourndet):
    # Select data
    # Compute group by fun sum  averages

    line_all_day = df_fourn.groupby('DAY')['multicurrency_total_ttc'].sum().reset_index()
    line_all_year = df_fourn.groupby('YEAR')['multicurrency_total_ttc'].sum().reset_index()

    line_all_quarter = df_fourn.groupby('QUARTER')['multicurrency_total_ttc'].sum().reset_index()
    all_count_sup = df_fourn.groupby('name_supplier')['multicurrency_total_ttc'].count()
    all_count_sup_fram = all_count_sup.to_frame()

    div_data = df_all_product.groupby('name_country')['total_value'].sum().reset_index()
    line_data = df_fourn.groupby(['MONTH','name_supplier'])['multicurrency_total_ttc'].sum().reset_index()
    tree_data = df_fourndet.groupby(['name_country','name_product'], as_index=False)['total_ht'].sum()
    #df_group = df_test.groupby(['drive-wheels', 'body-style'], as_index=False).mean() # must be False for the pivot to work
    #.reset_index()
    #as_index=False

    bar_data = df_fourn.groupby(['MONTH','name_supplier'])['multicurrency_total_ttc'].sum().reset_index()

    bar_data.sort_values(by=['multicurrency_total_ttc'])
    all_data = df_fourn['multicurrency_total_ttc'].sum()
    all_count = df_fourn['multicurrency_total_ttc'].count()

    '''
    count_data = df.groupby(['MONTH','name_consumer'])['multicurrency_total_ttc'].count().reset_index()
    df_all_facturedet_sum = df_facturedet.groupby(['MONTH','name_product'])['total_ht'].sum().reset_index()
    df_all_facturedet_count = df_facturedet.groupby(['MONTH','name_product'])['qty'].sum().reset_index()
    #avg_late = df.groupby(['Month','Reporting_Airline'])['LateAircraftDelay'].mean().reset_index()
    '''
    return  all_count_sup_fram,line_all_year,line_all_day,line_all_quarter,div_data,bar_data,line_data,tree_data,all_data,all_count

#function to grouping   فاتورة البيع
def compute_info2(df_facture, df_facturedet):
    # Select data
    # Select 2021 data
    # Group the data by Month and compute average over arrival delay time.
    #'Month',
    #df =  df_all[df_all['YEAR']==int(entered_year)]
    line_all_day_fac = df_facture.groupby('DAY')['multicurrency_total_ttc'].sum().reset_index()
    # Compute delay averages

    line_all_quarter_fac = df_facture.groupby('QUARTER')['multicurrency_total_ttc'].sum().reset_index()

    bar_data_fac = df_facture.groupby(['MONTH','name_consumer'])['multicurrency_total_ttc'].sum().reset_index()

    line_all_year_fac = df_facture.groupby('YEAR')['multicurrency_total_ttc'].sum().reset_index()

    all_count_cons_fram = df_facture.groupby('name_consumer')['multicurrency_total_ttc'].count()

    '''
    line_all_data = df_facture.groupby('MONTH')['multicurrency_total_ttc'].sum().reset_index()
    line_data = df_facture.groupby(['MONTH','name_consumer'])['multicurrency_total_ttc'].sum().reset_index()
    count_data = df_facture.groupby(['MONTH','name_consumer'])['multicurrency_total_ttc'].count().reset_index()
    df_all_facturedet_sum = df_facturedet.groupby(['MONTH','name_product'])['total_ht'].sum().reset_index()
    df_all_facturedet_count = df_facturedet.groupby(['MONTH','name_product'])['qty'].sum().reset_index()
    '''
    all_data_fac = df_facture['multicurrency_total_ttc'].sum()
    all_count_fac = df_facture['multicurrency_total_ttc'].count()
    #avg_late = df.groupby(['Month','Reporting_Airline'])['LateAircraftDelay'].mean().reset_index()
    return all_count_cons_fram,line_all_year_fac,bar_data_fac,line_all_quarter_fac,line_all_day_fac,all_data_fac,all_count_fac

def compute_info3(df_all_product,df_facture):
    # المخزون وحركه البيع
    # Select data
    # Select 2021 data
    # Group the data by Month and compute average over arrival delay time.
    #'Month',
    #df =  df_all[df_all['YEAR']==int(entered_year)]
    #line_all_day_fac = df_facture.groupby('DAY')['multicurrency_total_ttc'].sum().reset_index()
    # Compute delay averages
    bar_all_product = df_all_product.groupby('name_product')['total_value'].sum().reset_index()
    bar_all_product.sort_values("total_value", axis = 0, ascending = False ,
                 inplace = True, na_position ='last')
# ascending=False
#     data.sort_values("Name", axis = 0, ascending = True,
#                  inplace = True, na_position ='last')

    line_all_quarter_fac_p = df_facture.groupby('QUARTER')['multicurrency_total_ttc'].sum().reset_index()

    bar_all_product_count = df_all_product.groupby('name_product')['total_value'].count()
    line_all_year_fac = df_facture.groupby('YEAR')['multicurrency_total_ttc'].sum().reset_index()

    div_data_p = df_all_product.groupby('name_country')['total_value'].sum().reset_index()
    #bar_data_fac = df_facture.groupby(['MONTH','name_consumer'])['multicurrency_total_ttc'].sum().reset_index()

    #line_all_year_fac = df_facture.groupby('YEAR')['multicurrency_total_ttc'].sum().reset_index()

    #all_count_cons_fram = df_facture.groupby('name_consumer')['multicurrency_total_ttc'].count()
    '''
    line_all_data = df_facture.groupby('MONTH')['multicurrency_total_ttc'].sum().reset_index()
    line_data = df_facture.groupby(['MONTH','name_consumer'])['multicurrency_total_ttc'].sum().reset_index()
    count_data = df_facture.groupby(['MONTH','name_consumer'])['multicurrency_total_ttc'].count().reset_index()
    df_all_facturedet_sum = df_facturedet.groupby(['MONTH','name_product'])['total_ht'].sum().reset_index()
    df_all_facturedet_count = df_facturedet.groupby(['MONTH','name_product'])['qty'].sum().reset_index()
    '''
    all_data_product = df_all_product['total_value'].sum()
    all_count_product = df_all_product['total_value'].count()
    #avg_late = df.groupby(['Month','Reporting_Airline'])['LateAircraftDelay'].mean().reset_index()
    return div_data_p,line_all_year_fac,bar_all_product_count,line_all_quarter_fac_p,bar_all_product,all_data_product,all_count_product




#                 Output(component_id='plot6', component_property='children'),
#                 Output(component_id='plot7', component_property='children')
# add callback decorator
#callback
@app.callback( [Output('label', 'children'),
                Output('confirmed', 'children'),
                Output(component_id='plot1', component_property='children'),
                Output(component_id='plot2', component_property='children'),
                Output(component_id='plot3', component_property='children'),
                Output(component_id='plot4', component_property='children'),
                Output(component_id='plot5', component_property='children')],
               [Input(component_id='input-type', component_property='value'),
                Input(component_id='input-year', component_property='value')],
               # REVIEW4: Holding output state till user enters all the form information. In this case, it will be chart type and year
               [State("plot1", 'children'), State("plot2", "children"),
                State("plot3", "children"), State("plot4", "children"),
                State("plot5", "children")
               ])
def get_graph(chart, year, children1, children2, c3, c4, c5):
    #year1 = requests.get(year).txt

    if chart == 'OPT1':
         # Graph المشتريات
        df_fourn =  df_all_fourn[df_all_fourn['YEAR']==int(year or 0)]
        df_fourndet =  df_all_fourndet[df_all_fourndet['YEAR']==int(year or 0)]
        #calc of DATAFrame fro year
        # Compute required information for creating graph from the data
        all_count_sup_fram,line_all_year,line_all_day,line_all_quarter,div_data,bar_data,line_data,tree_data,all_data,all_count = compute_info1(df_fourn, df_fourndet)

        #fig.update_layout(width=700, height=500, bargap=0.05)
        #, padding="SAME"
        #1
        #bar_fig_day = px.bar(line_all_day, x='DAY', y='multicurrency_total_ttc', title='توزيعات الشراء ')
#         bar_fig_day = px.line(line_all_day, x='DAY', y='multicurrency_total_ttc')
#         bar_fig_day.add_bar(line_all_day, x='DAY', y='multicurrency_total_ttc', title='توزيعات الشراء ')
        #bar_fig_day.update_layout(width=700, height=400)

        fig = make_subplots(1,1)
        # add first bar trace at row = 1, col = 1
        fig.add_trace(go.Bar(x=line_all_day['DAY'], y=line_all_day['multicurrency_total_ttc'],
                     marker_color = 'green',
                     opacity=0.4))
        # add first scatter trace at row = 1, col = 1
        fig.add_trace(go.Scatter(x=line_all_day['DAY'], y=line_all_day['multicurrency_total_ttc'],
                                 line=dict(color='red')))
        fig.update_layout(showlegend=False)
        fig.update_layout(width=700, height=400)
        fig.update_layout(
            title="توزيعات الشراء",
            xaxis_title="الايام",
            yaxis_title="القيمة"
           )
#          ,
#             font=dict(
#                 family="Courier New, monospace",
#                 size=18,
#                 color="RebeccaPurple"
#                     )
# #             legend_title="Legend Title",
#         ,text="multicurrency_total_ttc" لاظهار القيم
        #bar_fig_day.add_traces(go.Scatter(x= dfs.bins, y=dfs.benchmark, mode = 'lines'))
        #color='DAY', marker_color='green',color_continuous_scale='Inferno',
        #2
        bar_fig_quarter = px.bar(line_all_quarter, x='QUARTER', y='multicurrency_total_ttc', title='توزيع الشراء خلال مواسم السنه')
        bar_fig_quarter.update_traces(marker_color='#07ed44')
        bar_fig_quarter.update_layout(bargap=.7)
        bar_fig_quarter.update_layout(width=500, height=400)
        #, bargap=0.05
        #bar_fig_quarter.update_traces(width=1)
        #color='QUARTER',
        #3
        bar_fig = px.bar(bar_data, x='name_supplier', y='multicurrency_total_ttc',  title='اجمالي شراء من كل مورد')
        bar_fig.update_traces(marker_color='#ed5b07')
        bar_fig.update_layout(width=700, height=500)
        bar_fig.update_layout(margin_l=0)


        # bar_data = df_fourn.groupby(['MONTH','name_supplier'])['multicurrency_total_ttc'].sum().reset_index()
        #4
        bar_year = px.bar(line_all_year, x='YEAR', y='multicurrency_total_ttc',  title='توزيع الشراء خلال السنوات')
        bar_year.update_layout(bargap=.7)
        bar_year.update_traces(marker_color='#f5b105')
        bar_year.update_layout(width=500, height=500)
        #color='MONTH',
        #5
        bar_sup = px.bar(all_count_sup_fram, x=all_count_sup_fram.index, y='multicurrency_total_ttc', title='توزيع عدد فواتيرالشراء بالنسبة للمورد')
        bar_sup.update_traces(marker_color='#8d0a8f')
        bar_sup.update_layout(width=700, height=500)
        #color='MONTH',
        #    all_count_sup = df_fourn.groupby(['MONTH','name_supplier'])['multicurrency_total_ttc'].count()
        #line_fig = px.line(line_data, x='MONTH', y='multicurrency_total_ttc', color='name_supplier', title='اجمالي شراء من كل مورد')


         # Number of flights under different cancellation categories

         #tree_fig_sup = px.treemap(bar_data,path=['name_supplier', 'MONTH'],values='multicurrency_total_ttc',color='multicurrency_total_ttc',color_continuous_scale='RdBu',title='Flight count by airline to destination state')
         #tree_data = df_fourndet.groupby(['name_country', 'name_product'])['multicurrency_total_ttc'].sum().reset_index()

        #pie_fig_sup = px.pie(bar_data, values='multicurrency_total_ttc', names='name_supplier', title=' توزيعات عمليات الشراء بالنسبة للموردين')
#         pie_fig = px.pie(div_data, values='total_ht', names='name_country', title='نسبة كل دولة من المشتريات')
#         pie_fig.update_layout(width=700, height=500)
#         tree_fig = px.treemap(tree_data,path=['name_country', 'name_product'],values='total_ht',color='total_ht',color_continuous_scale='RdBu',title= 'اجمالي الواردات لكل صنف حسب دولة المنشاء')
#         tree_fig.update_layout(width=700, height=500)
#         tree_fig = px.treemap(tree_data,path=['name_country', 'name_product'],values='total_ht')

        #tree_fig.update_traces(root_color="lightgrey")
#         tree_fig.update_layout(margin = dict(t=50, l=25, r=25, b=25))

        #,color='total_ht',color_continuous_scale='RdBu',title= 'اجمالي الواردات لكل صنف حسب دولة المنشاء')

        # fig = px.treemap(df, path=[px.Constant("all"), 'day', 'time', 'sex'], values='total_bill')
        # fig.update_traces(root_color="lightgrey")
        # fig.update_layout(margin = dict(t=50, l=25, r=25, b=25))
        # fig.show()
#         dcc.Graph(figure=pie_fig),
#         dcc.Graph(figure=tree_fig)
        #+str(round(all_data, 2))
        return [' اجمالي فواتير الشراء : '+str(round(all_data, 2)),'  عدد فواتير الشراء: '+str(all_count),
                dcc.Graph(figure=fig),
#                 dcc.Graph(figure=bar_fig_day),
                dcc.Graph(figure=bar_fig_quarter),
                dcc.Graph(figure=bar_fig),
                dcc.Graph(figure=bar_year),
                dcc.Graph(figure=bar_sup)
                ]

    elif chart == 'OPT2':
        # Graph المبيعات
        df_facture =  df_all[df_all['YEAR']==int(year or 0)]
        df_facturedet =  df_all_facturedet[df_all_facturedet['YEAR']==int(year or 0)]


        all_count_cons_fram,line_all_year_fac,bar_data_fac,line_all_quarter_fac,line_all_day_fac,all_data_fac,all_count_fac = compute_info2(df_facture, df_facturedet)
        #1
#         bar_fig_day_fac = px.bar(line_all_day_fac, x='DAY', y='multicurrency_total_ttc', title='توزيعات البيع ')
#         bar_fig_day_fac.update_layout(width=700, height=400)
        fig_fac = make_subplots(1,1)
        # add first bar trace at row = 1, col = 1
        fig_fac.add_trace(go.Bar(x=line_all_day_fac['DAY'], y=line_all_day_fac['multicurrency_total_ttc'],
                     marker_color = 'green',
                     opacity=0.4))
        # add first scatter trace at row = 1, col = 1
        fig_fac.add_trace(go.Scatter(x=line_all_day_fac['DAY'], y=line_all_day_fac['multicurrency_total_ttc'],
                                 line=dict(color='red')))
        fig_fac.update_layout(showlegend=False)
        fig_fac.update_layout(width=700, height=400)
        fig_fac.update_layout(
            title="توزيعات البيع",
            xaxis_title="الايام",
            yaxis_title="القيمة"
           )
        #2
        bar_fig_quarter_fac = px.bar(line_all_quarter_fac, x='QUARTER', y='multicurrency_total_ttc', title='توزيع البيع خلال مواسم السنه')
        bar_fig_quarter_fac.update_traces(marker_color='#07ed44')
        bar_fig_quarter_fac.update_layout(bargap=.7)
        bar_fig_quarter_fac.update_layout(width=500, height=400)
        #3   (2-1)
        bar_fig_fac = px.bar(bar_data_fac, x='name_consumer', y='multicurrency_total_ttc',  title='توزيعات البيع من خلال العملاء')
        bar_fig_fac.update_traces(marker_color='#ed5b07')
        bar_fig_fac.update_layout(width=700, height=500)
        #4   (2-2)
        bar_year_fac = px.bar(line_all_year_fac, x='YEAR', y='multicurrency_total_ttc',  title='توزيع البيع خلال السنوات')
        bar_year_fac.update_layout(bargap=.7)
        bar_year_fac.update_traces(marker_color='#f5b105')
        bar_year_fac.update_layout(width=500, height=500)
        #5   (2-3)
        bar_cons_fac = px.bar(all_count_cons_fram, x=all_count_cons_fram.index, y='multicurrency_total_ttc', title='عدد فواتيرالبيع بالنسبة للعملاء')
        bar_cons_fac.update_traces(marker_color='#8d0a8f')
        bar_cons_fac.update_layout(width=700, height=500)


        #line_all_fig = go.Figure(data=go.Scatter(x=line_data['MONTH'], y=line_data['multicurrency_total_ttc'], mode='line', marker=dict(color='green')))
        #ount_facturedet = px.line(df_all_facturedet_count, x='MONTH', y='qty', color='name_product', title='عدد المنتجات المباعه شهور ')
        #line_facturedet = px.line(df_all_facturedet_sum, x='MONTH', y='total_ht', color='name_product', title='اجمالي البيع للمنتجات شهور')
        #Bar
        #fig = go.Figure(data=go.Scatter(x=line_data['MONTH'], y=line_data['multicurrency_total_ttc'], mode='line', marker=dict(color='green')))
        #fig.update_layout(title='Month vs Average sales', xaxis_title='Month', yaxis_title='ArrDelay')
        #count_fig = px.line(count_data, x='MONTH', y='multicurrency_total_ttc', color='name_consumer', title='عدد مرات البيع للعملاء شهور')

        #line_fig = px.bar(line_data, x='MONTH', y='multicurrency_total_ttc', color='name_consumer',title='مبيعات العملاء شهور')

        #line_all_fig = px.line(line_all_data, x='MONTH', y='multicurrency_total_ttc', title='اجمالي المبيعات شهور')
        return[ ' اجمالي فواتير البيع : '+str(round(all_data_fac, 2)),'  عدد فواتير البيع: '+str(all_count_fac),
#                 dcc.Graph(figure=bar_fig_day_fac),
                dcc.Graph(figure=fig_fac),
                dcc.Graph(figure=bar_fig_quarter_fac),
                dcc.Graph(figure=bar_fig_fac),
                dcc.Graph(figure=bar_year_fac),
                dcc.Graph(figure=bar_cons_fac)
              ]

    else:
        df_facture =  df_all[df_all['YEAR']==int(year or 0)]

        div_data_p,line_all_year_fac,bar_all_product_count,line_all_quarter_fac_p,bar_all_product,all_data_product,all_count_product = compute_info3(df_all_product,df_facture)

        #1
        bar_fig_dproduct_sum = px.bar(bar_all_product, x='name_product', y='total_value', title='توزيع قيمة المنتجات المباعة بالنسبة للمنجات ')
        bar_fig_dproduct_sum.update_layout(width=700, height=500)
#         bar_fig_dproduct_sum.update_layout(xaxis=dict(rangeslider=dict(visible=True)))
#       , orientation='h'
# `     bar_fig_dproduct_count.update_layout(xaxis=dict(rangeslider=dict(visible=True),
#                              type="linear"))
#         bar_fig_dproduct_count.update_layout(xaxis=dict(rangeslider=dict(visible=True),
#                              type="multicategory"))
        #['-', 'linear', 'log', 'date', 'category','multicategory']

        #2
        bar_fig_quarter_fac = px.bar(line_all_quarter_fac_p, x='QUARTER', y='multicurrency_total_ttc', title='توزيع البيع خلال مواسم السنه')
        bar_fig_quarter_fac.update_traces(marker_color='#07ed44')
        bar_fig_quarter_fac.update_layout(bargap=.7)
        bar_fig_quarter_fac.update_layout(width=500, height=500)
#         #3   (2-1)
        bar_fig_dproduct_count = px.bar(bar_all_product_count, x=bar_all_product_count.index, y='total_value',title='توزيع الكميات المباعة بالنسبة للمنجات ')
        bar_fig_dproduct_count.update_traces(marker_color='#8d0a8f')
        bar_fig_dproduct_count.update_layout(width=700, height=500)
                #4   (2-2)
        bar_year_fac = px.bar(line_all_year_fac, x='YEAR', y='multicurrency_total_ttc',  title='توزيع البيع خلال السنوات')
        bar_year_fac.update_layout(bargap=.7)
        bar_year_fac.update_traces(marker_color='#f5b105')
        bar_year_fac.update_layout(width=500, height=500)
                #5   (2-3)
        pie_fig = px.pie(div_data_p, values='total_value', names='name_country', title='نسبة كل دولة من المشتريات')
        pie_fig.update_layout(width=700, height=500)
#         bar_fig_fac = px.bar(bar_data_fac, x='name_consumer', y='multicurrency_total_ttc',  title='توزيعات البيع من خلال العملاء')
#         bar_fig_fac.update_traces(marker_color='#ed5b07')
#         bar_fig_fac.update_layout(width=600, height=400)
#         #4   (2-2)
#         bar_year_fac = px.bar(line_all_year_fac, x='YEAR', y='multicurrency_total_ttc',  title='توزيع البيع خلال السنوات')
#         bar_year_fac.update_layout(bargap=.7)
#         bar_year_fac.update_traces(marker_color='#f5b105')
#         bar_year_fac.update_layout(width=300, height=400)
#         #5   (2-3)
#         bar_cons_fac = px.bar(all_count_cons_fram, x=all_count_cons_fram.index, y='multicurrency_total_ttc', title='عدد فواتيرالبيع بالنسبة للعملاء')
#         bar_cons_fac.update_traces(marker_color='#8d0a8f')


        #line_all_fig = go.Figure(data=go.Scatter(x=line_data['MONTH'], y=line_data['multicurrency_total_ttc'], mode='line', marker=dict(color='green')))
        #ount_facturedet = px.line(df_all_facturedet_count, x='MONTH', y='qty', color='name_product', title='عدد المنتجات المباعه شهور ')
        #line_facturedet = px.line(df_all_facturedet_sum, x='MONTH', y='total_ht', color='name_product', title='اجمالي البيع للمنتجات شهور')
        #Bar
        #fig = go.Figure(data=go.Scatter(x=line_data['MONTH'], y=line_data['multicurrency_total_ttc'], mode='line', marker=dict(color='green')))
        #fig.update_layout(title='Month vs Average sales', xaxis_title='Month', yaxis_title='ArrDelay')
        #count_fig = px.line(count_data, x='MONTH', y='multicurrency_total_ttc', color='name_consumer', title='عدد مرات البيع للعملاء شهور')

        #line_fig = px.bar(line_data, x='MONTH', y='multicurrency_total_ttc', color='name_consumer',title='مبيعات العملاء شهور')

        #line_all_fig = px.line(line_all_data, x='MONTH', y='multicurrency_total_ttc', title='اجمالي المبيعات شهور')
        return[ ' قمية المنتجات بالمخزن : '+str(round(all_data_product, 2)),'  كميات المنتجات بالمخزن: '+str(all_count_product),
                dcc.Graph(figure=bar_fig_dproduct_sum),
                dcc.Graph(figure=bar_fig_quarter_fac),
                dcc.Graph(figure=bar_fig_dproduct_count),
                dcc.Graph(figure=bar_year_fac),
                dcc.Graph(figure=pie_fig)
              ]


#return line_all_fig,line_fig, count_fig, line_facturedet, count_facturedet

# Run the app
if __name__ == '__main__':
        app.run_server()
#debug=True
