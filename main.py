import flet as ft
import pyrebase
from datetime import date, datetime
import locale
from flet import *
import numpy as np
from flet import UserControl



#################### Assets
BACKGROUND = "#E7E7ED"
BACKGROUND2 = "#EFEFEF"
BRANCO = "#FFFFFF"
CINZA_AZULADO = "#525A64"
PLACEHOLDER_INPUT = "#1C2439"
PRETO_50 = "#00000080"
PRIMARY_GREEN = "#00D154"
PRETO = "#000000"
WIDGET = "#EBEBF0"

############################# Dados Firebase

config = {
  'apiKey': "AIzaSyDRgO8OH2ctVG-d6D-bH3qD1cOqeeCXl_k",
  'authDomain': "estacao-meteorologic.firebaseapp.com",
  'databaseURL': "https://estacao-meteorologic-default-rtdb.firebaseio.com",
  'projectId': "estacao-meteorologic",
  'storageBucket': "estacao-meteorologic.appspot.com",
  'messagingSenderId': "483337827811",
  'appId': "1:483337827811:web:80b8b243ae10e899775cd6"
}

FIREBASE = pyrebase.initialize_app(config)

db = FIREBASE.database()

path1 = "/Produtor/Cultura/Meteorologia/{}/valor_atual"
path2 = "/Produtor/Cultura/{}"
path3 = "/Produtor/Cultura/Irrigacao/{}"


def calc_media(dicio, lista):
    length = 0
    soma = 0
    for valor in dicio.each():
       lista.append(valor.val()) 

    for valor in lista:
        soma = soma + valor

    media = soma/len(lista)
    return media
    

values_rad = []
values_temp = []
values_umi = []
values_vento = []
values_etc = []

dict_temp = db.child('/Produtor/Cultura/Meteorologia/temperatura_dht/3').get()
valores_etc = db.child('/Produtor/Cultura/Meteorologia/etc').get()
dict_rad = db.child('/Produtor/Cultura/Meteorologia/radiacao/3').get()
dict_umi = db.child('/Produtor/Cultura/Meteorologia/umidade/3').get()
dict_vento = db.child('/Produtor/Cultura/Meteorologia/vento/5').get()
dict_pressao = db.child('/Produtor/Cultura/Meteorologia/pressao_bmp/3').get()


Etc = calc_media(valores_etc, values_etc) #Saldo de radiação em MJ/m2.dia


Rn = calc_media(dict_rad, values_rad) #Saldo de radiação em MJ/m2.dia

Temp = calc_media(dict_temp, values_temp) # Temperatura em graus Celsius

ur = calc_media(dict_umi, values_umi)   # Umidade Relativa em porcentagem

vv = calc_media(dict_vento, values_vento)    # Velocidade do vento à 2m de altura em m/s


cultura = db.child('/Produtor/Cultura/cultura').get()
cultura = cultura.val()

data_plantio = db.child('/Produtor/Cultura/data_plantio').get()
data_plantio = data_plantio.val()

estagio = db.child('/Produtor/Cultura/estagio').get()
estagio = estagio.val()

Am = db.child('/Produtor/Cultura/Irrigacao/Am').get()
Am = Am.val()

TR = db.child('/Produtor/Cultura/Irrigacao/TR').get()
TR = TR.val()

Ai = db.child('/Produtor/Cultura/Irrigacao/Ai').get()
Ai = Ai.val()
Ai = float(Ai)


esp_linhas = db.child('/Produtor/Cultura/esp_linhas').get()
esp_linhas = esp_linhas.val()
esp_linhas = float(esp_linhas)

esp_plantas = db.child('/Produtor/Cultura/esp_plantas').get()
esp_plantas = esp_plantas.val()
esp_plantas = float(esp_plantas)


vazao = db.child('/Produtor/Cultura/Irrigacao/vz_gotej').get()
vazao = vazao.val()
vazao = float(vazao)

tempo_ant = db.child('/Produtor/Cultura/Irrigacao/tempo_ant').get()
tempo_ant = tempo_ant.val()

data_plantio = db.child('/Produtor/Cultura/data_plantio').get()
data_plantio = data_plantio.val()



def get_value(dicio):
    dic = dicio.val()
    ultimo_valor = list(dic.values())[-1]

    return str(ultimo_valor)
 


def setIdade(value):
    idd='idade'
    db.child(path2.format(idd)).set(value)


def registerCulture(dict_cultura, dict_irrigacao):
    for info in dict_cultura.keys():
        db.child(path2.format(info)).set(dict_cultura[info])
    for valor in dict_irrigacao:
        db.child(path3.format(valor)).set(dict_irrigacao[valor])


################################### Calculos de volume, tempo de irrigação e idade da planta 

################################ ETo

## Cálculo da Evapotranspiração de Referência (ETo)
## https://ainfo.cnptia.embrapa.br/digital/bitstream/CNPUV/8815/1/cir065.pdf

# Definição das variáveis

Rn = 12.3
G = 0 # Fluxo total diário de calor do solo em MJ/m2.dia 
z = 335     # Altitude do local em m'''

# Cálculo da declividade da curva de pressão de vapor em relação à temperatura (kPa/oC)
delta = 4098*(0.6108*2.71828**((17.27*Temp)/(Temp+237.3)))/(Temp+237.3)**2


# Cálculo do coeficiente psicométrico (kPa/oC)
gama = 0.665*(0.001)*(101.3*((293-0.0065*z)/293)**5.26)


# Cálculo do déficit de saturação 
# (Diferença entre Pressão de saturação de vapor - es e Pressão atual de vapor - ea) (kPa)
es = 0.6108*2.71828**((17.27*Temp)/(Temp+237.3))

ea = (es*ur)/100

# Cálculo da Evapotranspiração de Referência em mm
EToPMF = (0.408*delta*(Rn-G)+((gama*900*vv*(es-ea))/(Temp+273)))/(delta+gama*(1+0.34*vv))


##################### ETc


Kc= 1.10
Etc= (EToPMF*Kc)
Etc = float(Etc)


