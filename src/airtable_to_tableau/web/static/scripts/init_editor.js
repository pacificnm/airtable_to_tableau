document.addEventListener("DOMContentLoaded", function () {
  const editor = ace.edit("editor");
  editor.session.setMode("ace/mode/json");
  editor.setTheme("ace/theme/github");
  editor.session.setUseWorker(true);
  editor.setOptions({
    fontSize: "14px",
    useSoftTabs: true,
    showPrintMargin: false,
  });

  const form = document.querySelector("form");
  form.addEventListener("submit", function () {
    document.getElementById("config_data").value = editor.getValue();
  });
});
