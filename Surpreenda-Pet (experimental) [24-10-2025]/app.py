from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce_pet.db'
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

class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    preco = db.Column(db.Float, nullable=False)
    estoque = db.Column(db.Integer, nullable=False, default=0)
    imagem = db.Column(db.String(200))
    categoria = db.Column(db.String(50))

class Carrinho(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    finalizado = db.Column(db.Boolean, default=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    itens = db.relationship('ItemCarrinho', backref='carrinho', lazy=True)

class ItemCarrinho(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    carrinho_id = db.Column(db.Integer, db.ForeignKey('carrinho.id'), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey('produto.id'), nullable=False)
    quantidade = db.Column(db.Integer, default=1)
    
    produto = db.relationship('Produto', backref='carrinhos')

class Pedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    data_pedido = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Pendente')
    total = db.Column(db.Float, nullable=False)
    
    itens = db.relationship('ItemPedido', backref='pedido', lazy=True)

class ItemPedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedido.id'), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey('produto.id'), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    preco_unitario = db.Column(db.Float, nullable=False)

@app.route('/')
def index():
    produtos = Produto.query.limit(4).all()
    return render_template('index.html', produtos=produtos)

    produto = Produto.query.get_or_404(id)
    return render_template('detalhes_produto.html', produto=produto)

@app.route('/ajuda')
def ajuda():
    return render_template('ajuda.html')





@app.route('/adicionar_carrinho', methods=['POST'])
def adicionar_carrinho():
    if 'usuario_id' not in session:
        flash('Faça login para adicionar produtos ao carrinho', 'error')
        return redirect(url_for('login'))
    
    produto_id = request.form.get('produto_id')
    quantidade = int(request.form.get('quantidade', 1))
    
    produto = Produto.query.get(produto_id)
    if not produto:
        flash('Produto não encontrado', 'error')
        return redirect(url_for('produtos'))
    
    # Busca carrinho ativo
    carrinho = Carrinho.query.filter_by(
        usuario_id=session['usuario_id'],
        finalizado=False
    ).first()
    
    # Cria novo carrinho se não existir
    if not carrinho:
        carrinho = Carrinho(usuario_id=session['usuario_id'])
        db.session.add(carrinho)
        db.session.commit()
    
    # Verifica se produto já está no carrinho
    item = ItemCarrinho.query.filter_by(
        carrinho_id=carrinho.id,
        produto_id=produto_id
    ).first()
    
    if item:
        item.quantidade += quantidade
    else:
        item = ItemCarrinho(
            carrinho_id=carrinho.id,
            produto_id=produto_id,
            quantidade=quantidade
        )
        db.session.add(item)
    
    db.session.commit()
    flash(f'{produto.nome} adicionado ao carrinho!', 'success')
    return redirect(url_for('carrinho'))

@app.route('/carrinho')
def carrinho():
    if 'usuario_id' not in session:
        flash('Faça login para acessar seu carrinho', 'error')
        return redirect(url_for('login'))
    
    # Lógica do carrinho (igual ao seu código anterior)
    carrinho = Carrinho.query.filter_by(
        usuario_id=session['usuario_id'],
        finalizado=False
    ).first()
    
    itens = []
    total = 0
    
    if carrinho:
        for item in carrinho.itens:
            subtotal = item.produto.preco * item.quantidade
            total += subtotal
            itens.append({
                'id': item.id,
                'produto': item.produto,
                'quantidade': item.quantidade,
                'subtotal': subtotal
            })
    
    return render_template('carrinho.html', itens=itens, total=total)

@app.route('/produtos')
def produtos():
    categoria = request.args.get('categoria')
    if categoria:
        produtos = Produto.query.filter_by(categoria=categoria).all()
    else:
        produtos = Produto.query.all()
    return render_template('produto.html', produtos=produtos)

@app.route('/produto/<int:id>')
def produto_detalhes(id):
    produto = Produto.query.get_or_404(id)
    return render_template('detalhes_produto.html', produto=produto)


@app.route('/remover_item/<int:item_id>')
def remover_item(item_id):
    if 'usuario_id' not in session:
        flash('Faça login para gerenciar seu carrinho', 'error')
        return redirect(url_for('login'))
    
    item = ItemCarrinho.query.get(item_id)
    if not item:
        flash('Item não encontrado', 'error')
        return redirect(url_for('carrinho'))
    
    db.session.delete(item)
    db.session.commit()
    flash('Item removido do carrinho', 'success')
    return redirect(url_for('carrinho'))

@app.route('/finalizar_pedido')
def finalizar_pedido():
    if 'usuario_id' not in session:
        flash('Faça login para finalizar seu pedido', 'error')
        return redirect(url_for('login'))
    
    carrinho = Carrinho.query.filter_by(
        usuario_id=session['usuario_id'],
        finalizado=False
    ).first()
    
    if not carrinho or not carrinho.itens:
        flash('Seu carrinho está vazio', 'error')
        return redirect(url_for('carrinho'))
    
    # Calcula total e verifica estoque
    total = 0
    for item in carrinho.itens:
        if item.produto.estoque < item.quantidade:
            flash(f'Estoque insuficiente para {item.produto.nome}', 'error')
            return redirect(url_for('carrinho'))
        total += item.produto.preco * item.quantidade
    
    # Cria pedido
    pedido = Pedido(
        usuario_id=session['usuario_id'],
        total=total
    )
    db.session.add(pedido)
    db.session.flush()  # Gera ID para o pedido
    
    # Adiciona itens ao pedido e atualiza estoque
    for item in carrinho.itens:
        produto = Produto.query.get(item.produto_id)
        produto.estoque -= item.quantidade
        
        item_pedido = ItemPedido(
            pedido_id=pedido.id,
            produto_id=produto.id,
            quantidade=item.quantidade,
            preco_unitario=produto.preco
        )
        db.session.add(item_pedido)
    
    # Finaliza carrinho
    carrinho.finalizado = True
    db.session.commit()
    
    flash('Pedido realizado com sucesso!', 'success')
    return redirect(url_for('meus_pedidos'))

@app.route('/meus_pedidos')
def meus_pedidos():
    if 'usuario_id' not in session:
        flash('Faça login para ver seus pedidos', 'error')
        return redirect(url_for('login'))
    
    pedidos = Pedido.query.filter_by(usuario_id=session['usuario_id']).order_by(Pedido.data_pedido.desc()).all()
    return render_template('pedidos.html', pedidos=pedidos)

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
            return redirect(url_for('perfil'))
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

# Criar banco e dados iniciais
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Adicionar produtos iniciais
        if Produto.query.count() == 0:
            produtos = [
                Produto(
                    nome="Ração Premium para Cães",
                    descricao="Ração super premium para cães adultos",
                    preco=120.90,
                    estoque=50,
                    categoria="Alimentos",
                    imagem="racao_caes.jpg"
                ),
                Produto(
                    nome="Brinquedo Pelúcia",
                    descricao="Brinquedo de pelúcia para gatos",
                    preco=25.50,
                    estoque=30,
                    categoria="Brinquedos",
                    imagem="brinquedo_gato.jpg"
                ),
                Produto(
                    nome="Coleira Antipulgas",
                    descricao="Coleira com proteção contra pulgas e carrapatos",
                    preco=45.00,
                    estoque=20,
                    categoria="Acessórios",
                    imagem="coleira.jpg"
                ),
                Produto(
                    nome="Areia Sanitária",
                    descricao="Areia aglomerante para gatos",
                    preco=35.75,
                    estoque=40,
                    categoria="Higiene",
                    imagem="areia_gato.jpg"
                )
            ]
            db.session.add_all(produtos)
            db.session.commit()
    app.run(debug=True)