import os
import numpy
import base64
import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
from datetime import datetime
import plotly.express as px
from dash.dependencies import Input, Output, State
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
import pandas as pd
from predict import get_closest_img_names


server = Flask(__name__)
app = dash.Dash(__name__, server=server, external_stylesheets=[dbc.themes.JOURNAL])
app.server.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app.server)


COLORS = {'background': '#f4f4f4'}
query = """
select *
from animals
where is_social = 'да'
"""
df = pd.read_sql_query(query, con=db.engine)
df['date'] = pd.to_datetime(df['date'])
df['year'] = df['year'].apply(lambda x: x.split('-')[0])
df['year'] = 2020 - df['year'].astype(int)
dict_values = df.to_dict(orient='index')
animal_type_list = ['кошка', 'собака']
address_list = df['address'].unique()
values = list(dict_values.keys())


def create_submit_modal(pet_id):
    modal = html.Div(
        [
            dbc.Button(
                "Забрать",
                id=f"open_submit_{pet_id}",
                style={'margin': '0px 0px 0px 20px'},
                size='lg',
                color='dark',
                outline=True
            ),

            dbc.Modal([
                dbc.ModalHeader(f"Готовы взять питомца"),
                dbc.ModalBody(
                    dbc.Form(
                        [
                            dbc.FormGroup(
                                [
                                    dbc.Label("Имя", className="mr-2"),
                                    dbc.Input(type="text", placeholder="Введите Ваше имя"),
                                ],
                                className="mr-3",
                            ),
                            dbc.FormGroup(
                                [
                                    dbc.Label("e-mail", className="mr-2"),
                                    dbc.Input(type="email", placeholder="Введите e-mail"),
                                ],
                                className="mr-3",
                            ),
                            dbc.FormGroup(
                                [
                                    dbc.Label("Комментарий", className="mr-2"),
                                    dbc.Input(type="text"),
                                ],
                                className="mr-3",
                            ),
                            dbc.Button("Отправить", color="primary"),
                        ],
                        inline=True,
                    )
                ),
                dbc.ModalFooter(
                    dbc.Button("Закрыть", id=f"close_submit_{pet_id}", className="ml-auto")
                ),

            ],
                id=f"modal_submit_{pet_id}",
                is_open=False,    # True, False
                size="xl",        # "sm", "lg", "xl"
                backdrop=True,    # True, False or Static for modal to not be closed by clicking on backdrop
                scrollable=True,  # False or True if modal has a lot of text
                centered=True,    # True, False
                fade=True         # True, False
            ),
        ]
    )
    return modal


def create_pet_info_modal(pet_id, name, img, animal, year, weight, address):
    if address == 'г.Москва, Проектируемый проезд №5112, вл.2\\1':
        map_address = 'г.Москва, Проектируемый проезд №5112, вл.2'
    else:
        map_address = address
        
    info_card = dbc.Card(
        [
            # image
            dbc.CardBody(
                html.H4(f'Привет, {animal} по кличке {name}, ждет своих старших друзей. Вес: {weight} кг. Ждет по адресу: {address}')
            ),
            dbc.CardImg(src=f'assets/maps/{map_address}.png', top=True, bottom=False,
                    title="Расположение приюта", alt='Скоро мы добавим фото нашего друга')
        ]
    )
    
    
    modal = html.Div(
        [
            dbc.Button(
                "Подробнее",
                id=f"open_pet_info_{pet_id}",
                style={'margin': '-76px 0px 0px 200px'},
                size='lg',
                color='dark',
                outline=True
            ),

            dbc.Modal([
                dbc.ModalHeader("Готовы взять питомца"),
                dbc.ModalBody(
                    info_card
                ),
                dbc.ModalFooter(
                    dbc.Button("Закрыть", id=f"close_pet_info_{pet_id}", className="ml-auto")
                ),
                
            ],
                id=f"modal_pet_info_{pet_id}",
                is_open=False,    # True, False
                size="xl",        # "sm", "lg", "xl"
                backdrop=True,    # True, False or Static for modal to not be closed by clicking on backdrop
                scrollable=True,  # False or True if modal has a lot of text
                centered=True,    # True, False
                fade=True         # True, False),
            ),
        ]
            
        
    )
        
    return modal


