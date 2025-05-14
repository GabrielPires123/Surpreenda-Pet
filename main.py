from flask import Flask, render_template, request, redirect, url_for,flash, session
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usuarios.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tarefas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(100), nullable=False)

class Tarefa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text)
    data_vencimento = db.Column(db.String(50))


@app.route("/")
def homepage():
    tarefas = Tarefa.query.all()
    return render_template("login.html", tarefas=tarefas)

@app.route("/cadastrar", methods=['GET', 'POST'])
def cadastropage():
    if request.method == 'POST':
        
        nova_tarefa = Tarefa(
            titulo=request.form['titulo'],
            descricao=request.form['descricao'],
            data_vencimento=request.form['data_vencimento']
        )
        
        
        db.session.add(nova_tarefa)
        db.session.commit()
        
        return redirect(url_for('homepage'))
    
    return render_template("cadastrar.html")

@app.route("/editar", methods=['GET', 'POST'])
def editarpage():
    if request.method == 'POST':
        
        if 'consultar' in request.form:
            
            id = request.form['id']
            tarefa = Tarefa.query.get(id)
            
            if not tarefa:
                return render_template('editar.html', error="Tarefa não encontrada!")
            
            return render_template('editar.html', tarefa=tarefa, mostrar_form=True)
            
        elif 'salvar' in request.form:
            
            id = request.form['id']
            tarefa = Tarefa.query.get(id)
            
            tarefa.titulo = request.form['titulo']
            tarefa.descricao = request.form['descricao']
            tarefa.data_vencimento = request.form['data_vencimento']
            db.session.commit()
            
            return redirect(url_for('homepage'))
    
    return render_template('editar.html')

@app.route("/excluir", methods=['GET', 'POST'])
def excluirpage():
    if request.method == 'POST':
        if 'consultar' in request.form:
            id = request.form['id']
            tarefa = Tarefa.query.get(id)
            
            if not tarefa:
                return render_template('excluir.html', error="Tarefa não encontrada!")
            
            id = request.form['id']
            tarefa = Tarefa.query.get(id)
        
            db.session.delete(tarefa)
            db.session.commit()
            return redirect(url_for('homepage'))
    
    return render_template('excluir.html')

# Cadastro login
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']

        if Usuario.query.filter_by(email=email).first():
            flash('E-mail já cadastrado!', 'error')
        else:
            novo_usuario = Usuario(nome=nome, email=email, senha=senha)
            db.session.add(novo_usuario)
            db.session.commit()
            flash('Cadastro realizado com sucesso!', 'success')
            return redirect(url_for('login'))

    return render_template('cadastro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and usuario.senha == senha:
            session['usuario_id'] = usuario.id
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('homepage'))
        else:
            flash('E-mail ou senha incorretos.', 'error')

    return render_template('login.html')

# Perfil com edição
@app.route('/perfil', methods=['GET', 'POST'])
def perfil():
    
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    usuario = db.session.get(Usuario, session['usuario_id'])

    if request.method == 'POST':
        novo_email = request.form['email']

        if novo_email != usuario.email and Usuario.query.filter_by(email=novo_email).first():
            flash('Este e-mail já está em uso!', 'error')
            return redirect(url_for('perfil'))

        usuario.nome = request.form['nome']
        usuario.email = novo_email
        nova_senha = request.form['senha']

        if nova_senha:
            usuario.senha = nova_senha

        db.session.commit()
        flash("Perfil atualizado com sucesso!", "success")
        return redirect(url_for('perfil'))

    return render_template('perfil.html', usuario=usuario)

# Logout
@app.route('/logout')
def logout():
    session.pop('usuario_id', None)
    flash("Você saiu da conta.", "success")
    return redirect(url_for('login'))

# Criar banco e rodar app
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)




