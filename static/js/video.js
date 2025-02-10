window.addEventListener('beforeunload', () => {
    link = document.getElementById('a').href
    const data = JSON.stringify({'uuid': link})
    navigator.sendBeacon('/delete', data)
})