from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///to_do.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
Bootstrap(app)
db = SQLAlchemy(app)

TICK_EMOJI = "✔️"

def get_to_do_headers():
    strSQL = "SELECT p.[name] as [column_name] FROM sqlite_master AS m " \
             "INNER JOIN pragma_table_info(m.[name]) AS p " \
             "WHERE m.[name] = 'to_do' " \
             "ORDER BY p.[cid]"
    return [row[0] for row in db.engine.execute(strSQL)]

def get_to_do_bool_headers():
    strSQL = "SELECT p.[name] as [column_name] FROM sqlite_master AS m " \
             "INNER JOIN pragma_table_info(m.[name]) AS p " \
             "WHERE m.[name] = 'to_do' and p.[type]='BOOLEAN' " \
             "ORDER BY p.cid"
    return [row[0] for row in db.engine.execute(strSQL)]

class to_do(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    entry = db.Column(db.String(500), unique=False, nullable=False)
    log_date = db.Column(db.DateTime, unique=False, nullable=False)
    completed_flag = db.Column(db.Boolean, unique=False, nullable=True)
    completed_date = db.Column(db.DateTime, unique=False, nullable=True)

    def get_data(self):
        return {field: value for (field, value) in self.__dict__.items() if field != "_sa_instance_state"}

class AddItemForm(FlaskForm):
    entry = StringField("Entry", validators=[DataRequired()])
    submit = SubmitField("Add Item")

# all Flask routes below
@app.route("/")
def home():
    return render_template("index.html")


@app.route('/todo', methods=["GET", "POST"])
def ToDo():
    # Outstanding Tasks
    outstanding_data_q = to_do.query.filter_by(completed_flag=False).order_by(to_do.id).all()
    to_do_headers = get_to_do_headers()
    bool_headers = get_to_do_bool_headers()
    # Completed Tasks
    completed_data_q = to_do.query.filter_by(completed_flag=True).order_by(to_do.id).all()
    # print(to_do_headers)
    outstanding_data = []
    for item_x in outstanding_data_q:
        outstanding_data.append(item_x.get_data())
    completed_data = []
    for item_x in completed_data_q:
        completed_data.append(item_x.get_data())
    # print(outstanding_data)
    # Replace boolean fields with yes/no
    for item_x in outstanding_data:
        for field in bool_headers:
            if item_x[field]:
                item_x[field] = TICK_EMOJI
            else:
                item_x[field] = ""
    for item_x in completed_data:
        for field in bool_headers:
            if item_x[field]:
                item_x[field] = TICK_EMOJI
            else:
                item_x[field] = ""

    return render_template('to_do_list.html', outstanding_data=outstanding_data, completed_data=completed_data, headers=to_do_headers)

@app.route("/add", methods=["GET","POST"])
def add():
    form = AddItemForm()
    if form.validate_on_submit():
        entry = form.entry.data
        log_date = datetime.datetime.now()
        completed_flag = False
        new_item = to_do(entry=entry, log_date=log_date, completed_flag=completed_flag)
        db.session.add(new_item)
        db.session.commit()
        return redirect(url_for("ToDo"))
    return render_template("add.html", form=form)

def toggle_completed_flag(id):
    item_to_update = to_do.query.get(id)
    item_to_update.completed_flag = not item_to_update.completed_flag
    if item_to_update.completed_flag:
        item_to_update.completed_date = datetime.datetime.now()
    else:
        item_to_update.completed_date = None
    db.session.commit()

@app.route("/update/<id>", methods=["GET","POST"])
def update(id):
    print("Got this far")
    toggle_completed_flag(id)
    return redirect(url_for("ToDo"))


if __name__ == '__main__':
    app.run(debug=True)

