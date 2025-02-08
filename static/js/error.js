document.addEventListener("DOMContentLoaded", change_message)

function change_message(){
    const text = document.getElementById("info");
    const fontSize = parseInt(window.getComputedStyle(text).fontSize)
    if (fontSize <= 22)
        text.textContent = "Похоже, что вы ввели некорректный url. Также проверьте подключение к интернету."
}