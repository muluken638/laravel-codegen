

from flask import Flask, render_template, request, redirect, url_for, flash

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
        enums=get_enums(database_id),
         get_enum_values=get_enum_values
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
        fields=fields,     # <-- Pass fields to template!
        enums=enums,
        guide=guide
    )
# Show enum values for a specific enum
@app.route("/enums/<int:enum_id>")
def view_enum(enum_id):
    conn = get_connection()
    enum_row = conn.execute("SELECT name, database_id FROM enums WHERE id=?", (enum_id,)).fetchone()
    conn.close()
    enum_name = enum_row[0]
    database_id = enum_row[1]
    values = get_enum_values(enum_id)
    return render_template(
        "enum_values.html",
        enum_id=enum_id,
        enum_name=enum_name,
        values=values,
        database_id=database_id
    )

@app.route("/enum_values/<int:enum_id>")
def enum_values(enum_id):
    conn = get_connection()
    row = conn.execute("SELECT name, database_id FROM enums WHERE id=?", (enum_id,)).fetchone()
    conn.close()

    values = get_enum_values(enum_id)
    return render_template("enum_values.html", enum_id=enum_id, enum_name=row[0], values=values, database_id=row[1])
# Add a new value to an enum
@app.route("/enums/<int:enum_id>/add-value", methods=["POST"])
def add_enum_value_route(enum_id):
    value = request.form["value"]
    add_enum_value(enum_id, value)
    return redirect(f"/enums/{enum_id}")


@app.route("/delete_table/<int:table_id>")
def delete_table(table_id):
    conn = get_connection()
    database_id = conn.execute("SELECT database_id FROM tables WHERE id=?", (table_id,)).fetchone()[0]
    conn.execute("DELETE FROM tables WHERE id = ?", (table_id,))
    conn.commit()
    conn.close()
    # Flash works like this in Flask
  
    flash("Table deleted successfully", category="success")
    return redirect(f"/tables/{database_id}")


@app.route("/delete_enum/<int:enum_id>")
def delete_enum(enum_id):
    conn = get_connection()
    database_id = conn.execute("SELECT database_id FROM enums WHERE id=?", (enum_id,)).fetchone()[0]
    conn.execute("DELETE FROM enums WHERE id = ?", (enum_id,))
    conn.commit()
    conn.close()
    flash("Enum deleted successfully", category="success")
    return redirect(f"/tables/{database_id}")

@app.route("/enums/<int:enum_id>/delete_value/<value>")
def delete_enum_value(enum_id, value):
    delete_enum_value(enum_id, value)  # You need this function in enum_service.py
    flash(f"Value '{value}' deleted", "success")
    return redirect(f"/enums/{enum_id}")
@app.route("/fields/<int:field_id>/delete", methods=["POST"])
def delete_field_route(field_id):
    delete_field(field_id)  # this is your DB function
    return redirect(request.referrer)
@app.route("/fields/<int:field_id>/edit", methods=["POST"])
def edit_field_route(field_id):

    name = request.form["name"]
    field_type = request.form["type"]
    nullable = 1 if request.form.get("nullable") else 0
    enum_id = request.form.get("enum_id")

    if field_type != "enum":
        enum_id = None

    update_field(
        field_id,
        name,
        field_type,
        nullable,
        int(enum_id) if enum_id else None
    )

    return redirect(request.referrer)

@app.route("/enums/<int:enum_id>/codegen")
def enum_codegen(enum_id):
    conn = get_connection()
    enum_row = conn.execute("SELECT name FROM enums WHERE id=?", (enum_id,)).fetchone()
    conn.close()

    enum_name = enum_row[0]
    values = get_enum_values(enum_id)

    class_name = ''.join(word.capitalize() for word in enum_name.split('_')) + "Enums"

    php_code = "<?php\n"
    php_code += f"//file: app/Enums/{class_name}.php\n\n"
    php_code += "namespace App\\Enums;\n\n"
    php_code += f"class {class_name}\n{{\n"
    for v in values:
        php_code += f"    public static ${v['name']} = {v['value']};\n"
    php_code += "\n    public static function toArray(): array\n    {\n"
    php_code += "        return [\n"
    for v in values:
        php_code += f"            {class_name}::${v['name']} => __('general.{v['name']}'),\n"
    php_code += "        ];\n"
    php_code += "    }\n"
    php_code += "}\n"

    return render_template("enum_codegen.html", php_code=php_code, enum_name=enum_name, enum_id=enum_id)


if __name__ == "__main__":
    app.run(debug=True)