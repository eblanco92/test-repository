from flask import Flask,request
from flask_restful import Api
from flask_restful import Resource, reqparse
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

#
app = Flask(__name__)

app.config['PROPAGATE_EXCEPTIONS'] = True
app.secret_key = 'jose'
api = Api(app)
#initialize spreadsheet------------


scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('world_samples_secret.json', scope)
client = gspread.authorize(creds)
sheet = client.open('World Samples').sheet1
countries = (sheet.col_values(1))
c = 0
country_list = list(range(0, len(countries)))
for country in countries:
    x = country.split("|")
    country_list[c] = x[0]
    c += 1

data = sheet.get_all_values()
df = pd.DataFrame.from_records(data, columns=data[0])
#---------------------------------------

class linkGetter(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('region',
                        type=str,
                        required=True,
                        help="This field cannot be left blank!"
                        )
    parser.add_argument('docType',
                        type=str,
                        required=False,
                        help="Please specify NI, PS or DL"
                        )

    def get(self):
            data = request.get_json()
            region = data['region']
            docType = data['docType']
            for country in countries:
                if country[0:2] == region:
                    country_to_find = country
            docs_country = df[df['Country'] == country_to_find]
            spec_docs_country = docs_country[docs_country["Type"] == docType]
            l = spec_docs_country.index
            columnsWithLinks = ['E', 'F', 'G', 'H', 'I', 'J', 'K']
            # ,'L','M','N','O','P','Q','R','S','T','U','V','Y','Z']
            # need to handle exception when no sample was found mb if index is [] then stop and message : no samples available
            links = []
            html = '<H1>Hello world </H1>'
            for index in l:
                index = index + 1
                for column in columnsWithLinks:
                    cell_to_find = column + str(index)
                    cell_to_evaluate = sheet.acell(cell_to_find, value_render_option='FORMULA').value
                    if cell_to_evaluate is not '':
                        # print('link is =',cell_to_evaluate.split('"')[1])
                        if len(cell_to_evaluate.split('"')) == 3:
                            link = cell_to_evaluate.split('"')[1]
                            links.append(link)
                            # p,int(links)

                           #links
            return links, 201



api.add_resource(linkGetter, '/link')
#api.add_resource(StoreList, '/stores')
#api.add_resource(Item, '/item/<string:name>')
#api.add_resource(ItemList, '/items')
#api.add_resource(UserRegister, '/register')











if __name__ == '__main__':
    app.run(port=5000, debug=True)