def find_photo(search_name):
    img = 'assets/dog.jpg'
    files = os.listdir('assets')
    
    for file in files:
        if file != 'maps':
            name, ext = file.split('.')[0], file.split('.')[1]
            if name == search_name:
                img = f'assets/{name}.{ext}'
                break
    return img


def make_card(pet_id, pet_card, name, breed, date, animal, year, weight, address):
    img = find_photo(pet_card)
    card_question = dbc.Card(
        [
            dbc.CardImg(src=img, top=True, bottom=False,
                        title="Image by Kevin Dinkel", alt='Скоро мы добавим фото нашего друга',
                        #style={'height':'20%', 'width':'20%'}
                       ),
            dbc.CardBody(
                [
                    html.H4(f'{name}, {animal}', className="card-title"),
                    html.P(f'{breed}, возраст: {year}', className="card-subtitle"),
                    html.P(
                        f"Ждет своего хозяина уже {(datetime.now().date() - date.date()).days} суток",
                        className="card-text",
                    ),
                ],
            ),
            create_submit_modal(pet_id),
            create_pet_info_modal(pet_id, name, img, animal, year, weight, address)
        ],
        inverse=False,   # change color of text (black or white)
        outline=True,    # True = remove the block colors from the background and header
    )
    return card_question


cards = dbc.CardColumns(
    children=[make_card(
        dict_values[key]['id'],
        dict_values[key]['card'],
        dict_values[key]['name'],
        dict_values[key]['breed'],
        dict_values[key]['date'],
        dict_values[key]['animal'],
        dict_values[key]['year'],
        dict_values[key]['weight'],
        dict_values[key]['address']
    ) for key in values],
    id='cards',
    style={'padding': '20px 100px 0px 100px'}
)


age_select_layout = html.Div([

    html.Div([
        html.Label(['Возраст:'],
                    style={'font-weight': 'bold'}),
        html.P(),
        dcc.RangeSlider(
            id='age_range_slider',
            marks={
                0: '0',
                2: '2',
                4: '4',
                10: '10',
                20: {'label': '20', 'style': {'color':'#f50', 'font-weight':'bold'}},
            },
            step=1,
            min=0,
            max=20,
            value=[0,3],
            dots=True,             # True, False - insert dots, only when step>1
            allowCross=False,      # True,False - Manage handle crossover
            disabled=False,        # True,False - disable handle
            updatemode='mouseup',  # 'mouseup', 'drag' - update value method
            included=True,         # True, False - highlight handle
            vertical=False,        # True, False - vertical, horizontal slider
            verticalHeight=900,    # hight of slider (pixels) when vertical=True
            className='None',
            ),
    ]),

])


address_dropdown_layout = html.Div([
    html.Label(['Приют:'],style={'font-weight': 'bold', "text-align": "center"}),

    dcc.Dropdown(id='address_dropdown',
        options=[{'label' : color, 'value': color} for color in address_list],
        optionHeight=35, 
        value='г.Москва, Востряковский пр-д, вл.10 А',
        disabled=False,                     #disable dropdown value selection
        multi=False,                        #allow multiple dropdown values to be selected
        searchable=True,                    #allow user-searching of dropdown values
        search_value='',                    #remembers the value searched in dropdown
        placeholder='Пожалуйста, выберите', 
        clearable=True,                     #allow user to removes the selected value
        style={'width':"100%"},             #use dictionary to define CSS styles of your dropdown
        )                                   #'memory': browser tab is refreshed
])


animal_layout = html.Div([
    html.Label(['Выберите животное:'], style={'font-weight': 'bold'}),
    dcc.Dropdown(
        id='animal_type_checklist',                      # used to identify component in callback
        options=[{'label': animal_type, 'value': animal_type} for animal_type in animal_type_list], # class of the <label> that wraps the checkbox input and the option's label
        optionHeight=35,                    #height/space between dropdown options
        disabled=False,                     #disable dropdown value selection
        multi=False,
        value='собака',     #allow multiple dropdown values to be selected
        searchable=True,                    #allow user-searching of dropdown values
        search_value='',                    #remembers the value searched in dropdown
        placeholder='Пожалуйста, выберите',     #gray, default text shown when no option is selected
        clearable=True,                     #allow user to removes the selected value
        style={'width':"100%"},
    )
])


