from flask import render_template, session, redirect, url_for, current_app
from .. import db
from ..models import User, Role
from ..email import send_email, send_simple_message
from . import main
from .forms import NameForm, MudarNome
from flask import request, flash


@main.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    forms_editar=MudarNome()
    users=User.query.all()

    delete_id=request.args.get('delete')
    if delete_id:
        user=User.query.get(delete_id)
        if user:
            db.session.delete(user)
            db.session.commit()
            flash('Usuário deletado com sucesso')
            return redirect(url_for('.index'))

    edit=request.args.get('edit',type=int)
    if forms_editar.validate_on_submit() and edit:
        user=User.query.get(edit)
        if user:
            user.username = forms_editar.novo_nome.data
            db.session.commit()
            flash('Nome do usuário atualizado com sucesso')
        return redirect(url_for('.index'))

    if form.validate_on_submit():

        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user_role=Role.query.filter_by(name="User").first()
            user = User(username=form.name.data, role=user_role)
            db.session.add(user)
            db.session.commit()
            session['known'] = False
            print('FLASKY_ADMIN: ' + str(current_app.config['FLASKY_ADMIN']), flush=True)
            if current_app.config['FLASKY_ADMIN']:
                #send_email(current_app.config['FLASKY_ADMIN'], 'New User', 'mail/new_user', user=user)
                print('Enviando mensagem...', flush=True)
                send_simple_message([current_app.config['FLASKY_ADMIN'], "flaskaulasweb@zohomail.com", form.email.data], 'Novo usuário', form.name.data)
                print('Mensagem enviada...', flush=True)
        else:
            session['known'] = True
        session['name'] = form.name.data
        return redirect(url_for('.index'))
    return render_template('index.html',
                           form=form, name=session.get('name'), form_editar=forms_editar, edit_id=edit,
                           known=session.get('known', False), users=users)
