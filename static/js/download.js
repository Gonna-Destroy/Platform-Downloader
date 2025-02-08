
document.addEventListener('DOMContentLoaded', main);

const buttons = document.querySelectorAll('.buttons');
const form = document.getElementById('send-params');

form.addEventListener('submit', function (event){
    event.preventDefault();

    let url = document.getElementById('url')
    url.value = document.getElementById('link').src

    let format = document.getElementById('format').value
    let quality = document.getElementById('quality').value

    if (format && quality){
        const data = {
            'format': format,
            'quality': quality,
            'url': url.value
        }
        fetch("/success", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => {
            if(response.ok){
                return response.json()
            }          
        })
        .then(dataResponse => {
            if (dataResponse.load === 'loaded') {
                window.location.href = `/success?format=${format}&url=${dataResponse.url}`
            }
            else if (dataResponse.load === 'not loaded'){
                window.location.href = `/error`
            }
        })
    }
    else {
        alert("Пожалуйста, выберите формат и качество видео.")
    }
})

function main() {

    buttons.forEach(
        (button) => {
            button.addEventListener('click', function() {
                if (button.dataset.quality) {
                    buttons.forEach(
                        btn => {
                            if(btn.dataset.quality){
                                btn.style.backgroundColor = "white";
                                btn.style.color = "#17252a";
                            }
                        }
                    ); 
                    quality = document.getElementById('quality')
                    quality.value = button.dataset.quality
                }
                if (button.dataset.format) {
                    buttons.forEach(
                        btn => {
                            if(btn.dataset.format){
                                btn.style.backgroundColor = "white";
                                btn.style.color = "#17252a";
                            }
                        }
                    ); 
                    format = document.getElementById('format')
                    format.value = button.dataset.format
                }
                button.style.color = 'white';
                button.style.backgroundColor = 'black';
            });
        }
    );
}
