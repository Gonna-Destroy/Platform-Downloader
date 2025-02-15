document.getElementById('download').addEventListener('click', function(){
    const link = document.createElement('a')

    source = document.getElementsByTagName('source')[0]
    
    link.href = source.src

    var type = source.type
    const format = type.split('/')[1];

    title = document.getElementsByTagName('input')[0].value

    link.download = `${title}.${format}`

    document.body.appendChild(link)

    link.click()

    document.removeChild(link)    
})