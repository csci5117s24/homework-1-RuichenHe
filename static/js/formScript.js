function toggleTextArea(checkbox){
    var textarea = document.getElementById('conditionalTextarea');
    var textareaTitle = document.getElementById("conditionalTextareaTitle");
    textarea.style.display = checkbox.checked ? 'block' : 'none';
    textareaTitle.style.display = checkbox.checked ? 'block' : 'none';
}