############################# Volume

Cu = 0.85

#Vt = volume total de água a ser aplicado por irrigação, m3;
Vt = 1000*((float(Etc)*float(TR)*float(Ai))/(Cu))

Vt = (int(Vt/100))


esp_plantas = esp_plantas/100
esp_linhas = esp_linhas/100

####################################### Tempo de irrigação
Ti = 6*((float(Vt)*float(esp_linhas)*float(esp_plantas))/(float(Ai)*float(vazao)))

Ti = round(Ti)
#Tempo de funcionamento por posição(Setor) para Irrigação em faixa contínua

Area = Ai*10000

################# idade da cultura
data1 = date.today()
data2 = datetime.strptime(data_plantio, "%d/%m/%Y").date()

idade = data1 - data2

idade = idade.days

setIdade(idade)


#################### Economia

economia_value = 100 - (((Ti/60)*vazao)/((tempo_ant/60)*vazao)*100)

quant_gotej = ((Ai*10000)/((esp_linhas/100)*(esp_plantas/100)))

litros_economizados = (quant_gotej*(tempo_ant/60)*vazao)-(Vt*1000)

litros_economizados = round(litros_economizados)

#economia = "{:.0f}%".format(economia)
#print(economia)
###################### templates

#################### Status estação
class DialogTemplateEstacao(ft.UserControl):
        def __init__(
            self,
            modal=False,
            content=None,
            content_padding=10,
            actions=None,
            actions_alignment=ft.MainAxisAlignment.END,
            actions_padding=None,
            shape=RoundedRectangleBorder(radius=10),
            on_dismiss=None,
        ):
            

            super().__init__()
            self.modal = modal
            self.content = content
            self.content_padding = content_padding
            self.actions = actions
            self.actions_padding = actions_padding
            self.actions_alignment = actions_alignment
            self.shape = shape
            self.on_dismiss = on_dismiss

        def build(self):

            actions = []
            """for action in self.actions:
                if isinstance(action, str):
                    actions.append(ft.TextButton(action, on_click=close))
                else:
                    actions.append(action)
            self.page.add(
                ft.ElevatedButton("Open modal dialog", on_click=open),
            )"""
            return ft.AlertDialog(
                modal=self.modal,
                content=self.content,
                content_padding=self.content_padding,
                actions=actions,
                actions_padding=self.actions_padding,
                actions_alignment=self.actions_alignment,
                shape=self.shape,
                on_dismiss=self.on_dismiss,
            )

class StatusTemplate(UserControl):
    """
    Classe para criar campos de texto com configurações comuns

    Atributos:
        ATRIBUTO    TIPO        DEFINIÇÃO                               DEFAULT
        label       (str)       Descrição do campo de texto             ("Texto")
        value       (int)       Valor inicial do campo de texto         (0)
        text_align  (TextAlign) Alinhamento do texto dentro do campo    (TextAlign.CENTER)
        width       (int)       Largura do campo de texto               (175)
        suffix_text (str)       Texto que aparece após o valor          ("")
    """

    def __init__(
        self,
        bgcolor='white',
        content=None,
        width=250,
        height=37,
        padding=padding.only(left=15, right=21),
        margin=0,
        border_radius=10,
    ):
        super().__init__()
        self.bgcolor = bgcolor
        self.content= content
        self.width = width
        self.height = height
        self.padding = padding
        self.margin = margin
        self.border_radius = border_radius

    def build(self):
        """
        Cria um objeto TextField com as configurações especificadas no construtor

        Retorna: TextField: campo de texto criado
        """
        return Container(
            bgcolor=self.bgcolor,
            content=self.content,
            width=self.width,
            height=self.height,
            padding=self.padding,
            margin=self.margin,
            border_radius = self.border_radius
        )

def status_template(titulo: str, unidade: str, status: str):
    # Cria os controles filhos para a linha do título
    texto_titulo = Text(titulo.title(), color="#000000", size=13, weight=FontWeight.W_600)

    # Cria os controles filhos para a linha do valor
    texto_unidade = Text(unidade, color="#000000", size=9, weight=FontWeight.W_700)
    container_unidade = Container(
        content=texto_unidade,
        alignment=alignment.center,
        border_radius=12,
        bgcolor='#EBEBF0',
        width=50,
        height=22,
    )

    if status == 'on':
        controles_status = [container_unidade, Icon(ft.icons.CIRCLE, color='#00D154', size=9)]
    elif status == 'off':
        controles_status = [container_unidade, Icon(ft.icons.CIRCLE, color='red', size=9)]

    # Cria a linha principal de conteúdo com as linhas de título e valor

    linha_status = Row(controls=controles_status)
    conteudo = Row(
        controls=[texto_titulo, linha_status],
        alignment=MainAxisAlignment.SPACE_BETWEEN,
    )

    # Retorna o objeto ClimaTemplate com o conteúdo e a cor de fundo
    return StatusTemplate(content=conteudo)


temperatura = status_template("temperatura", "°C", "on")

vento = status_template("vento", "km/h", "on")

umidade = status_template("umidade", "%", "on")

pressao = status_template("pressão", "hpa", "on")

radiacao = status_template("radiação", "W/m²", "off")


dlg_estacao = DialogTemplateEstacao(
    content=Container(
        width=270,
        height=310,
        bgcolor=None,
        content=Column(
            controls = [
                Container(
                    height=37,
                    width=270,
                    
                    content=Row(#vertical_alignment = CrossAxisAlignment.CENTER,
                        controls = [
                            Container(
                                margin=margin.only(right=-95, bottom=-140, top=-40, left=-20),
                                content = Image(
                                        src=f"/icons/settings.svg",                                          
                                    )
                            ),
                            Text(
                                "Estação",
                                color="#000000",
                                size=22,
                                weight=FontWeight.W_800,
                            ),

                            
                        ]
                    ) 
                ),
            
                Card(temperatura, elevation=9),
                Card(umidade, elevation=12),
                Card(vento, elevation=12),
                Card(pressao, elevation=12),
                Card(radiacao, elevation=8),
            ]
        )
    )
).build()

