function validateAndSubmitForm() {
  const editor = ace.edit("editor");
  const jsonText = editor.getValue();
  let parsed;

  try {
    parsed = JSON.parse(jsonText);
  } catch (e) {
    alert("❌ Invalid JSON: " + e.message);
    return false;
  }

  if (!parsed.profiles || typeof parsed.profiles !== "object") {
    alert("❌ Missing or invalid 'profiles' object.");
    return false;
  }

  for (const [profileName, profileData] of Object.entries(parsed.profiles)) {
    if (!profileData || !Array.isArray(profileData.tables)) {
      alert(`❌ Profile '${profileName}' must contain a 'tables' array.`);
      return false;
    }

    for (const [i, table] of profileData.tables.entries()) {
      if (!table.base_id || !table.table_name || !table.output_file || !Array.isArray(table.columns)) {
        alert(`❌ In profile '${profileName}', table ${i + 1} is missing required fields.`);
        return false;
      }

      for (const [j, col] of table.columns.entries()) {
        if (!col.source || !col.type) {
          alert(`❌ In profile '${profileName}', table ${i + 1}, column ${j + 1} is missing 'source' or 'type'.`);
          return false;
        }
      }
    }
  }

  document.getElementById("json_data").value = jsonText;
  return true;
}
