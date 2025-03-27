from flask import Flask, request, render_template_string, jsonify
from flask_cors import CORS
from jobs import extract_job_info, append_to_json  # Updated import: changed to append_to_json
import json
import subprocess
import os
import sys

app = Flask(__name__)
CORS(app)

JSON_PATH = "/Users/coding/Desktop/localRepos/resume-generator/_submitted/_applied.json"

FORM_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Job Submission Form</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Segoe UI', Arial, sans-serif;
        }

        body {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            background-color: #f5f5f5;
        }

        .container {
            width: 50%;
            max-width: 600px;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        h1 {
            color: #BA68C8;
            text-align: center;
            margin-bottom: 20px;
        }

        label {
            font-weight: bold;
            display: block;
            margin: 10px 0 5px;
            color: #424242;
        }

        input, textarea {
            width: 100%;
            padding: 10px;
            margin-bottom: 15px;
            border: 2px solid #9e9e9e;
            border-radius: 5px;
            font-size: 16px;
            transition: border-color 0.3s;
        }

        input:focus, textarea:focus {
            outline: none;
            border-color: #BA68C8;
        }

        textarea {
            height: 200px;
            resize: none;
        }

        .button-container {
            text-align: center;
        }

        input[type="submit"] {
            background: #BA68C8;
            color: white;
            border: none;
            cursor: pointer;
            padding: 10px 20px;
            font-size: 16px;
            border-radius: 5px;
            transition: background-color 0.3s;
        }

        input[type="submit"]:hover {
            background: #9e9e9e;
        }

        /* New navigation button styles */
        .nav-buttons {
            text-align: center;
            margin-bottom: 20px;
        }
        .toggle-nav-btn {
            background-color: #BA68C8;
            color: white;
            text-decoration: none;
            padding: 8px 16px;
            border-radius: 4px;
            margin: 0 5px;
            transition: background-color 0.3s;
        }
        .toggle-nav-btn:hover {
            background-color: #9e9e9e;
        }

        /* New door icon styles */
        #door-icon {
            position: fixed;
            top: 10px;
            right: 10px;
            font-size: 24px;
            cursor: pointer;
        }
        .closed-door {
            color: #BA68C8;
        }
        .open-door {
            color: #9e9e9e;
        }
    </style>
</head>
<body>
    <a href="/view" id="door-icon" class="closed-door">📝</a>
    <div class="container">
        <h1>Job Submission Form</h1>
        <form action="/submit" method="post">
            <label for="url">Job Posting URL:</label>
            <input type="text" id="url" name="url" required>

            <label for="job_description">Job Description:</label>
            <textarea id="job_description" name="job_description" required></textarea>

            <div class="button-container">
                <input type="submit" value="Submit">
            </div>
        </form>
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    return render_template_string(FORM_HTML)