data_de_hoje = datetime.today()

# Obtenha o dia da semana, o dia do mês e o mês em formato de string
dia_da_semana = data_de_hoje.strftime('%A')
dia_do_mes = data_de_hoje.strftime('%d')
mes = data_de_hoje.strftime('%B')

# Formate a string no formato desejado
string_data = f"{dia_da_semana.title()}, {dia_do_mes} de {mes.lower()}"

class Estacao(UserControl):
    def build(self):
        def close_dlg(e):
            dlg_estacao.open = False
            self.page.update()
            
        def open_dlg_modal(e):
            self.page.dialog = dlg_estacao
            dlg_estacao.open = True
            self.page.update()

        return Container(
                width=70,
                height=29,
                margin=ft.margin.only(right=25.0, left=-50),
                on_click=open_dlg_modal,
                content=Container(
                    bgcolor=WIDGET,
                    padding=ft.padding.symmetric(horizontal=10),
                    border_radius=100,
                    content=Row(
                        spacing=3,
                        controls=[
                            Text(
                                value="Estação", color="#000000", size=10, weight=FontWeight.W_600
                            ),
                            Icon("settings", color=PRIMARY_GREEN, size=10),
                        ],
                    ),
                ),
        )
estacao = Estacao()


############################## Appbar


class AppBarTemplate(AppBar):
    """
    Classe para criar uma barra de aplicativo com configurações comuns

    Atributos:
        ATRIBUTO       TIPO        DEFINIÇÃO                                                             DEFAULT
        title          (Any):      Título da barra de aplicativo                                           (None)
        bgcolor        (Color):    Cor de fundo da barra de aplicativo                                     (colors.PRIMARY)
        actions        (list):     Lista de elementos a serem exibidos à direita da barra de aplicativo     (None)
    """

    def __init__(
        self,
        title=Container(
            content=Row(alignment=MainAxisAlignment.SPACE_BETWEEN,
                controls = [
                    Column(
                        controls=[
                            Text(
                                value="Olá, Victor",
                                color="#000000",
                                size=20,
                                weight=FontWeight.W_700,
                                font_family="Poppins Bold",
                            ),
                            Text(
                                value=string_data,
                                color="#000000",
                                size=10,
                                font_family="Poppins Regular",
                            ),
                        ],
                        spacing=3,
                    ),
                    estacao,
                ]
            ),
            margin=margin.only(left=20, bottom=10),    
        ),
        bgcolor=BRANCO,
    ):
        """
        Construtor da classe AppBarTemplate. Define os atributos title, bgcolor e actions da AppBar.

        Atributos:
        ATRIBUTO       TIPO        DEFINIÇÃO                                                             DEFAULT
        title          (Any):      Título da barra de aplicativo                                           (None)
        bgcolor        (Color):    Cor de fundo da barra de aplicativo                                     (colors.PRIMARY)
        actions        (list):     Lista de elementos a serem exibidos à direita da barra de aplicativo     (None)

        Returns:
            Nenhum retorno.
        """
        super().__init__()
        self.title = title
        self.bgcolor = bgcolor


appbar = AppBarTemplate()

########################cadastro cultura
class DialogTemplateCadastro(ft.UserControl):
    def __init__(
        self,
        modal=False,
        content=None,
        content_padding=padding.only(bottom=-10, top=10, left=0, right=0),
        actions=None,
        actions_padding=None,
        actions_alignment="center",
        shape=RoundedRectangleBorder(radius=10),
        on_dismiss=None,
    ):
        def on_close(self, e):
            self.open = False
            self.page.update()
            print("close")

        def on_open(self, e):
            self.page.dialog = dlg_cadastro
            self.open = True
            self.page.update()
            print("open")

        super().__init__()
        self.page = page
        self.modal = modal
        self.content = content
        self.content_padding = content_padding
        self.actions = actions
        self.actions_padding = actions_padding
        self.actions_alignment = actions_alignment
        self.shape = shape
        self.on_dismiss = on_dismiss
        self.on_open = on_open
        self.on_close = on_close

    def build(self):

        actions = []
        """for action in self.actions:
            if isinstance(action, str):
                actions.append(ft.TextButton(action, on_click=close))
            else:
                actions.append(action)
        self.page.add(
            ft.ElevatedButton("Open modal dialog", on_click=open),
        )"""
        return ft.AlertDialog(
            modal=self.modal,
            content=self.content,
            content_padding=self.content_padding,
            actions=actions,
            actions_padding=self.actions_padding,
            actions_alignment=self.actions_alignment,
            shape=self.shape,
            on_dismiss=self.on_dismiss,
        )

class TextFieldTemplate(UserControl):
    def __init__(
        self,
        border_radius=6,
        filled=True,
        border_color=colors.TRANSPARENT,
        bgcolor="#F1F4FA",
        width=273,
        height=40,
        label="Field",
        label_style=TextStyle(size=12, color='#1c2439', weight=FontWeight.W_400),
        text_style = TextStyle(size=12, color='#1c2439'),
        hint_style=TextStyle(size=12, color='#525a64', weight=FontWeight.W_700),
        hint_text = '',
        on_focus = None,
        keyboard_type=KeyboardType.TEXT,
        content_padding=padding.only(top=8, left=8, right=8),
    ):
        super().__init__()
        self.filled = filled
        self.border_color = border_color
        self.bgcolor = bgcolor
        self.width = width
        self.height = height
        self.border_radius = border_radius
        self.label = label
        self.label_style = label_style
        self.text_style = text_style
        self.hint_style = hint_style
        self.hint_text = hint_text
        self.on_focus = on_focus
        self.keyboard_type = keyboard_type
        self.content_padding = content_padding

    # top_view = self.page.views[-1]

    def build(self):
        """
        Cria um objeto TextField com as configurações especificadas no construtor

        Retorna: TextField: campo de texto criado
        """
        return TextField(
            filled = self.filled,
            border_color = self.border_color,
            bgcolor=self.bgcolor,
            width=self.width,
            height=self.height,
            border_radius=self.border_radius,
            label=self.label,
            label_style = self.label_style,
            text_style = self.text_style,
            hint_style = self.hint_style,
            hint_text = self.hint_text,
            on_focus = self.on_focus,
            keyboard_type=self.keyboard_type,
            content_padding = self.content_padding,
        )


