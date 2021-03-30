/**
 * Created by linea on 12.06.2017.
 * by Vladis
 */


/**
 * Получение и отправка данных AJAX
 * @param {Object} data Параметры запроса
 *   @param {String} [data.url=document.location] URL запроса
 *   @param {String} [data.method="GET"] Метод запроса (GET или POST]
 *   @param {String} [data.dataType="json"] Формат получаемых данных
 *   @param {(Object|String)} data.data Данные запроса в виде объекта или сериализованной строки
 *   @param {Boolean} [data.async=true] Выполнить запрос асинхронно
 * @param {Function} [onsuccess] Функция, вызываемая в случае успешного запроса
 * @param {Function} [onerror] Функция, вызываемая при ошибке
 *
 * @author nomnes
 * @version 0.1
 */
var AJAX = function(data, onsuccess, onerror){
    if (!data) {
        data = {};
    }
    data.url = data.url || document.location;
    data.method = data.method || 'GET';
    data.dataType = data.dataType || 'json';
    data.data = data.data || false;
    data.async = typeof data.async == 'boolean' ? data.async : true;

    data.method = data.method.toUpperCase();

    function sender() {
        var request = new XMLHttpRequest();
        // обработка ответа
        request.onload = function() {
            if (request.status >= 200 && request.status < 400) {
                // выполнить при получении данных
                if (onsuccess) {
                    var result;
                    if (data.dataType.toLowerCase() == 'json') {
                        // парсинг JSON в объект
                        result = JSON.parse(request.responseText);
                    } else {
                        // удаление комментариев из html
                        var re = /<!--.*?-->/g;
                        result = request.responseText;
                        result = result.replace(re, '');
                    }
                    // пользовательская функция обработки данных
                    onsuccess(result);
                }
            } else {
                // выполнить при ошибке получения данных
                if (onerror) {
                    onerror(request.status);
                }
            }
        };
        var num = 0;
        request.onerror = function() {
            // выполнить при ошибке запроса
            if (onerror) {
                onerror(request.status);
            } else {
                if (num < 10) {
                    sender();
                }
            }
        };
        if (data.data) {
            // если есть данные для отправки
            var body = '';
            if (typeof(data.data) == "object") {
                // сериализация данных
                body = Object.keys(data.data).map(function(key) {
                    return key + '=' + encodeURIComponent(data.data[key]);
                }).join('&');
            } else {
                body = data.data;
            }
            if (data.method == 'POST') {
                // отправка методом POST
                request.open('POST', data.url, true);
                request.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
                request.send(body);
            } else {
                // отправка методом GET
                request.open('GET', data.url + '?' + body, true);
                request.send();
            }
        } else {
            // отправка пустого запроса
            request.open(data.method, data.url, data.async);
            request.send();
        }
    }
    sender();
};


/**
 * Сериализация данных формы
 * @param {object} form Объект DOM
 * @returns {string} Сериализованная строка данных
 *
 * @author nomnes
 * @version 0.1
 */
var Serialize = function(form) {
    function text(e){
        if ( e.value !== '' ) {
            return [e.name + '=' + encodeURIComponent(e.value)];
        } else {
            return [];
        }
    }
    function select(e){
        var array = [],
            options = e.selectedOptions;
        if ( options.length ) {
            for (var i=0; i<options.length; i++) {
                array[array.length] = e.name + '=' + encodeURIComponent(options[i].value);
                if ( i+1 == options.length ) {
                    return array;
                }
            }
        } else {
            return array;
        }
    }
    function checkbox(e){
        if ( e.checked ) {
            return [e.name + '=' + encodeURIComponent(e.value)];
        } else {
            return [];
        }
    }
    var array = [],
        elements = form.querySelectorAll('input,textarea,select');
        for (var i=0; i<elements.length; i++) {
            var newVal;
            switch ( elements[i].tagName.toLowerCase()  ) {
                case 'select':
                    newVal = select(elements[i]);
                    break;
                case 'textarea':
                    newVal = text(elements[i]);
                    break;
                default:
                    switch ( elements[i].type.toLowerCase()  ) {
                        case 'checkbox':
                        case 'radio':
                            newVal = checkbox(elements[i]);
                            break;
                        default:
                            newVal = text(elements[i]);
                    }
            }
            if ( newVal && newVal.length > 0 ) {
                array = array.concat(newVal);
            }
            if ( i+1 == elements.length ) {
                return array.join('&');
            }
        }
};


