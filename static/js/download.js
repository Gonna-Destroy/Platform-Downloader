
document.addEventListener('DOMContentLoaded', main);
var link;
var cycle;

const buttons = document.querySelectorAll('.buttons');
const form = document.getElementById('send-params');

async function message() {
    await alert("Не обновляйте страницу, иначе видео начнёт скачивание сначала!")
}

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

        visibility = document.getElementById('visible-progress')
        visibility.style.display = 'block';

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
            else {
                window.location.href = `/error`
            }    
        })
        .then(dataResponse => {
            if (dataResponse.load === 'start') {
                message()

                link = dataResponse.url

                const ws = new WebSocket('/progress')
                percent = document.getElementById('percent')

                data_for_send = {
                    'uuid': dataResponse.url
                }

                ws.onopen = function(event) {
                    cycle = setInterval(() => {
                        ws.send(JSON.stringify(data_for_send))
                    }, 1000)
                }

                ws.onmessage = function(event) {
                    info = JSON.parse(event.data)
                    if (/^\d+(\.\d+)?$/.test(info.curper)){
                        percent.textContent = info.curper
                    }
                    else {
                        var insert = "0.1"
                        percent.textContent = insert
                    }
                }

                ws.onclose = function(event) {
                    clearInterval(cycle)
                    window.location.href = `/success?format=${format}&url=${dataResponse.url}`
                }

                ws.onerror = function(event) {
                    clearInterval(cycle)
                    window.location.href = `/error`
                }
            }
            else {
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

// window.addEventListener('unload', () => {
//     const data = JSON.stringify({'title': link})
//     navigator.sendBeacon('/delload', data)
// })