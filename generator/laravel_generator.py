from database.enum_service import get_enum_values


class LaravelGenerator:

    # Convert table name to ModelName
    def to_model_name(self, table):

        return "".join(
            word.capitalize()
            for word in table.split("_")
        )


    # Generate Migration
    def generate_migration(self, table, fields):
        table_snake = self.to_table_name_snake(table)
        code = "            $table->id();\n"

        for f in fields:

            name = f[1]
            type_ = f[2]
            nullable = f[3]
            enum_id = f[4]

            field_line = ""

            if type_ == "string":
                field_line = f"$table->string('{name}')"

            elif type_ == "integer":
                field_line = f"$table->integer('{name}')"

            elif type_ == "bigInteger":
                field_line = f"$table->bigInteger('{name}')"

            elif type_ == "text":
                field_line = f"$table->text('{name}')"

            elif type_ == "boolean":
                field_line = f"$table->boolean('{name}')"

            elif type_ == "date":
                field_line = f"$table->date('{name}')"

            elif type_ == "datetime":
                field_line = f"$table->dateTime('{name}')"

            elif type_ == "timestamp":
                field_line = f"$table->timestamp('{name}')"

            elif type_ == "float":
                field_line = f"$table->float('{name}')"

            elif type_ == "double":
                field_line = f"$table->double('{name}')"

            elif type_ == "json":
                field_line = f"$table->json('{name}')"

            elif type_ == "enum":

                values = get_enum_values(enum_id)

                if values:
                    enum_values = ",".join(
                        [f"'{v['name']}'" for v in values]
                    )
                    field_line = f"$table->enum('{name}', [{enum_values}])"
                else:
                    field_line = f"$table->string('{name}')"

            else:
                field_line = f"$table->string('{name}')"


            # Nullable support
            if nullable:
                field_line += "->nullable()"

            field_line += ";"

            code += f"            {field_line}\n"


        migration = f"""<?php

use Illuminate\\Database\\Migrations\\Migration;
use Illuminate\\Database\\Schema\\Blueprint;
use Illuminate\\Support\\Facades\\Schema;

return new class extends Migration
{{
    public function up(): void
    {{
        Schema::create('{table_snake}', function (Blueprint $table) {{
{code}
            $table->timestamps();
        }});
    }}

    public function down(): void
    {{
        Schema::dropIfExists('{table_snake}');
    }}
}};
"""

        return migration


    # Generate Model
    def generate_model(self, table, fields):

        model = self.to_model_name(table)
        table_snake= self.to_table_name_snake(table)
        fillable = ",\n        ".join(
            [f"'{f[1]}'" for f in fields]
        )

        model_code = f"""<?php

namespace App\\Models;

use Illuminate\\Database\\Eloquent\\Model;

class {model} extends Model
{{
    protected $table = '{table_snake}';

    protected $fillable = [
        {fillable}
    ];
}}
"""

        return model_code


    # Generate Controller
    def generate_controller(self, table):

        model = self.to_model_name(table)

        controller = f"""<?php

namespace App\\Http\\Controllers;

use App\\Models\\{model};
use Illuminate\\Http\\Request;

class {model}Controller extends Controller
{{

    public function index()
    {{
        return response()->json({model}::all());
    }}

    public function store(Request $request)
    {{
        $data = $request->validate([]);

        $record = {model}::create($data);

        return response()->json($record);
    }}

    public function show($id)
    {{
        return response()->json(
            {model}::findOrFail($id)
        );
    }}

    public function update(Request $request, $id)
    {{
        $record = {model}::findOrFail($id);

        $record->update($request->all());

        return response()->json($record);
    }}

    public function destroy($id)
    {{
        {model}::destroy($id);

        return response()->json(['message'=>'Deleted']);
    }}

}}
"""

        return controller


    # Generate Route
    def generate_route(self, table):
        table_snake= self.to_table_name_snake(table)
        model = self.to_model_name(table)

        route = f"""use App\\Http\\Controllers\\{model}Controller;

Route::resource('{table_snake}', {model}Controller::class);
"""

        return route

    #Generate Facade
    def generate_facade(self, table):

        model = self.to_model_name(table)

        facade = f"""<?php
namespace App\\Facades;

use Illuminate\\Support\\Facades\\Facade;

class {model}Facade extends Facade
{{
    protected static function getFacadeAccessor()
    {{
        return '{model}';
    }}
}}
"""

        return facade
    
#Generate Text Translation




    # Generate API Route
    def generate_api_route(self, table):

        model = self.to_model_name(table)

        route = f"""use App\\Http\\Controllers\\{model}Controller;

Route::apiResource('{table}', {model}Controller::class);
"""

        return route

    @staticmethod
    def to_model_name(table_name):
        # "sales manager" → "SalesManager"
        return "".join(word.capitalize() for word in table_name.strip().split())

    @staticmethod
    def to_table_name_snake(table_name):
        # "Sales Manager" → "sales_manager"
        return "_".join(table_name.strip().lower().split())
    