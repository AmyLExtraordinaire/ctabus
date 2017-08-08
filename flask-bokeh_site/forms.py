from flask_wtf import Form
from wtforms import SelectField

class RouteSelectForm(Form):
    route = SelectField(
        'Route',
        choices=[
        	('6', '6 Jackson Park Express'),
        	('9', '9 Ashland'),
        	('15', '15 Jeffery Local'),
        	('31', '31 31st'),
        	('47', '47 47th'),
        	('55', '55 Garfield'),
        	('66', '66 Chicago'), 
        	('72', '72 North'), 
        	('73', '73 Armitage'),
        	('77', '77 Belmont'),
        	('82', '82 Kimball-Homan')
        ],
        default='55'
    )