function UpdateCurseList() {
    var all_course_div = document.getElementById('all_course'),
        filter = document.querySelectorAll('.filter select');

    function update_page() {
        all_course_div.innerHTML = '';
        AJAX({url: "/course", data: Serialize(document.querySelector('.filter'))},
            function(data){
                var text = '';
                for (var i = 0; i < data.all_course.length; i++) {
                    text += '<a class="list-group-item" href="/course/'+data.all_course[i].id+'">'+data.all_course[i].name+'</a>';
                }
                all_course_div.innerHTML = text;
            });
    }
    for (var j = 0; j < filter.length; j++) {
        filter[j].onchange = update_page;
    }
}


function Search() {
    var all_user_div = document.getElementById('list_user'),
        search = document.querySelectorAll('.search_f input');

    function update_page() {
        all_user_div.innerHTML = '';
        AJAX({url: "/search", data: Serialize(document.querySelector('.search_f'))},
            function (data) {
                var text = '',
                    button = '',
                    b_div = '',
                    span = '',
                    img = '',
                    p = '';
                for (var i = 0; i < data.all_user.length; i++) {
                    button = '<button class="btn btn-primary btn-rounded"><span class="fa fa-pencil"></span></button>';
                    b_div = '<div class="list-group-controls">'+button+'</div>';
                    span = '<span class="contacts-title">'+data.all_user[i].login+'</span>';
                    p = '<p>'+data.all_user[i].email+'</p>';
                    img = '<img src="'+data.all_user[i].avatar+'" class="pull-left" alt="'+data.all_user[i].login+'">';
                    text += '<a href="/message/'+data.all_user[i].login+'" class="list-group-item">'+img+span+p+b_div+'</a>';
                }
                all_user_div.innerHTML = text;
        });
    }
    for (var j = 0; j < search.length; j++) {
        search[j].onchange = update_page;
    }
}


function alarm_mess(url) {
    var new_mess = document.getElementById('count_new_mess'),
        cur_count = new_mess.innerHTML;
    AJAX({url: "/new_message", data: {new_mess: true}},
        function (data) {
            if (data.check == true) {
                new_mess.innerHTML = parseInt(cur_count)+1;
                var audio = new Audio(url);
                audio.play();
            }
        }
    )
}


function no_reload_mess(login) {
    var text_area = document.getElementById('text_area');
    if (text_area != '' || text_area != []) {
        AJAX({url: "/message/"+login, data: {mess_get: text_area.value}});
        text_area.value = '';
        var keklol = setTimeout(function () {
            var block = document.getElementById("scrolls_down");
            block.scrollTop = block.scrollHeight;
        }, 500);
    }
}


function update_mess(login, cur_user_avatar, user_avatar) {
    var all_mess = document.getElementById('all_mess'),
        text = '',
        father = '';
    AJAX({url: "/message/"+login, data: {ajax: true}},
        function (data) {
            for (var i = 0; i < data.all_mes.length; i++) {
                var span_name = '',
                    span_data = '',
                    div_span = '',
                    div_img = '',
                    div_text = '';
                if (data.all_mes[i].user_id == data.all_mes[i].cur_user_id) {
                    span_name = '<span>'+data.all_mes[i].cur_user_login+'</span>';
                    span_data = '<span class="date">'+data.all_mes[i].datatime+'</span>';
                    div_span = '<div class="heading">'+span_name+span_data+'</div>';
                    div_img = '<div class="image"><img src="'+cur_user_avatar+'" alt="'+data.all_mes[i].cur_user_login+'"></div>';
                    div_text = div_img+'<div class="text">'+div_span+data.all_mes[i].text+'</div>';

                    text += '<div class="item in item-visible">'+div_text+'</div>';
                }
                else {
                    span_name = '<span>'+login+'</span>';
                    span_data = '<span class="date">'+data.all_mes[i].datatime+'</span>';
                    div_span = '<div class="heading">'+span_name+span_data+'</div>';
                    div_img = '<div class="image"><img src="'+user_avatar+'" alt="'+login+'"></div>';
                    div_text = div_img+'<div class="text">'+div_span+data.all_mes[i].text+'</div>';

                    text += '<div class="item item-visible">'+div_text+'</div>';
                }
                if (all_mess.innerHTML == null || all_mess.innerHTML != text) {
                    all_mess.innerHTML = text;
                }
            }
        }
    );
}


function check_radio() {
    var check_free = document.getElementById('check_free'),
        check_homework = document.getElementById('check_homework'),
        check_test = document.getElementById('check_test'),
        type_test = document.getElementById('type_test'),
        type_homework = document.getElementById('type_homework');
    if (check_free.checked) {
        type_test.style.display = 'none';
        type_homework.style.display = 'none';
    }
    if (check_homework.checked) {
        type_test.style.display = 'none';
        type_homework.style.display = 'block';
    }
    if (check_test.checked) {
        type_test.style.display = 'block';
        type_homework.style.display = 'none';
    }
}