@app.route("/submit", methods=["POST"])
def submit():
    url = request.form.get("url")
    # normalize URL by removing trailing slash
    norm_url = url.rstrip('/')
    job_description = request.form.get("job_description")
    
    # Duplicate URL validation with normalized URLs
    try:
        with open(JSON_PATH, "r") as f:
            jobs = json.load(f)
    except Exception:
        jobs = []
    for job in jobs:
        existing_url = job.get("url", "").rstrip('/')
        if existing_url == norm_url:
            return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Duplicate Job URL</title>
    <style>
        body { display: flex; justify-content: center; align-items: center; height: 100vh; background-color: #f5f5f5; }
        .container { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); text-align: center; }
        button { background: #BA68C8; color: white; border: none; cursor: pointer; padding: 10px 20px; font-size: 16px; border-radius: 5px; transition: background-color 0.3s; }
        button:hover { background: #9e9e9e; }
    </style>
</head>
<body>
    <div class="container">
        <p>The job URL already exists. Please submit a different job posting.</p>
        <form action="/" method="get">
            <button type="submit">Go Back</button>
        </form>
    </div>
</body>
</html>
            """
    
    job_title, company = extract_job_info(norm_url)
    append_to_json(job_title, company, norm_url, job_description)
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Submission Successful</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Segoe UI', Arial, sans-serif;
        }

        body {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            background-color: #f5f5f5;
            text-align: center;
        }

        .container {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            width: 50%;
            max-width: 400px;
        }

        p {
            font-size: 18px;
            margin-bottom: 20px;
            color: #424242;
        }

        button {
            background: #BA68C8;
            color: white;
            border: none;
            cursor: pointer;
            padding: 10px 20px;
            font-size: 16px;
            border-radius: 5px;
            transition: background-color 0.3s;
        }

        button:hover {
            background: #9e9e9e;
        }
    </style>
</head>
<body>
    <div class="container">
        <p>Job information submitted successfully!</p>
        <form action="/" method="get">
            <button type="submit">Submit Another Job</button>
        </form>
    </div>
</body>
</html>
    """

@app.route("/view", methods=["GET"])
def view_jobs():
    with open(JSON_PATH, "r") as f:
        jobs = json.load(f)
    companies = sorted({job.get('company', '') for job in jobs if job.get('company', '')})
    options_html = '<option value="all">All Companies</option>'
    for company in companies:
        options_html += f'<option value="{company}">{company}</option>'
    table_rows = ""
    for idx, job in enumerate(jobs):
        table_rows += """
        <tr data-applied="{applied}" data-skip="{skip}" data-company="{company}">
            <td class="checkbox-cell">
                <label class="checkbox-container">
                    <input type="checkbox" {applied_checked} onchange="updateField({index}, 'applied', this.checked)">
                    <span class="checkmark"></span>
                </label>
            </td>
            <td>
                <button class="url-btn" onclick="window.open('{url}', '_blank')">View Link</button>
            </td>
            <td>
                <button class="toggle-btn" onclick="togglePanel(this)" data-field="resume" data-index="{index}" data-content="<pre style='white-space: pre-wrap;'>{resume}</pre>">View Resume</button>
            </td>
            <td>
                <button class="toggle-btn" onclick="togglePanel(this)" data-field="cover_letter" data-index="{index}" data-content="<pre style='white-space: pre-wrap;'>{cover_letter}</pre>">View Cover Letter</button>
            </td>
            <td>
                <button class="toggle-btn" onclick="togglePanel(this)" data-content="<pre style='white-space: pre-wrap;'>{job_description}</pre>">View Job Description</button>
            </td>
            <td class="job-title">{job_title}</td>
            <td>{company}</td>
            <td class="checkbox-cell">
                <label class="checkbox-container">
                    <input type="checkbox" {skip_checked} onchange="updateField({index}, 'skip', this.checked)">
                    <span class="checkmark"></span>
                </label>
            </td>
        </tr>
        """.format(
            index=idx,
            applied=job.get('applied', False),
            skip=job.get('skip', False),
            job_title=job.get('job_title', ''),
            company=job.get('company', ''),
            url=job.get('url', ''),
            job_description=job.get('job_description', ''),
            resume=job.get('resume', ''),
            cover_letter=job.get('cover_letter', ''),
            applied_checked="checked" if job.get('applied', False) else "",
            skip_checked="checked" if job.get('skip', False) else ""
        )
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>View Job Data</title>
        <style>
            body {{
                font-family: 'Segoe UI', Arial, sans-serif;
                margin: 20px;
                background-color: #f5f5f5;
            }}
            h1 {{
                color: #BA68C8;
                text-align: center;
                margin-bottom: 30px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                background: white;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                border-radius: 8px;
                overflow: hidden;
            }}
            th {{
                background-color: #BA68C8;
                color: white;
                padding: 15px;
                text-align: left;
            }}
            td {{
                padding: 12px 15px;
                border-bottom: 1px solid #eee;
            }}
            tr:hover {{
                background-color: #f8f8f8;
            }}
            .toggle-btn {{
                background-color: #BA68C8;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                cursor: pointer;
                transition: background-color 0.3s;
            }}
            .toggle-btn:hover {{
                background-color: #9e9e9e;
            }}
            .toggle-btn.active {{
                background-color: #9e9e9e;
            }}
            .checkbox-container {{
                display: block;
                position: relative;
                padding-left: 25px;
                cursor: pointer;
            }}
            .checkbox-container input {{
                position: absolute;
                opacity: 0;
                cursor: pointer;
            }}
            .checkmark {{
                position: absolute;
                top: 0;
                left: 0;
                height: 18px;
                width: 18px;
                background-color: #fff;
                border: 2px solid #BA68C8;
                border-radius: 3px;
            }}
            .checkbox-container:hover input ~ .checkmark {{
                background-color: #f0f0f0;
            }}
            .checkbox-container input:checked ~ .checkmark {{
                background-color: #BA68C8;
            }}
            .checkmark:after {{
                content: "";
                position: absolute;
                display: none;
            }}
            .checkbox-container input:checked ~ .checkmark:after {{
                display: block;
            }}
            .checkbox-container .checkmark:after {{
                left: 5px;
                top: 2px;
                width: 5px;
                height: 10px;
                border: solid white;
                border-width: 0 2px 2px 0;
                transform: rotate(45deg);
            }}
            .job-title {{
                font-weight: 600;
                color: #424242;
            }}
            .checkbox-cell {{
                text-align: center;
            }}
            .action-bar {{
                margin-bottom: 20px;
                text-align: right;
            }}
            .generate-btn {{
                background-color: #BA68C8;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 16px;
                transition: background-color 0.3s;
            }}
            .generate-btn:hover {{
                background-color: #9e9e9e;
            }}
            .generate-btn:disabled {{
                background-color: #cccccc;
                cursor: not-allowed;
            }}
            .status-message {{
                display: none;
                margin-top: 10px;
                padding: 10px;
                border-radius: 4px;
                text-align: center;
            }}
            .status-message.success {{
                background-color: #e8f5e9;
                color: #2e7d32;
                border: 1px solid #a5d6a7;
            }}
            .status-message.error {{
                background-color: #ffebee;
                color: #c62828;
                border: 1px solid #ef9a9a;
            }}
            #info-panel {{
                position: fixed;
                top: 0;
                right: 0;
                width: 33%;
                height: 100%;
                background-color: #f8f8f8;
                border-left: 1px solid #ccc;
                box-shadow: -2px 0 5px rgba(0,0,0,0.1);
                overflow: auto;
                padding: 20px;
                display: none;
            }}
            .close-btn {{
                background-color: #BA68C8;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 4px;
                cursor: pointer;
                margin-bottom: 10px;
            }}
            .close-btn:hover {{
                background-color: #9e9e9e;
            }}
            .copy-btn {{
                background-color: #BA68C8;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 4px;
                cursor: pointer;
                margin-bottom: 10px;
                margin-left: 10px;
            }}
            .copy-btn:hover {{
                background-color: #9e9e9e;
            }}
            .edit-btn {{
                background-color: #BA68C8;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 4px;
                cursor: pointer;
                margin-bottom: 10px;
                margin-left: 10px;
            }}
            .edit-btn:hover {{
                background-color: #9e9e9e;
            }}            
            .panel-controls {{
                margin-bottom: 10px;
            }}
            .nav-buttons {{
                text-align: center;
                margin-bottom: 20px;
            }}
            .toggle-nav-btn {{
                background-color: #BA68C8;
                color: white;
                text-decoration: none;
                padding: 8px 16px;
                border-radius: 4px;
                margin: 0 5px;
                transition: background-color 0.3s;
            }}
            .toggle-nav-btn:hover {{
                background-color: #9e9e9e;
            }}
            #door-icon {{
                position: fixed;
                top: 10px;
                right: 10px;
                font-size: 24px;
                cursor: pointer;
            }}
            .closed-door {{
                color: #BA68C8;
            }}
            .open-door {{
                color: #9e9e9e;
            }}
        </style>
    </head>
    <body>
        <a href="/" id="door-icon" class="open-door">🚪</a>
        <h1>Job Applications Dashboard</h1>
        <div class="filter-container" style="margin-bottom: 20px; text-align: center;">
            <label>
                <input type="checkbox" id="filter-applied"> Hide Applied Records
            </label>
            <label style="margin-left: 20px;">
                <input type="checkbox" id="filter-skip"> Hide Skipped Records
            </label>
            <label style="margin-left: 20px;">
                <input type="checkbox" id="filter-unprocessed"> Hide Unprocessed Records
            </label>
            <!-- New company filter dropdown -->
            <label style="margin-left: 20px;">
                Company:
                <select id="filter-company">
                    {options_html}
                </select>
            </label>
        </div>
        <div class="action-bar">
            <button class="generate-btn" onclick="generateContent()">Generate Resume/Cover Letter</button>
            <div id="status-message" class="status-message"></div>
        </div>
        <table>
            <thead>
                <tr>
                    <th>Applied</th>
                    <th>URL</th>
                    <th>Resume</th>
                    <th>Cover Letter</th>
                    <th>Job Description</th>
                    <th>Job Title</th>
                    <th>Company</th>
                    <th>Skip</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>
        <div id="info-panel"></div>
        <script>
            function updateField(index, field, value) {{
                fetch("/update", {{
                    method: "POST",
                    headers: {{
                        "Content-Type": "application/json"
                    }},
                    body: JSON.stringify({{ index: index, field: field, value: value }})
                }})
                .then(response => response.json())
                .then(data => {{
                    if(data.status !== "success") {{
                        alert("Error updating");
                    }}
                }});
            }}
            
            let infoPanel = document.getElementById('info-panel');
            let activeButton = null;
            let currentJobIndex = null;
            let currentField = null;
            let isEditing = false;
            function togglePanel(btn) {{
                if(activeButton === btn) {{
                    closePanel();
                    return;
                }}
                if(activeButton) {{
                    activeButton.classList.remove("active");
                }}
                activeButton = btn;
                btn.classList.add("active");
                let content = btn.getAttribute("data-content");
                currentJobIndex = btn.getAttribute("data-index");
                currentField = btn.getAttribute("data-field");
                isEditing = false;
                let editButtonHtml = "";
                if(currentField === "resume" || currentField === "cover_letter") {{
                    editButtonHtml = '<button id="edit-btn" onclick="toggleEdit()" class="edit-btn">Edit</button>';
                }}
                // Removed the close button from the panel-controls:
                document.getElementById("info-panel").innerHTML = "<div class='panel-controls'><button onclick='copyContent()' class='copy-btn'>Copy All</button>" + editButtonHtml + "</div><div id='panel-content'>" + content + "</div>";
                document.getElementById("info-panel").style.display = "block";
            }}
            function toggleEdit() {{
                if (!isEditing) {{
                    const panelContentDiv = document.getElementById("panel-content");
                    const currentText = panelContentDiv.innerText;
                    panelContentDiv.innerHTML = '<textarea id="edit-textarea" style="width:100%; height:200px;">' + currentText + '</textarea>';
                    document.getElementById("edit-btn").textContent = 'Save';
                    isEditing = true;
                }} else {{
                    saveEdit();
                }}
            }}
            function saveEdit() {{
                const newText = document.getElementById("edit-textarea").value;
                fetch('/edit_text', {{
                    method: 'POST',
                    headers: {{
                        "Content-Type": "application/json"
                    }},
                    body: JSON.stringify({{ index: parseInt(currentJobIndex), field: currentField, text: newText }})
                }})
                .then(response => response.json())
                .then(data => {{
                    if(data.status === 'success') {{
                        const panelContentDiv = document.getElementById("panel-content");
                        panelContentDiv.innerHTML = '<pre style="white-space: pre-wrap;">' + newText + '</pre>';
                        document.getElementById("edit-btn").textContent = 'Edit';
                        isEditing = false;
                        const activeButton = document.querySelector('.toggle-btn.active');
                        if (activeButton) {{
                            activeButton.setAttribute('data-content', '<pre style="white-space: pre-wrap;">' + newText + '</pre>');
                        }}
                    }} else {{
                        alert("Error updating: " + data.message);
                    }}
                }})
                .catch(err => {{
                    alert("Error: " + err);
                }});
            }}
            function copyContent() {{
                let panelContent = document.getElementById("panel-content").innerText;
                navigator.clipboard.writeText(panelContent)
                    .then(() => {{
                        alert("Copied to clipboard!");
                    }})
                    .catch((err) => {{
                        alert("Error copying text: " + err);
                    }});
            }}
            
            function filterTableRows() {{
                const hideApplied = document.getElementById('filter-applied').checked;
                const hideSkip = document.getElementById('filter-skip').checked;
                const hideUnprocessed = document.getElementById('filter-unprocessed').checked;
                const filterCompany = document.getElementById('filter-company').value;
                const tableRows = document.querySelectorAll("table tbody tr");
                tableRows.forEach(row => {{
                    const applied = row.getAttribute('data-applied') === "True" || row.getAttribute('data-applied') === "true";
                    const skip = row.getAttribute('data-skip') === "True" || row.getAttribute('data-skip') === "true";
                    const company = row.getAttribute('data-company');
                    if ((hideApplied && applied) || (hideSkip && skip) || (hideUnprocessed && !applied && !skip) ||
                        (filterCompany !== 'all' && company !== filterCompany)) {{
                        row.style.display = "none";
                    }} else {{
                        row.style.display = "";
                    }}
                }});
            }}
            
            document.getElementById('filter-applied').addEventListener('change', filterTableRows);
            document.getElementById('filter-skip').addEventListener('change', filterTableRows);
            document.getElementById('filter-unprocessed').addEventListener('change', filterTableRows);
            // New event listener for company dropdown
            document.getElementById('filter-company').addEventListener('change', filterTableRows);
            
            function generateContent() {{
                const button = document.querySelector('.generate-btn');
                const statusMessage = document.getElementById('status-message');
                
                button.disabled = true;
                button.textContent = 'Generating...';
                statusMessage.style.display = 'none';
                
                fetch('/generate', {{
                    method: 'POST',
                }})
                .then(response => response.json())
                .then(data => {{
                    if (data.status === 'success') {{
                        statusMessage.textContent = 'Generation completed successfully! Refreshing page...';
                        statusMessage.className = 'status-message success';
                        setTimeout(() => location.reload(), 2000);
                    }} else {{
                        throw new Error(data.message || 'Generation failed');
                    }}
                }})
                .catch(error => {{
                    statusMessage.textContent = `Error: ${{error.message}}`;
                    statusMessage.className = 'status-message error';
                }})
                .finally(() => {{
                    button.disabled = false;
                    button.textContent = 'Generate Resume/Cover Letter';
                    statusMessage.style.display = 'block';
                }});
            }}
        </script>
    </body>
    </html>
    """.format(table_rows=table_rows, options_html=options_html)
    return html_content

@app.route("/update", methods=["POST"])
def update_job_field():
    data = request.get_json()
    idx = data.get("index")
    field = data.get("field")
    value = data.get("value")
    try:
        with open(JSON_PATH, "r") as f:
            jobs = json.load(f)
        if idx < 0 or idx >= len(jobs):
            return jsonify(status="error", message="Index out of bounds"), 400
        if field not in ["applied", "skip"]:
            return jsonify(status="error", message="Invalid field"), 400
        jobs[idx][field] = value
        # If the "skip" checkbox is checked, mark the record as processed.
        if field == "skip" and value:
            jobs[idx]["llm_processed"] = True
        with open(JSON_PATH, "w") as f:
            json.dump(jobs, f, indent=2)
        return jsonify(status="success")
    except Exception as e:
        return jsonify(status="error", message=str(e)), 500

@app.route("/edit_text", methods=["POST"])
def edit_text():
    data = request.get_json()
    index = data.get("index")
    field = data.get("field")
    text = data.get("text")
    try:
        with open(JSON_PATH, "r") as f:
            jobs = json.load(f)
        if index < 0 or index >= len(jobs):
            return jsonify(status="error", message="Index out of bounds"), 400
        if field not in ["resume", "cover_letter"]:
            return jsonify(status="error", message="Invalid field"), 400
        jobs[index][field] = text
        with open(JSON_PATH, "w") as f:
            json.dump(jobs, f, indent=2)
        return jsonify(status="success", message="Updated successfully", text=text)
    except Exception as e:
        return jsonify(status="error", message=str(e)), 500

@app.route("/generate", methods=["POST"])
def generate():
    try:
        script_path = os.path.join(os.path.dirname(__file__), "main.py")
        subprocess.run([sys.executable, script_path], check=True)
        return jsonify({"status": "success", "message": "Generation completed successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5600)