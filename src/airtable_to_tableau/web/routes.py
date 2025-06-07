import os
import json
import re
import subprocess
from flask import Blueprint, Response, stream_with_context, render_template, send_from_directory, request, redirect, url_for, flash

from airtable_to_tableau.libs.read_hyper import read_hyper_to_dataframe
from airtable_to_tableau.libs.table_name import get_table_name_for_file
from airtable_to_tableau.libs.file_stats import get_file_stats
from airtable_to_tableau.libs.airtable_metadata import get_airtable_metadata
from airtable_to_tableau.libs.type_to_json import airtable_type_to_json_type

routes = Blueprint("routes", __name__)

# 📁 Folder paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", ".."))
HYPER_DIR = os.path.join(ROOT_DIR, "output")
CONFIG_DIR = os.path.join(ROOT_DIR, "configs")

# View Home
@routes.route("/")
def index():
    config_files = [f for f in os.listdir(CONFIG_DIR) if f.endswith(".json")]

    return render_template("index.html", config_files=config_files)

@routes.route("/view/<filename>")
def view_hyper(filename):
    config_file = request.args.get("config")
    profile = request.args.get("profile")

    file_path = os.path.join(HYPER_DIR, filename)

    # Default table name if not found
    table_name = "Building"

    # If config and profile are provided, try to load the correct table name
    if config_file and profile:
        config_path = os.path.join(CONFIG_DIR, config_file)
        if not os.path.exists(config_path):
            flash(f"Config file '{config_file}' not found.", "danger")
            return redirect(url_for("routes.index"))

        try:
            with open(config_path, "r") as f:
                config = json.load(f)
        except json.JSONDecodeError:
            flash("Invalid config file format.", "danger")
            return redirect(url_for("routes.index"))

        profile_data = config.get("profiles", {}).get(profile)
        if not profile_data:
            flash(f"Profile '{profile}' not found in config.", "danger")
            return redirect(url_for("routes.index"))

        tables = profile_data.get("tables", [])
        if tables:
            table_name = tables[0].get("table_name", table_name)

    # Ensure the hyper file exists
    if not os.path.exists(file_path):
        flash("Hyper file not found.", "danger")
        return redirect(url_for("routes.index"))

    # Read the dataframe from the hyper file
    df = read_hyper_to_dataframe(file_path, table_name=table_name)
    if df is None:
        flash(f"Failed to read Hyper file for table: {table_name}", "danger")
        return redirect(url_for("routes.index"))

    # Pagination setup
    page = int(request.args.get("page", 1))
    per_page = 20
    total_pages = (len(df) + per_page - 1) // per_page
    start = (page - 1) * per_page
    end = start + per_page
    paginated_df = df.iloc[start:end]

    # File info and HTML rendering
    file_info = get_file_stats(file_path, project_root=os.getcwd())
    table_html = paginated_df.to_html(classes="table table-striped", index=False)

    return render_template(
        "view_hyper.html",
        filename=filename,
        file_info=file_info,
        table=table_html,
        page=page,
        total_pages=total_pages,
        total_rows=len(df),
        displayed_rows=len(paginated_df),
        config_file=config_file,
        table_name=table_name
    )

# View Config file list
@routes.route("/configs")
def list_configs():
    config_files = []
    for f in os.listdir(CONFIG_DIR):
        if f.endswith(".json"):
            full_path = os.path.join(CONFIG_DIR, f)
            config_files.append({
                "name": f,
                "path": full_path
            })

    return render_template("config_list.html", config_files=config_files)

# View a config file
@routes.route("/configs/view/<filename>")
def view_config(filename):
    # print(f"🚀 Viewing config: {filename}")
    config_path = os.path.join(CONFIG_DIR, filename)

    if not os.path.exists(config_path):
        flash("Config file not found.", "danger")
        return redirect(url_for("routes.list_configs"))


    with open(config_path, "r") as f:
        full_config = json.load(f)  # Load as Python dict
        config_contents = json.dumps(full_config, indent=2)  # Pretty-print for UI

    # Get file stats
    file_info = get_file_stats(config_path, ROOT_DIR, relative_path_prefix="configs")

    # Generate CLI commands for each profile
    profiles = full_config.get("profiles", {})
    
    # Generate CLI commands for each profile as a dictionary
    cli_commands = {
    profile: {
        "cmd": f"airtable-export export --config configs/{filename} --profile {profile}",
        "output_file": table.get("output_file"),
        "table_name": table.get("table_name"),
    }
    for profile, profile_data in full_config.get("profiles", {}).items()
    for table in profile_data.get("tables", [])
}

    # Pull Airtable metadata for all tables in the default profile
    default_profile = full_config.get("profiles", {}).get("default", {})
    tables = default_profile.get("tables", [])
    metadata = []

    # Loop though tables
    for table in tables:
        base_id = table.get("base_id")
        table_name = table.get("table_name")
        try:
            meta = get_airtable_metadata(base_id, table_name)
            metadata.append({
                "base_id": base_id,
                "table_name": table_name,
                "fields": meta,
            })
        except Exception as e:
            metadata.append({
                "base_id": base_id,
                "table_name": table_name,
                "fields": [],
                "error": str(e),
            })

    return render_template("config_view.html", 
        filename=filename, 
        config=config_contents, 
        metadata=metadata, 
        file_info=file_info,
        cli_commands=cli_commands,
    )

