from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from validate_docbr import CNPJ
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from dotenv import load_dotenv
import os

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///companies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your_fallback_jwt_secret_key')  # Use a chave padrão se não estiver definida no .env
jwt = JWTManager(app)
db = SQLAlchemy(app)


# Definindo o modelo de dados da empresa
class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cnpj = db.Column(db.String(14), unique=True, nullable=False)
    razao_social = db.Column(db.String(100), nullable=False)
    nome_fantasia = db.Column(db.String(100), nullable=False)
    cnae = db.Column(db.String(10), nullable=False)

    def __init__(self, cnpj, razao_social, nome_fantasia, cnae):
        self.cnpj = self.clean_cnpj(cnpj)
        self.razao_social = razao_social
        self.nome_fantasia = nome_fantasia
        self.cnae = self.clean_cnae(cnae)
        self.validate_cnpj()
        
    def validate_cnpj(self):
        if not CNPJ().validate(self.cnpj):
            raise ValueError('CNPJ inválido')

    @staticmethod
    def clean_cnpj(cnpj):
        # Remove pontuação e caracteres não numéricos
        return ''.join(filter(str.isdigit, cnpj))

    @staticmethod
    def clean_cnae(cnae):
        # Remove pontuação e caracteres não numéricos
        return ''.join(filter(str.isdigit, cnae))
    def format_cnpj(self):
        # Formata o CNPJ com pontuações
        return f'{self.cnpj[:2]}.{self.cnpj[2:5]}.{self.cnpj[5:8]}/{self.cnpj[8:12]}-{self.cnpj[12:]}'

    def format_cnae(self):
        # Formata o CNAE com pontuações
        return f'{self.cnae[:4]}-{self.cnae[4:]}'
    
    def as_dict(self):
        # Retorna um dicionário com os campos formatados
        return {
            'cnpj': self.format_cnpj(),
            'razao_social': self.razao_social,
            'nome_fantasia': self.nome_fantasia,
            'cnae': self.format_cnae()
        }


# Rotas CRUD

# Rota para cadastrar uma nova empresa
@app.route('/companies', methods=['POST'])
@jwt_required()
def create_company():
    try:
        data = request.get_json()

        new_company = Company(
            cnpj=data['cnpj'],
            razao_social=data['razao_social'],
            nome_fantasia=data['nome_fantasia'],
            cnae=data['cnae']
        )

        db.session.add(new_company)
        db.session.commit()

        return jsonify({'message': 'Company created successfully'}), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400  # HTTP 400 Bad Request

# Rota para editar uma empresa existente
@app.route('/companies/<cnpj>', methods=['PUT'])
@jwt_required()
def update_company(cnpj):

    print("[CNPJ]: ", cnpj)
    company = Company.query.filter_by(cnpj=cnpj).first()

    if not company:
        return jsonify({'error': 'Company not found'}), 404

    data = request.get_json()

    company.nome_fantasia = data.get('nome_fantasia', company.nome_fantasia)
    company.cnae = data.get('cnae', company.cnae)

    db.session.commit()

    return jsonify({'message': 'Company updated successfully'}), 200

# Rota para remover uma empresa existente
@app.route('/companies/<cnpj>', methods=['DELETE'])
@jwt_required()
def delete_company(cnpj):
    company = Company.query.filter_by(cnpj=cnpj).first()

    if not company:
        return jsonify({'error': 'Company not found'}), 404

    db.session.delete(company)
    db.session.commit()

    return jsonify({'message': 'Company deleted successfully'}), 200


# Rota para consultar uma empresa por CNPJ
@app.route('/companies/<cnpj>', methods=['GET'])
@jwt_required()
def get_company_by_cnpj(cnpj):
    try:
        company = Company.query.filter_by(cnpj=cnpj).first()

        if not company:
            return jsonify({'error': 'Company not found'}), 404

        company_data = company.as_dict()

        return jsonify({'company': company_data}), 200
    except Exception as e:
        return jsonify({'error': f'Failed to get company. Error: {str(e)}'}), 500


# Rota para listar empresas com suporte a paginação, ordenação e limite de registros por página
@app.route('/companies', methods=['GET'])
@jwt_required()
def list_companies():
    page = int(request.args.get('start', 1))
    limit = int(request.args.get('limit', 10))
    sort_by = request.args.get('sort', 'id')
    sort_dir = request.args.get('dir', 'asc')

    companies = Company.query.order_by(
        getattr(Company, sort_by).asc() if sort_dir == 'asc' else getattr(
            Company, sort_by).desc()
    ).paginate(page=page, per_page=limit, error_out=False)

    companies_list = [company.as_dict() for company in companies.items]

    return jsonify({'companies': companies_list, 'total_pages': companies.pages}), 200


# Rota para autenticação e obtenção do token JWT
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    # Aqui você verificará as credenciais do usuário, comparando com um banco de dados ou outras fontes
    if data['username'] == os.getenv('USERNAME_API') and data['password'] == os.getenv('PASSWORD_API'):
        access_token = create_access_token(identity=data['username'])
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({'error': 'Invalid credentials'}), 401
    

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
    
    
    
    
    
    

