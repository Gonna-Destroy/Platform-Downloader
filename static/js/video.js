

link = document.getElementsByTagName('source')[0].src
const data = JSON.stringify({'title': link})

window.addEventListener('unload', () => {
    navigator.sendBeacon('/delete', data)
})