# Upload a Config
@routes.route("/configs/upload", methods=["GET", "POST"])
def upload_config():
    if request.method == "POST":
        uploaded_file = request.files.get("file")
        if uploaded_file and uploaded_file.filename.endswith(".json"):
            save_path = os.path.join(CONFIG_DIR, uploaded_file.filename)
            uploaded_file.save(save_path)
            flash(f"Config file '{uploaded_file.filename}' uploaded successfully!", "success")
        else:
            flash("Invalid file type. Only .json config files are allowed.", "danger")
        return redirect(url_for("routes.index"))

    return render_template("upload_config.html")

# Run a config export
@routes.route("/configs/run_view/<filename>")
@routes.route("/configs/run_view/<filename>/<profile>")
def run_export_view(filename, profile="default"):
    return render_template("run_export.html", filename=filename, profile=profile)

# Delete a config
@routes.route("/configs/delete/<filename>", methods=["POST"])
def delete_config(filename):
    # Ensure it's a JSON file
    if not filename.endswith(".json"):
        flash("Only JSON config files can be deleted.", "danger")
        return redirect(url_for("routes.index"))

    file_path = os.path.join(CONFIG_DIR, filename)

    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            flash(f"🗑️ Deleted config file: {filename}", "success")
        else:
            flash("Config file not found.", "warning")
    except Exception as e:
        flash(f"❌ Failed to delete config file: {e}", "danger")

    return redirect(url_for("routes.index"))

# Edit a config
@routes.route("/configs/edit/<filename>", methods=["POST"])
def edit_config(filename):
    config_path = os.path.join(CONFIG_DIR, filename)

    if not os.path.exists(config_path):
        flash("Config file not found.", "danger")
        return redirect(url_for("routes.list_configs"))

    new_config_data = request.form.get("config_data")

    try:
        # Validate JSON first
        parsed_json = json.loads(new_config_data)

        # If valid, overwrite the file
        with open(config_path, "w") as f:
            json.dump(parsed_json, f, indent=2)

        flash(f"✅ Successfully saved changes to {filename}.", "success")
    except json.JSONDecodeError as e:
        flash(f"❌ Invalid JSON: {str(e)}", "danger")
        return redirect(url_for("routes.view_config", filename=filename))

    return redirect(url_for("routes.view_config", filename=filename))

# Download Config or Hyper File
@routes.route("/download/<folder>/<filename>")
def download_file(folder, filename):
    if folder not in ["output", "configs"]:
        flash("Invalid folder.", "danger")
        return redirect(url_for("routes.index"))

    directory = HYPER_DIR if folder == "output" else CONFIG_DIR
    return send_from_directory(directory, filename, as_attachment=True)

# Help page
@routes.route("/help")
def help_page():
    return render_template("help.html")

@routes.route("/configs/stream/<filename>")
def stream_export(filename):
    config_path = os.path.join(CONFIG_DIR, filename)
    profile = request.args.get("profile", "default")

    def generate():
        yield f"▶️ Running export for `{filename}` using profile `{profile}`...\n\n"
        try:
            process = subprocess.Popen(
                ["airtable-export", "export", "--config", config_path, "--profile", profile],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            for line in iter(process.stdout.readline, ''):
                yield line
        except Exception as e:
            yield f"❌ Error running export: {e}\n"

    return Response(stream_with_context(generate()), mimetype="text/plain")

# Create a new config form
@routes.route("/configs/create", methods=["GET"])
def create_config_form():
    return render_template("config_create.html")

#$ Create a new config
@routes.route("/configs/create", methods=["POST"])
def create_config():
    description = request.form.get("description")
    base_id = request.form.get("base_id")
    table_name = request.form.get("table_name")
    filename = request.form.get("filename")

    if not all([description, base_id, table_name, filename]):
        flash("All fields are required.", "danger")
        return redirect(url_for("routes.create_config_form"))

    # Verify file doesn't already exist
    config_path = os.path.join(CONFIG_DIR, filename)
    if os.path.exists(config_path):
        flash("A config file with that name already exists.", "danger")
        return redirect(url_for("routes.create_config_form"))

    try:
        fields = get_airtable_metadata(base_id, table_name)
        columns = []

        for field in fields:
            col = {
                "source": field["name"],
                "type": airtable_type_to_json_type(field["type"]),
            }
            columns.append(col)

        config = {
            "profiles": {
                "default": {
                    "description": description,
                    "tables": [
                        {
                            "base_id": base_id,
                            "table_name": table_name,
                            "output_file": f"output/{table_name.lower()}.hyper",
                            "columns": columns,
                        }
                    ]
                }
            }
        }

        # Save to file
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)

        flash(f"Config '{filename}' created successfully.", "success")
        return redirect(url_for("routes.view_config", filename=filename))

    except Exception as e:
        flash(f"Error creating config: {e}", "danger")
        return redirect(url_for("routes.create_config_form"))