data_de_plantio = TextFieldTemplate(
    width = 130,
    label='Data de plantio',
    hint_text='dd/mm/aa'
).build()

area = TextFieldTemplate(
    label='Área de cada setor',
    hint_text='Em ha'
).build()

vazao_gotejador = TextFieldTemplate(
    width=130, label='Vazão do gotejador',
    hint_text='Em litros/h'
).build()

espacamento_linhas = TextFieldTemplate(
    width=130, 
    label='Entre linhas',
    hint_text='Em cm²'
).build()

espacamento_plantas= TextFieldTemplate(
    width=130,
    label='Entre plantas',
    hint_text='Em cm²'
).build()

horas = TextFieldTemplate(
    width=130,
    label=None,
    hint_text='Horas'
).build()

minutos = TextFieldTemplate(
    width=130,
    label=None,
    hint_text='Minutos'
).build()

tipo = Dropdown(
    options=[
        dropdown.Option("Milho"),
        dropdown.Option("Melão"),
        dropdown.Option("Berinjela"),
    ],
    label='Tipo',
    width=130,
    height=40,
    content_padding=padding.only(left=10, right=12),
    text_style = TextStyle(size=11, color='#000000'),
    label_style = TextStyle(size=11, color='#1c2439'),
    border_radius=6,
    filled=True,
    border_color=colors.TRANSPARENT,
    bgcolor='#F1F4FA',
)

textura_solo = Dropdown(
    options=[
        dropdown.Option("Grossa"),
        dropdown.Option("Média"),
        dropdown.Option("Fina"),
    ],
    label='Textura do solo',
    width=130,
    height=40,
    content_padding=padding.only(left=10, right=12),
    text_style = TextStyle(size=11, color='#000000'),
    label_style = TextStyle(size=11, color='#1c2439'),
    border_radius=6,
    filled=True,
    border_color=colors.TRANSPARENT,
    bgcolor='#F1F4FA',
)

title_cadastrar = Text('Cadastro de cultura', color='#000000', size=17, weight=FontWeight.W_700)

text_cadastrar = Text('Preencha os campos abaixo para\ncadastrar sua cultura.', color='#000000', size=13)

text_espacamento = Text('Espaçamento:', color='#000000', weight=FontWeight.W_600, size=11)

text_tempo = Text('Tempo de irrigação atual por setor:', color='#000000', weight=FontWeight.W_600, size=11)

lista_inputs = [data_de_plantio,    vazao_gotejador,    espacamento_linhas,    
                espacamento_plantas,   horas,    minutos,   tipo, textura_solo, area]

info_cultura = {'data_plantio':0,   'esp_linhas': 0,    
                'esp_plantas': 0,   'cultura': 0, 'solo': 0} 

valores_irrigacao = {'vz_gotej': 0, 'tempo_ant': 0, 'Ai': 0}

def getValues(e):
    info_cultura['data_plantio'] = data_de_plantio.value
    info_cultura['esp_linhas'] = int(espacamento_linhas.value)
    info_cultura['esp_plantas'] = int(espacamento_plantas.value)
    info_cultura['cultura'] = tipo.value
    info_cultura['solo'] = textura_solo.value
    valores_irrigacao['Ai'] = area.value
    valores_irrigacao['tempo_ant'] = int(horas.value)*60 + int(minutos.value)
    valores_irrigacao['vz_gotej'] = int(vazao_gotejador.value)

    registerCulture(info_cultura, valores_irrigacao)

    for input in lista_inputs:
        input.value = ''

dlg_cadastro = DialogTemplateCadastro(
    content=Container(
        padding=padding.only(top=8, left=15, right=15, bottom=15),
        width=310,
        height=470,
        bgcolor='white',
        content = Column(alignment=MainAxisAlignment.CENTER,
            horizontal_alignment = CrossAxisAlignment.CENTER,
            controls = [
                Container(
                    alignment = alignment.top_left,
                    content = title_cadastrar,   
                ),
                    Container(
                    alignment = alignment.top_left,
                    margin=margin.only(bottom=10),
                    content = text_cadastrar,   
                ),
                Row(
                    controls = [
                        tipo,
                        data_de_plantio, 
                    ]
                ), 
                Container(
                    margin = margin.only(top=10),
                    alignment = alignment.top_left,
                    content = text_tempo,   
                ),                
                Row(
                    controls = [
                        horas,
                        minutos,
                    ]
                ), 
                    Row(
                    controls = [
                        vazao_gotejador,
                        textura_solo
                    ]
                ),                            
                Container(
                    margin = margin.only(top=10),
                    alignment = alignment.center_left,
                    content = text_espacamento,   
                ),
                Row(
                    controls = [
                        espacamento_linhas,
                        espacamento_plantas,
                    ]
                ),
                area,
            ]
        )
    ),
).build()

################### Clima

class ClimaTemplate(UserControl):
    """
    Classe para criar campos de texto com configurações comuns

    Atributos:
        ATRIBUTO    TIPO        DEFINIÇÃO                               DEFAULT
        label       (str)       Descrição do campo de texto             ("Texto")
        value       (int)       Valor inicial do campo de texto         (0)
        text_align  (TextAlign) Alinhamento do texto dentro do campo    (TextAlign.CENTER)
        width       (int)       Largura do campo de texto               (175)
        suffix_text (str)       Texto que aparece após o valor          ("")
    """

    def __init__(
        self,
        bgcolor=BRANCO,
        content=None,
        width=300,
        height=47,
        padding=padding.only(left=20, right=20),
        margin=0,
        border_radius=10,
    ):
        super().__init__()
        self.bgcolor = bgcolor
        self.content = content
        self.width = width
        self.height = height
        self.padding = padding
        self.margin = margin
        self.border_radius = border_radius

    def build(self):
        """
        Cria um objeto TextField com as configurações especificadas no construtor

        Retorna: TextField: campo de texto criado
        """
        return Container(
            bgcolor=self.bgcolor,
            content=self.content,
            width=self.width,
            height=self.height,
            padding=self.padding,
            margin=self.margin,
            border_radius=self.border_radius,
        )


