var main = document.getElementById("main-picture")
var isAnim = false;



function check_click(button){
    if (isAnim == true){
        return;
    }

    isAnim = true;

    switch(button.value){
        case "1":
            main.style.backgroundImage = "url('/static/pictures/first-picture.jpg')";
            break;
        case "2":
            main.style.backgroundImage = "url('/static/pictures/second-picture.jpg')";
            break;
        case "3":
            main.style.backgroundImage = "url('/static/pictures/third-picture.jpg')";
            break;  
        case "4":
            main.style.backgroundImage = "url('/static/pictures/fourth-picture.jpg')";
            break;
    }

    setTimeout(
        function(){
            isAnim = false;
        }, 1000
    )
}

function arrow_change(id) {
    if (isAnim == true){
        return;
    }

    var elements = document.getElementsByName('click');
    var act_button;

    for (var i = 0; i < elements.length; i++) {
        if (elements[i].checked) {
            act_button = elements[i];
            break;
        }
    }

    var number = parseInt(act_button.value);

    if (id == "right-arrow") {
        number += 1;
    } else if (id == "left-arrow") {
        number -= 1;
    }

    if (number < 1) {
        number = 4;
    } else if (number > 4) {
        number = 1;
    }

    isAnim = true;

    switch(number) {
        case 1:
            document.getElementById('first').checked = "true"
            main.style.backgroundImage = "url('/static/pictures/first-picture.jpg')";
            break;
        case 2:
            document.getElementById('second').checked = "true"
            main.style.backgroundImage = "url('/static/pictures/second-picture.jpg')";
            break;
        case 3:
            document.getElementById('third').checked = "true"
            main.style.backgroundImage = "url('/static/pictures/third-picture.jpg')";
            break;  
        case 4:
            document.getElementById('fourth').checked = "true"
            main.style.backgroundImage = "url('/static/pictures/fourth-picture.jpg')";
            break;
    }

    setTimeout(
        function(){
            isAnim = false;
        }, 1000
    );

}



