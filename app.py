from flask import Flask, render_template, request, redirect
from database.database import init_db, get_connection
from database.database_service import *
from database.table_service import *
from database.field_service import *
from database.enum_service import *
from generator.laravel_generator import LaravelGenerator

app = Flask(__name__)

init_db()  # Initialize DB

generator = LaravelGenerator()


@app.route("/")
def databases():
    return render_template(
        "databases.html",
        databases=get_databases()
    )


@app.route("/create_database", methods=["POST"])
def create_database_route():
    create_database(request.form["name"])
    return redirect("/")


@app.route("/tables/<int:database_id>")
def tables(database_id):
    return render_template(
        "tables.html",
        database_id=database_id,
        tables=get_tables(database_id),
        enums=get_enums(database_id)
    )


@app.route("/create_table", methods=["POST"])
def create_table_route():
    create_table(
        request.form["database_id"],
        request.form["name"]
    )
    return redirect(f"/tables/{request.form['database_id']}")


@app.route("/create_enum", methods=["POST"])
def create_enum_route():
    create_enum(
        request.form["database_id"],
        request.form["name"]
    )
    return redirect(f"/tables/{request.form['database_id']}")


@app.route("/add_field", methods=["POST"])
def add_field():
    nullable = 1 if request.form.get("nullable") else 0
    enum_id = request.form.get("enum_id")

    if request.form["type"] != "enum":
        enum_id = None

    create_field(
        int(request.form["table_id"]),
        request.form["name"],
        request.form["type"],
        nullable,
        int(enum_id) if enum_id else None
    )

    return redirect(f"/codegen/{request.form['table_id']}")


@app.route("/codegen/<int:table_id>")
def codegen(table_id):
    fields = get_fields(table_id)

    conn = get_connection()
    table_row = conn.execute(
        "SELECT name, database_id FROM tables WHERE id=?",
        (table_id,)
    ).fetchone()
    conn.close()

    table_name = table_row[0]
    database_id = table_row[1]

    enums = get_enums(database_id)

    # Generate code
    migration = generator.generate_migration(table_name, fields)
    model = generator.generate_model(table_name, fields)
    controller = generator.generate_controller(table_name)
    route = generator.generate_route(table_name)

    # Generate dynamic guide
    table_snake = generator.to_table_name_snake(table_name)
    model_name = generator.to_model_name(table_name)
    controller_name = model_name + "Controller"

    guide = f"""// Note: It is recommended you copy this guide and follow it side by side with the tool

1. Create Database / Migration
- cd app-folder
- php artisan make:migration create_{table_snake}_table --create={table_snake}
- Apply the generated migration code
- php artisan migrate

2. Add Model
- php artisan make:model {model_name}
- Apply the generated model code

3. Add Controller
- php artisan make:controller {controller_name} --resource
- Apply the generated controller code

4. Add Route
- Apply the generated route code
"""

    return render_template(
        "codegen.html",
        migration=migration,
        model=model,
        controller=controller,
        route=route,
        table_id=table_id,
        enums=enums,
        guide=guide
    )

if __name__ == "__main__":
    app.run(debug=True)