# icons.AIR


def clima_template(titulo: str, valor: str, icone: str):
    # Cria os controles filhos para a linha do título
    imagem_titulo = Container(
        Image(src=f"/icons/clima/{titulo}.svg", width=18, height=18),
        shape=BoxShape.CIRCLE, 
        bgcolor=PRIMARY_GREEN, 
        padding=5
    )

    texto_titulo = Text(titulo.title(), color="#000000", size=15, weight=FontWeight.W_600)
    controles_titulo = [imagem_titulo, texto_titulo]

    # Cria os controles filhos para a linha do valor
    texto_valor = Text(valor, color="#000000", size=11, weight=FontWeight.W_700)
    container_valor = Container(
        content=texto_valor,
        alignment=alignment.center,
        border_radius=12,
        bgcolor=WIDGET,
        width=70,
        height=22,
    )
    imagem_valor = Image(src=f"/icons/{icone}.svg", height=13)
    controles_valor = [container_valor, imagem_valor]

    # Cria a linha principal de conteúdo com as linhas de título e valor
    linha_titulo = Row(controls=controles_titulo)
    linha_valor = Row(controls=controles_valor)
    conteudo = Row(
        controls=[linha_titulo, linha_valor],
        alignment=MainAxisAlignment.SPACE_BETWEEN,
    )

    # Retorna o objeto ClimaTemplate com o conteúdo e a cor de fundo
    return ClimaTemplate(content=conteudo)


temperatura = clima_template("temperatura", get_value(dict_temp)+' °C', "setaBaixo")
vento = clima_template("vento", get_value(dict_vento)+' Km/h', "setaCima")
umidade = clima_template("umidade", get_value(dict_umi)+' %', "setaBaixo")
pressao = clima_template("pressão", get_value(dict_pressao)+' hpa', "setaCima")
radiacao = clima_template("radiação", get_value(dict_rad)+' W/m²', "setaCima")


######## Containers

class TextTemplate(UserControl):
    """
    Classe para criar campos de texto com configurações comuns

    Atributos:
        ATRIBUTO    TIPO        DEFINIÇÃO                               DEFAULT
        label       (str)       Descrição do campo de texto             ("Texto")
        value       (int)       Valor inicial do campo de texto         (0)
        text_align  (TextAlign) Alinhamento do texto dentro do campo    (TextAlign.CENTER)
        width       (int)       Largura do campo de texto               (175)
        suffix_text (str)       Texto que aparece após o valor          ("")
    """

    def __init__(
        self,
        bgcolor=BRANCO,
        value="Milho",
        width=200,
        height=20,
        margin=0,
        color="#000000",
        size=10,
        weight=FontWeight.W_600,
    ):
        super().__init__()
        self.bgcolor = bgcolor
        self.value = value
        self.width = width
        self.height = height
        self.margin = margin
        self.color = color
        self.size = size
        self.weight = weight

    def build(self):
        """
        Cria um objeto TextField com as configurações especificadas no construtor

        Retorna: TextField: campo de texto criado
        """
        return Text(
            bgcolor=self.bgcolor,
            value=self.value,
            width=self.width,
            height=self.height,
            color=self.color,
            size=self.size,
            weight=self.weight,
        )


def click(e: ContainerTapEvent):
    print("clck")



line = Container(width=290, height=1.6, bgcolor="#00D154", alignment=alignment.center)

# Criação de campos de texto com configurações comuns

relatorio = Container(
    margin=margin.only(top=20),
    content=Row(
        controls=[
            Icon(icons.SQUARE, color="#00D154", size=16),
            Text(value="Relatório", color="#000000", size=20, weight=FontWeight.W_600),
        ],
        vertical_alignment=CrossAxisAlignment.CENTER
        # expand=1,
    ),
    width=300,
)

dashboard = Container(
    margin=margin.only(top=20),
    content=Row(
        controls=[
            Icon(icons.SQUARE, color="#00D154", size=16),
            Text(value="Dashboard", color="#000000", size=20, weight=FontWeight.W_600),
        ],
        vertical_alignment=CrossAxisAlignment.CENTER
        # expand=1,
    ),
    width=300,
)

clima = Container(
    margin=margin.only(top=20),
    content=Row(
        controls=[
            Icon(icons.SQUARE, color="#00D154", size=16),
            Text(value="Clima", color="#000000", size=20, weight=FontWeight.W_600),
        ],
        vertical_alignment=CrossAxisAlignment.CENTER
        # expand=1,
    ),
    width=300,
)


###################### Info Cultuta

class DialogTemplateCultura(ft.UserControl):
    def __init__(
        self,
        modal=False,
        content=None,
        actions=[],
        actions_padding=None,
        actions_alignment="end",
        shape=RoundedRectangleBorder(radius=10),
        on_dismiss=None,
    ):
        def on_close(self, e):
            self.open = False
            self.page.update()
            print("close")

        def on_open(self, e):
            self.page.dialog = dlg_cultura
            self.open = True
            self.page.update()
            print("open")

        super().__init__()
        self.modal = modal
        self.content = content
        self.actions = actions
        self.actions_padding = actions_padding
        self.actions_alignment = actions_alignment
        self.shape = shape
        self.on_dismiss = on_dismiss
        self.on_open = on_open
        self.on_close = on_close

    def build(self):
        return ft.AlertDialog(
            modal=self.modal,
            content=self.content,
            actions=self.actions,
            actions_padding=self.actions_padding,
            actions_alignment=self.actions_alignment,
            shape=self.shape,
            content_padding = 0,
            on_dismiss=self.on_dismiss,
        )

