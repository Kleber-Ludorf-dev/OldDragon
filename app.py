from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from functools import wraps
import json
import os
from datetime import datetime

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

# Arquivo onde os personagens serão salvos
ARQUIVO_PERSONAGENS = 'personagens.json'

# Decorator para verificar se o usuário está logado
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def carregar_personagens():
    """Carrega os personagens do arquivo JSON"""
    try:
        if os.path.exists(ARQUIVO_PERSONAGENS):
            with open(ARQUIVO_PERSONAGENS, 'r', encoding='utf-8') as f:
                conteudo = f.read().strip()
                if conteudo:
                    return json.loads(conteudo)
        return []
    except Exception as e:
        print(f"Erro ao carregar personagens: {e}")
        return []

def salvar_personagens(personagens):
    """Salva os personagens no arquivo JSON"""
    try:
        with open(ARQUIVO_PERSONAGENS, 'w', encoding='utf-8') as f:
            json.dump(personagens, f, ensure_ascii=False, indent=2)
        print(f"✅ Personagens salvos! Total: {len(personagens)}")
        return True
    except Exception as e:
        print(f"❌ Erro ao salvar personagens: {e}")
        return False

def salvar_personagem_simples(nome, raca_nome, classe_nome, atributos):
    """Salva um personagem de forma simples e direta"""
    try:
        print(f"🎯 Tentando salvar personagem: {nome}")
        
        # Carregar personagens existentes
        personagens = carregar_personagens()
        print(f"📁 Personagens existentes: {len(personagens)}")
        
        # Criar dados do personagem
        novo_personagem = {
            'nome': nome,
            'raca': raca_nome,
            'classe': classe_nome,
            'atributos': atributos,
            'nivel': 1,
            'data_criacao': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        print(f"📝 Dados do novo personagem: {novo_personagem}")
        
        # Adicionar à lista
        personagens.append(novo_personagem)
        
        # Salvar
        if salvar_personagens(personagens):
            print("✅ Personagem salvo com sucesso!")
            return True
        else:
            print("❌ Falha ao salvar personagem!")
            return False
            
    except Exception as e:
        print(f"💥 ERRO CRÍTICO: {e}")
        return False

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
            print("📝 Iniciando criação de personagem...")
            
            # Coletar dados do formulário
            nome = session['user']
            raca_opcao = request.form['raca']
            estilo_opcao = request.form['estilo']
            classe_opcao = request.form['classe']
            
            print(f"📋 Dados coletados: {nome}, raça:{raca_opcao}, estilo:{estilo_opcao}, classe:{classe_opcao}")
            
            # Mapeamento de raças
            racas_map = {
                '1': 'Humano',
                '2': 'Elfo', 
                '3': 'Anao',
                '4': 'Meio-Elfo',
                '5': 'Gnomo',
                '6': 'Halfling'
            }
            
            # Mapeamento de classes
            classes_map = {
                '1': 'Mago',
                '2': 'Ladrão',
                '3': 'Druida'
            }
            
            # Mapeamento de estilos
            estilos_map = {
                '1': 'Clássico',
                '2': 'Aventureiro', 
                '3': 'Heroico'
            }
            
            # Obter nomes
            raca_nome = racas_map.get(raca_opcao, 'Humano')
            classe_nome = classes_map.get(classe_opcao, 'Mago')
            estilo_nome = estilos_map.get(estilo_opcao, 'Clássico')
            
            # Atributos básicos (podemos ajustar conforme o estilo)
            atributos = {
                'forca': 10,
                'destreza': 10, 
                'constituicao': 10,
                'inteligencia': 10,
                'sabedoria': 10,
                'carisma': 10,
                'estilo': estilo_nome
            }
            
            # Ajustar atributos conforme estilo
            if estilo_opcao == '2':  # Aventureiro
                atributos = {
                    'forca': 12, 'destreza': 14, 'constituicao': 13,
                    'inteligencia': 10, 'sabedoria': 11, 'carisma': 10,
                    'estilo': estilo_nome
                }
            elif estilo_opcao == '3':  # Heroico
                atributos = {
                    'forca': 15, 'destreza': 13, 'constituicao': 14,
                    'inteligencia': 10, 'sabedoria': 12, 'carisma': 11,
                    'estilo': estilo_nome
                }
            
            print(f"🎯 Salvando personagem: {nome}, {raca_nome}, {classe_nome}")
            
            # SALVAR O PERSONAGEM - FORMA SIMPLES E DIRETA
            if salvar_personagem_simples(nome, raca_nome, classe_nome, atributos):
                flash("✅ Personagem criado e salvo com sucesso!")
            else:
                flash("❌ Erro ao salvar personagem!")
            
            # Armazenar dados na sessão para mostrar no resultado
            session['personagem_data'] = {
                'nome': nome,
                'atributos': atributos
            }
            
            session['raca_data'] = {
                'nome': raca_nome
            }
            
            session['classe_data'] = {
                'nome': classe_nome
            }
            
            return redirect(url_for('resultado'))
            
        except Exception as e:
            print(f"💥 ERRO na criação: {e}")
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

@app.route('/verificar_salvamento')
def verificar_salvamento():
    """Verifica se os personagens estão sendo salvos"""
    personagens = carregar_personagens()
    return jsonify({
        'total_personagens': len(personagens),
        'personagens': personagens,
        'arquivo': ARQUIVO_PERSONAGENS,
        'arquivo_existe': os.path.exists(ARQUIVO_PERSONAGENS)
    })

@app.route('/lista_personagens')
@login_required
def lista_personagens():
    """Mostra todos os personagens salvos"""
    personagens = carregar_personagens()
    return render_template('lista_personagens.html', personagens=personagens)

@app.route('/salvar_teste')
def salvar_teste():
    """Rota para testar o salvamento manualmente"""
    try:
        print("🧪 Testando salvamento...")
        
        # Dados de teste
        personagem_teste = {
            'nome': 'Personagem Teste',
            'raca': 'Humano', 
            'classe': 'Guerreiro',
            'atributos': {'forca': 15, 'destreza': 12, 'constituicao': 14},
            'nivel': 1,
            'data_criacao': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        personagens = carregar_personagens()
        print(f"📁 Personagens antes: {len(personagens)}")
        
        personagens.append(personagem_teste)
        
        if salvar_personagens(personagens):
            return "✅ Personagem teste salvo com sucesso! Verifique /verificar_salvamento"
        else:
            return "❌ Erro ao salvar personagem teste!"
            
    except Exception as e:
        return f"Erro: {str(e)}"

@app.route('/debug_arquivo')
def debug_arquivo():
    """Debug completo do arquivo"""
    try:
        info = {
            'arquivo': ARQUIVO_PERSONAGENS,
            'existe': os.path.exists(ARQUIVO_PERSONAGENS),
            'pasta_atual': os.getcwd(),
            'conteudo_pasta': os.listdir('.')
        }
        
        if info['existe']:
            with open(ARQUIVO_PERSONAGENS, 'r', encoding='utf-8') as f:
                conteudo = f.read()
                info['conteudo'] = conteudo
                info['tamanho'] = len(conteudo)
        
        return jsonify(info)
    except Exception as e:
        return f"Erro no debug: {str(e)}"

@app.route('/limpar_personagens')
def limpar_personagens():
    """Limpa todos os personagens (apenas para teste)"""
    try:
        with open(ARQUIVO_PERSONAGENS, 'w', encoding='utf-8') as f:
            json.dump([], f)
        return "✅ Personagens limpos!"
    except Exception as e:
        return f"Erro: {str(e)}"

if __name__ == '__main__':
    # Cria arquivo vazio se não existir
    if not os.path.exists(ARQUIVO_PERSONAGENS):
        with open(ARQUIVO_PERSONAGENS, 'w', encoding='utf-8') as f:
            json.dump([], f)
        print("📄 Arquivo personagens.json criado!")
    
    print("🚀 Servidor iniciando...")
    print("📍 URLs para testar:")
    print("   http://localhost:5000/criar_personagem")
    print("   http://localhost:5000/verificar_salvamento")
    print("   http://localhost:5000/salvar_teste")
    print("   http://localhost:5000/debug_arquivo")
    
    app.run(debug=True, host='0.0.0.0', port=5000)