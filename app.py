from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
import json

# Importações dos modelos
from models.Personagem import Personagem
from models.racas.Humano import Humano
from models.racas.Elfo import Elfo
from models.racas.Anao import Anao
from models.racas.Meio_Elfo import Meio_Elfo
from models.racas.Gnomo import Gnomo
from models.racas.Halfling import Halfling
from models.estilos.EstiloClassico import Estilo_Classico
from models.estilos.EstiloAventureiro import Estilo_Aventureiro
from models.estilos.EstiloHeroico import Estilo_Heroico
from models.classe.Mago import Mago
from models.classe.Ladrao import Ladrao
from models.classe.Druida import Druida

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'  # Altere para uma chave segura em produção

# Função para serializar objetos complexos
def serialize_obj(obj):
    if hasattr(obj, '__dict__'):
        return obj.__dict__
    return str(obj)

# Decorator para verificar se o usuário está logado
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        session['user'] = username
        return redirect(url_for('criar_personagem'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('personagem_data', None)
    session.pop('raca_data', None)
    session.pop('classe_data', None)
    return redirect(url_for('login'))

@app.route('/criar_personagem', methods=['GET', 'POST'])
@login_required
def criar_personagem():
    if request.method == 'POST':
        try:
            # Coletar dados do formulário
            nome = session['user']
            raca_opcao = request.form['raca']
            estilo_opcao = request.form['estilo']
            classe_opcao = request.form['classe']
            
            # Processar raça
            racas = {
                '1': Humano,
                '2': Elfo,
                '3': Anao,
                '4': Meio_Elfo,
                '5': Gnomo,
                '6': Halfling
            }
            
            raca_class = racas.get(raca_opcao, Humano)
            raca = raca_class()
            
            # Processar estilo
            estilos = {
                '1': Estilo_Classico,
                '2': Estilo_Aventureiro,
                '3': Estilo_Heroico
            }
            
            estilo_class = estilos.get(estilo_opcao, Estilo_Classico)
            personagem = estilo_class(nome, raca)
            
            if estilo_opcao in ['2', '3']:  # Aventureiro ou Heroico
                # Para estes estilos, precisamos processar a distribuição de atributos
                atributos = ['forca', 'destreza', 'constituicao', 'inteligencia', 'sabedoria', 'carisma']
                for attr in atributos:
                    personagem.atributos[attr] = int(request.form[attr])
                personagem.aplicar_bonus_raca()
            
            # Processar classe
            classes = {
                '1': Mago,
                '2': Ladrao,
                '3': Druida
            }
            
            classe_class = classes.get(classe_opcao, Mago)
            classe = classe_class()
            personagem.escolher_classe(classe)
            
            # Armazenar dados serializáveis na sessão
            session['personagem_data'] = {
                'nome': personagem.nome,
                'atributos': personagem.atributos
            }
            
            session['raca_data'] = {
                'nome': raca.nome,
                'movimento': raca.movimento,
                'infravisao': raca.infravisao,
                'alinhamento': raca.alinhamento,
                'habilidades': raca.habilidades,
                'modificadores': raca.modificadores
            }
            
            session['classe_data'] = {
                'nome': classe.nome,
                'dado_vida': classe.dado_vida,
                'habilidades': classe.habilidades,
                'nivel': classe.nivel,
                'pontos_de_vida': classe.pontos_de_vida
            }
            
            # Adicionar atributos específicos de classes
            if hasattr(classe, 'magias_conhecidas'):
                session['classe_data']['magias_conhecidas'] = classe.magias_conhecidas
            if hasattr(classe, 'magias_preparadas'):
                session['classe_data']['magias_preparadas'] = classe.magias_preparadas
            if hasattr(classe, 'bonus_ataque_furtivo'):
                session['classe_data']['bonus_ataque_furtivo'] = classe.bonus_ataque_furtivo
            if hasattr(classe, 'transformacoes'):
                session['classe_data']['transformacoes'] = classe.transformacoes
            if hasattr(classe, 'forma_max_dv'):
                session['classe_data']['forma_max_dv'] = classe.forma_max_dv
            
            return redirect(url_for('resultado'))
            
        except Exception as e:
            flash(f"Erro ao criar personagem: {str(e)}")
            return redirect(url_for('criar_personagem'))
    
    return render_template('personagem.html', username=session['user'])

@app.route('/resultado')
@login_required
def resultado():
    if 'personagem_data' not in session:
        return redirect(url_for('criar_personagem'))
    
    # Recuperar dados da sessão
    personagem_data = session.get('personagem_data', {})
    raca_data = session.get('raca_data', {})
    classe_data = session.get('classe_data', {})
    
    return render_template('resultado.html', 
                         personagem=personagem_data, 
                         raca=raca_data, 
                         classe=classe_data)

if __name__ == '__main__':
    app.run(debug=True)