class TextFieldTemplate(UserControl):
    def __init__(
        self,
        border_radius=6,
        filled=True,
        border_color=colors.TRANSPARENT,
        bgcolor='#F1F4FA',
        width=74,
        height=39,
        read_only=True,
        label='Field',
        label_style=TextStyle(size=13, color='#1c2439', weight=FontWeight.W_400),
        value='Info',
        text_style = TextStyle(size=13, color='#1c2439'),
        content_padding = padding.only(left=15, bottom=10),

    ):
        super().__init__()
        self.filled = filled
        self.border_color = border_color
        self.bgcolor = bgcolor
        self.width = width
        self.height = height
        self.border_radius = border_radius
        self.read_only = read_only
        self.label = label
        self.label_style = label_style
        self.value = value
        self.text_style = text_style
        self.content_padding = content_padding
        

#top_view = self.page.views[-1]

    def build(self):
        """
        Cria um objeto TextField com as configurações especificadas no construtor

        Retorna: TextField: campo de texto criado
        """
        return TextField(
            filled = self.filled,
            border_color = self.border_color,
            bgcolor=self.bgcolor,
            width=self.width,
            height=self.height,
            border_radius=self.border_radius,
            read_only=self.read_only,
            label=self.label,
            label_style=self.label_style,
            value=self.value,
            text_style = self.text_style,
            content_padding = self.content_padding,
            
        )

info_tipo = TextFieldTemplate(width=300, label='Tipo', value=cultura).build()

info_data = TextFieldTemplate(width=117, label='Data de plantio', value=data_plantio).build()

info_area = TextFieldTemplate(width=117, label='Área', value="{:.0f} m²".format(Area)).build()

info_vazao = TextFieldTemplate(width=300, label='Vazão', value=str(vazao)+' L/h').build()

info_tempo_ant = TextFieldTemplate(label='Anterior', value=str(tempo_ant)+' min').build()

info_tempo_atu = TextFieldTemplate(label='Atual', value=str(Ti)+' min').build()

info_economia = TextFieldTemplate(bgcolor='#00D154', label='Economia', label_style=TextStyle(size=13, color='white', weight=FontWeight.W_400), value=str(economia_value)).build()

info_estagio = TextFieldTemplate(width=110, label='Estágio', value=estagio).build()

info_duracao = TextFieldTemplate(width=70, label='Duração', value='27 dias').build()

info_kc = TextFieldTemplate(width=45, label='Kc', value=Kc).build()

dlg_cultura = DialogTemplateCultura(
    content=Container(
        padding=13,
        margin=margin.only(bottom=-25),
        width=270,
        height=410,
        bgcolor='white',
        border_radius=10,
        content = Column(
            controls = [
                Row(vertical_alignment=CrossAxisAlignment.CENTER,
                    controls=[
                        Container(
                            content=Image(
                                src=f"assets/icons/corn.png",
                                width=170,
                                height=170,
                            ),
                            margin=margin.only(right=-130, bottom=-60, top=-60),
                        ),
                        Text(
                            "Milho",
                            color="#000000",
                            size=22,
                            weight=FontWeight.W_800,
                        )
                    ]
                ),
                info_tipo,
                Row(spacing=13,
                    controls=[
                            info_data,
                            info_area,
                    ]
                ),
                info_vazao,
                Container(
                    margin=margin.only(top=8),
                    content=Text(
                        'Tempo de irrigação',
                        color="#1C2A50",
                        size=13,
                        weight=FontWeight.W_600,                          
                    )
                ),
                Row(spacing=13,
                    controls = [
                        info_tempo_ant,
                        info_tempo_atu,
                        info_economia,
                    ]
                ),
                Container(
                    margin=margin.only(top=8),
                    content=Text(
                        'Desenvolvimento',
                        color='#1C2A50',
                        size=13,
                        weight=FontWeight.W_600,
                    )
                ),
                Row(spacing=13,
                    controls = [
                        info_estagio,
                        info_duracao,
                        info_kc,
                    ]
                ),
            ]
        ),         
    )         
).build()





###########CArds

class cadastrarCultura(UserControl): 
    def build(self):
        def close_dlg(e):
            dlg_cadastro.open = False
            self.page.update()

        def registerClose(e):
            getValues(e)
            dlg_cadastro.open = False
            card_cultura = Cultura()
            self.page.update()
            
        def open_dlg_modal(e):
            self.page.dialog = dlg_cadastro
            dlg_cadastro.open = True
            dlg_cadastro.actions = [
                Container(
                    width = 240,
                    height = 40,
                    bgcolor = '#00D154',
                    alignment=alignment.center,
                    border_radius=6,
                    on_click=registerClose,
                    content = Text('CADASTRAR', color='#1c2439', size=11, weight=FontWeight.W_600),
                )
            ]
            self.page.update()

        return Card(
            content=Container(
                bgcolor="white",
                height=95,
                width=300,
                border_radius=11,
                padding=padding.only(left=20, right=20),
                on_click=open_dlg_modal,
                content=Row(alignment=MainAxisAlignment.SPACE_BETWEEN,
                    controls = [
                        Text(
                            "Cadastre sua cultura",
                            color=PRETO,
                            size=19,
                            weight=FontWeight.W_700,
                        ),
                        Container(
                            bgcolor=PRIMARY_GREEN,
                            height=40,
                            width=40,
                            border_radius=30,
                            content = Icon(icons.ADD, size=24, color=BRANCO),
                        ),
                    ]
                )
            ),
            elevation=4,
        )