search_button_layout = html.Div([
    dbc.Button('Поиск', id='search', n_clicks=1)
], style={'padding': '20px 100px 0px 100px'})


search_layout = html.Div([
    animal_layout,
    address_dropdown_layout,
    age_select_layout,
    #search_button_layout
], style={'padding': '20px 100px 0px 100px'})


upload_img_layout = html.Div([
    html.Label(['Вы можете найти наиболее похожего питомца по Вашей фотографии:'],style={'font-weight': 'bold', "text-align": "center"}),
    dcc.Upload(
        dbc.Button('Загрузить фото'),
        id='upload-image',
        contents=''
    ),
    #html.Div(id='output-image-upload')
], style={'padding': '20px 100px 0px 100px'})


app.layout = html.Div(
    style={'backgroundColor': COLORS['background']},
    children=[
        search_layout,
        upload_img_layout,
        search_button_layout,
        cards
])


#@app.callback(Output('output-image-upload', 'children'),
#              [Input('upload-image', 'contents')])
#def output_img(contents):
#    return html.Img(src=contents, style={'height':'20%', 'width':'20%'})


@app.callback(Output(component_id='cards', component_property='children'),
    [Input(component_id='age_range_slider', component_property='value'),
     Input(component_id='address_dropdown', component_property='value'),
     Input(component_id='animal_type_checklist', component_property='value'),
     Input(component_id='search', component_property='n_clicks'),
     Input('upload-image', 'contents')]
)
def return_search_params(age_range, address, animal_types, n_clicks, contents):
    print(age_range)
    if n_clicks:
        values = list(df[
            (df['address'] == address)
            & (df['animal'] == animal_types)
            & (df['year'] <= age_range[1])
            & (df['year'] >= age_range[0])
        ].index)
                 
        if contents != '':
            filtered_card_names = [dict_values[key]['card'] for key in values]
            filtered_img_names = [find_photo(card) for card in filtered_card_names]
            print('1', filtered_img_names)
            filtered_img_names = [img.split('/')[1] for img in filtered_img_names]
            print('2', filtered_img_names)
            
            data = contents.encode("utf8").split(b";base64,")[1]
            with open('search_images/photo_from_search.jpg', "wb") as fp:
                fp.write(base64.decodebytes(data))  
            
            search_img_name = 'photo_from_search.jpg'
            search_path = 'search_images'
            weights_path = 'models/weights/DenseNet-BC-121-32-no-top.h5'
            
            closest_card_names = get_closest_img_names(filtered_img_names,
                                  'assets',
                                  search_img_name,
                                  search_path,
                                  weights_path)
            
            values = [key for key in values if dict_values[key]['card'] in closest_card_names]
            
        cards = [make_card(
            dict_values[key]['id'],
            dict_values[key]['card'],
            dict_values[key]['name'],
            dict_values[key]['breed'],
            dict_values[key]['date'],
            dict_values[key]['animal'],
            dict_values[key]['year'],
            dict_values[key]['weight'],
            dict_values[key]['address']
        ) for key in values]   
            
        return cards
    
    
for key in values:
    @app.callback(
        Output(f"modal_pet_info_{dict_values[key]['id']}", "is_open"),
        [Input(f"open_pet_info_{dict_values[key]['id']}", "n_clicks"), Input(f"close_pet_info_{dict_values[key]['id']}", "n_clicks")],
        [State(f"modal_pet_info_{dict_values[key]['id']}", "is_open")],
    )
    def toggle_modal_pet_info(n1, n2, is_open):
        if n1 or n2:
            return not is_open
        return is_open

    @app.callback(
        Output(f"modal_submit_{dict_values[key]['id']}", "is_open"),
        [Input(f"open_submit_{dict_values[key]['id']}", "n_clicks"), Input(f"close_submit_{dict_values[key]['id']}", "n_clicks")],
        [State(f"modal_submit_{dict_values[key]['id']}", "is_open")],
    )
    def toggle_modal_submit(n1, n2, is_open):
        if n1 or n2:
            return not is_open
        return is_open


if __name__ == '__main__':
    app.run_server(debug=True, host='mn-hdap03', port=8913)