from flask import Flask, render_template, flash, redirect, url_for, request, jsonify
from flask_bootstrap import Bootstrap
from flask_nav import Nav
from flask_nav.elements import Navbar, View, Subgroup
from entity.entities import Node, Type

from forms import EditNodeForm, EditTypeForm

################################
################################
nodes = []
u_nodes = []
c_nodes = []
types = []

for i in range(10):
    nodes.append(Node())
    u_nodes.append(Node(ip=f"1.0.0.{i}"))
    c_nodes.append(Node(ip=f"2.0.0.{i}"))
    types.append(Type())

PORT = 5000

################################
################################

app = Flask("client-web")
app.secret_key = "4dbae3052d7e8b16ebcfe8752f70a4efe68d2ae0558b4a1b25c5fd902284e52e"

Bootstrap(app)
nav = Nav(app)

nav.register_element('my_navbar', Navbar('Navigation Bar',
                                         View('Home', 'home'),
                                         Subgroup("Nodes", View('View Nodes', 'view_nodes'),
                                                  View('Edit / Insert', 'edit_nodes')),
                                         Subgroup("Types", View('View Types', 'view_types'),
                                                  View('Edit / Insert', 'edit_types')),
                                         ))


@app.route("/")
@app.route("/home/", methods=['GET', 'POST'])
def home():
    return render_template("index.html", configured_nodes=c_nodes, unconfigured_nodes=u_nodes)


@app.route("/view_nodes/", methods=['GET', 'POST'])
def view_nodes():
    if request.method == 'POST':
        node_ip = request.form.get('node_ip')
        print(f'{node_ip}')
        if node_ip:
            return redirect(url_for("edit_nodes", node=Node(ip=node_ip)))

    return render_template("view_nodes.html", nodes=nodes)


@app.route("/edit_nodes/", methods=['GET', 'POST'])
@app.route("/edit_nodes/<node>/", methods=['GET', 'POST'])
def edit_nodes(node=None):

    edit_nodes_form = EditNodeForm(obj=types)
    edit_nodes_form.type.choices = [(t.name, f"{t.name}\t{t.repoUrl}") for t in types]

    print(f'{node}')
    if request.method == 'POST':
        if edit_nodes_form.validate_on_submit():
            flash(f"Successfully edited node {edit_nodes_form.ip_address.data} {edit_nodes_form.name.data}!", "success")
            print('view nodes')
            return redirect(url_for("view_nodes"))

    return render_template("edit_node.html", node=node, form=edit_nodes_form)


@app.route("/view_types/", methods=['GET', 'POST'])
def view_types():
    return render_template("view_types.html", types=types)


@app.route("/edit_types/", methods=['GET', 'POST'])
def edit_types():
    edit_types_form = EditTypeForm()
    return render_template("edit_type.html", type=None, form=edit_types_form)


if __name__ == "__main__":
    app.run(debug=True, use_reloader=True, port=PORT)