class Cultura(UserControl): 
    def build(self):
        def close_dlg(e):
            dlg_cultura.open = False
            self.page.update()
            
        def open_dlg_modal(e):
            self.page.dialog = dlg_cultura
            dlg_cultura.open = True
            self.page.update()

        return Card(
            elevation=6,
            content = Container(
                bgcolor="white",
                height=95,
                width=300,
                border_radius=11,
                padding=padding.only(left=20),
                on_click=open_dlg_modal,
                content=Row(
                    controls=[
                        Container(
                            Image(
                                src=f"/icons/corn.png",
                                width=300,
                                height=300,
                            ),
                            margin=margin.only(left=-60, right=-180),
                        ),
                        Column(
                            alignment=MainAxisAlignment.CENTER,
                            controls=[
                                Container(
                                    Text(
                                        "Milho",
                                        color="#000000",
                                        size=17,
                                        weight=FontWeight.W_600,
                                    ),
                                    margin=margin.only(bottom=-8),
                                ),
                                Text(
                                    "Plantio: {} \nEstágio: {} \nÁrea: {:.0f}m² \nVazão: {}L/h".format(data_plantio, estagio, Area, vazao),
                                    color="#000000",
                                    size=10,
                                    weight=FontWeight.W_600,
                                ),
                            ],
                        ),
                    ],
                ),
        ))
      
if cultura == 'none':
    card_cultura = cadastrarCultura()
else:
    card_cultura = Cultura()

card_irrigacao = Card(
    content = Container(
        bgcolor="white",
        height=140,
        width=140,
        border_radius=11,
        padding=padding.only(top=14, left=17, right=17, bottom=22),
        content=Column(
            controls=[
                Row(
                    controls=[
                        Container(
                            bgcolor="#EBEBF0",
                            height=24,
                            width=75,
                            border_radius=20,
                            margin=margin.only(right=7),
                            padding=padding.only(left=10),
                            content=ft.Text(
                                "Irrigação",
                                color="#000000",
                                size=12,
                                weight=FontWeight.W_700,
                            ),
                        ),
                        Image(
                            src=f"/icons/watch.svg",
                            width=20,
                            height=20,
                        ),
                    ]
                ),
                Container(
                    margin=margin.only(top=-7),
                    content= Text(
                                value=str(Ti)+'min',
                                color="#000000", size=33, weight=FontWeight.W_700
                            ),
                ),
                Container(
                    margin=margin.only(top=-4),
                    content = Text(
                        value="Tempo ideal de irrigação para hoje",
                        color="#000000",
                        size=11,
                        weight=FontWeight.W_400,
                    )
                ),
            ]
        ),
    ),
    elevation=8,
)

card_economia = Card(
    content = Container(
        bgcolor="white",
        height=140,
        width=140,
        border_radius=11,
        padding=padding.only(top=14, left=17, right=17, bottom=22),
        content=Column(
            controls=[
                Row(
                    controls=[
                        Container(
                            bgcolor="#EBEBF0",
                            height=24,
                            width=75,
                            border_radius=20,
                            margin=margin.only(right=7),
                            padding=padding.only(left=10),

                            content=ft.Text(
                                "Economia",
                                color="#000000",
                                size=12,
                                weight=FontWeight.W_700,
                            ),
                        ),
                        Image(
                            src=f"assets/icons/percentage.svg",
                            width=20,
                            height=20,
                        ),
                    ]
                ),
                Container(
                    Text(
                        value="{:.0f}%".format(economia_value), color="#000000", size=33, weight=FontWeight.W_700
                    ),
                ),
                Container(
                    content = ft.Text(
                        str(litros_economizados)+" litros economizados",
                        color="#000000",
                        size=11,
                        weight=FontWeight.W_400,
                    ),
                    margin=margin.only(top=-4),
                ),
            ]
        ),
    ),
    elevation=8,
)

card_ET = Card(
    content = Container(
        bgcolor=BRANCO,
        # height=120,
        width=300,
        border_radius=11,
        padding=padding.only(top=14, left=20, right=10, bottom=25),
        content=Column(
            spacing=12,
            controls=[
                Container(
                    bgcolor=WIDGET,
                    height=22,
                    width=500,
                    border_radius=17,
                    alignment=alignment.center,
                    # margin=margin.only(top=-10, bottom=-22, left=-14, right=20),
                    content=Text(
                        "Evapotranspiração",
                        color="#000000",
                        size=12,
                        weight=FontWeight.W_700,
                    ),
                ),
                Row(
                    spacing=50,
                    alignment=MainAxisAlignment.CENTER,
                    controls=[
                        Column(
                            horizontal_alignment=CrossAxisAlignment.CENTER,
                            spacing=1,
                            controls=[
                                Row(
                                    alignment=MainAxisAlignment.CENTER,
                                    controls=[
                                        Image(
                                            src=f"/icons/gotinha.svg",
                                            width=16,
                                            height=16,
                                        ),
                                        Container(
                                            content=Text(
                                                "Referencia",
                                                color="#000000",
                                                size=12,
                                                weight=FontWeight.W_700,
                                            ),
                                            alignment=alignment.center,
                                        ),
                                    ],
                                ),
                                Container(
                                    Column(
                                        [
                                            Text(
                                                value="{:.2f}".format(EToPMF),
                                                font_family="Montserrat",
                                                color="#000000",
                                                size=42,
                                                weight=FontWeight.W_700,
                                            ),
                                            Text(
                                                value="mm/dia",
                                                color="#808080",
                                                size=17,
                                                weight=FontWeight.W_700,
                                            ),
                                        ],
                                    )
                                ),
                            ],
                        ),
                        Column(
                            horizontal_alignment=CrossAxisAlignment.CENTER,
                            spacing=1,
                            controls=[
                                Row(
                                    alignment=MainAxisAlignment.CENTER,
                                    controls=[
                                        Image(
                                            src=f"/icons/plantinha.svg",
                                            width=16,
                                            # height=16,
                                        ),
                                        Container(
                                            content=Text(
                                                "Cultura",
                                                color="#000000",
                                                size=12,
                                                weight=FontWeight.W_700,
                                            ),
                                            alignment=alignment.center,
                                        ),
                                    ],
                                ),
                                Container(
                                    Text(
                                        value="{:.2f}".format(Etc),
                                        font_family="Montserrat",
                                        color="#000000",
                                        size=42,
                                        weight=FontWeight.W_700,
                                    ),
                                ),
                                Container(
                                    Text(
                                        value="mm/dia",
                                        color="#808080",
                                        size=17,
                                        weight=FontWeight.W_700,
                                    ),
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        ),
    ),
    elevation=8,
)





################### Elevated button


class ElevatedButtonTemplate:
    """Classe para criar botões elevados com configurações comuns

    Atributos:
        ATRIBUTO    TIPO        DEFINIÇÃO                       DEFAULT
        autofocus   (bool):     Se o botão tem autofoco         (False)
        bgcolor     (Color):    Cor de fundo do botão           (ft.colors.PRIMARY)
        color       (Color):    Cor do texto do botão           (ft.colors.WHITE)
        content     (Any):      Conteúdo do botão               (None)
        elevation   (int):      Altura do sombreamento do botão (2)
        icon        (str):      Icone do botão                  (None)
        icon_color  (Color):    Cor do icone                    (ft.colors.PRIMARY)
        style       (str):      Estilo css do botão             (None)
        text        (str):      Texto do botão                  ("Button")
        tooltip     (str):      Texto de dica                   (None)
    """

    def __init__(
        self,
        autofocus=False,
        bgcolor="white",
        color=ft.colors.WHITE,
        content=None,
        elevation=2,
        icon=None,
        icon_color=ft.colors.PRIMARY,
        style=None,
        text="Button",
        tooltip=None,
    ):

        self.autofocus = autofocus
        self.bgcolor = bgcolor
        self.color = color
        self.content = content
        self.elevation = elevation
        self.icon = icon
        self.icon_color = icon_color
        self.style = style
        self.text = text
        self.tooltip = tooltip

    def build(self):
        """
        Cria um objeto <ElevatedButton> com as configurações especificadas no construtor

        Retorna: ElevatedButton: botão elevado criado
        """
        return ft.ElevatedButton(
            autofocus=self.autofocus,
            bgcolor=self.bgcolor,
            color=self.color,
            content=self.content,
            elevation=self.elevation,
            icon=self.icon,
            icon_color=self.icon_color,
            style=self.style,
            text=self.text,
            tooltip=self.tooltip,
        )


# Criação de botões elevados com configurações comuns
HomeButton = ElevatedButtonTemplate(text="Estou em home").build()
LoginButton = ElevatedButtonTemplate(
    text="Perfil",
    icon=(ft.Image(src=f"/icons/icon.png")),
).build()

ElevatedButton = ElevatedButtonTemplate(text="Go to Login").build()
ElevatedButton2 = ElevatedButtonTemplate(text="Go to HOME").build()


########################  NAvigation Bar

class NavigationDestinationTemplate(NavigationDestination):
    def __init__(self, icon, label="Cultura", width=16):
        super().__init__()
        self.label = label
        self.icon_content = Image(src=f"/icons/navbar/{icon}.svg", width=width)


class NavigationBarTemplate(NavigationBar):
    """
    Classe para criar uma barra de navegação com configurações comuns

    Atributos:
        ATRIBUTO       TIPO                            DEFINIÇÃO
        destinations   (List[NavigationDestination])   lista de destinos de navegação
    """

    def __init__(
        self,
        destinations=[
            NavigationDestinationTemplate(label="Dashboard", icon="plant"),
            NavigationDestinationTemplate(label="Home", icon="home"),
            NavigationDestinationTemplate(label="Perfil", icon="user"),
        ],
        bgcolor="#FFFFFF",
        height=70,
        page: Page = None,
    ):
        super().__init__()
        self.destinations = destinations
        self.bgcolor = bgcolor
        self.height = height
        self.page = page
        self.on_change = self.change

    def change(self, e):
        self.page.go(e.control.selected_index)


navigation_bar = NavigationBarTemplate()


###################### Renderizar home page

class HomePage:
    def build():
        return ft.View(
            "/",
            [
                Column(
                    controls=[
                        card_cultura,
                        line,
                        relatorio,
                        Row(
                            controls=[
                                card_irrigacao,
                                card_economia,
                            ],
                            alignment="center",
                        ),
                        card_ET,
                        clima,
                        Card(temperatura, elevation=8),
                        Card(umidade, elevation=8),
                        Card(vento, elevation=8),
                        Card(pressao, elevation=8),
                        Card(radiacao, elevation=4),
                    ],
                    horizontal_alignment="center",
                ),
                navigation_bar,
            ],
            scroll="auto",
            appbar=appbar,
            horizontal_alignment="center",
        )

########################### Route config

class RouteConfig:
    """
    Classe que representa as rotas disponíveis no aplicativo web.
    """

    def __init__(self, page: Page):
        self.page = page
        self.routes = {
            "/": HomePage.build(),
        }
        """
        Configura os eventos de mudança de rota e de remoção da última vista.
        """
        self.page.on_route_change = self.route_change
        self.page.on_view_pop = self.view_pop
        self.page.go(self.page.route)

    def route_change(self, route):
        """
        Método que trata a mudança de rota.
        Limpa a lista de vistas e adiciona a vista destino à lista.
        """
        self.page.views.clear()
        self.page.views.append(self.get_destiny(self.page.route))
        self.page.update()

    def view_pop(self, view):
        """
        Método que remove a última vista da lista.
        """
        self.page.views.pop()
        top_view = self.page.views[-1]
        self.page.go(top_view.route)

    def get_destiny(self, route):
        """
        Método que retorna o destino (página ou componente) associado à rota especificada.
        Se a rota não estiver presente em routes, retorna a página inicial.
        """
        # Retorna o destino (página ou componente) associado à rota especificada
        return self.routes.get(route, "/")

    def get_routes(self):
        """
        Método que retorna uma lista de todas as rotas disponíveis no aplicativo.
        """
        # Retorna uma lista de todas as rotas disponíveis no aplicativo
        return list(self.routes.keys())

    def go_route(self, index):
        """
        Método que vai para a rota correspondente ao índice especificado.
        """
        self.page.go(self.get_routes()[index])


############ Main.py
def main(page: ft.Page):

    navigation_bar.page = page
    RouteConfig(page)
   
    # firebase = config.firebase.FirebaseConfig(page)


ft.app(main, view=ft.WEB_BROWSER)
