/**
 * Created by vladis on 08.07.2017.
 */

var i = 0;

function new_quest() {
    var div__test = document.getElementById('div_for_test'),
        div = document.createElement('div'),
        inp_t = document.createElement('input'),
        inp_b = document.createElement('input'),
        ul = document.createElement('ul'),
        inp_b_d = document.createElement('input');
    inp_t.className = 'form-control';
    inp_t.style.width = '250px';
    inp_t.style.marginRight = '5px';
    inp_t.style.float = 'left';
    inp_b.className = 'btn btn-success';
    inp_b_d.className = 'btn btn-danger';
    inp_b_d.style.marginBottom = '5px';
    div__test.appendChild(div);
        div.className = 'test_div_'+i;
        div.appendChild(inp_t);
            inp_t.type = 'text';
            inp_t.name = 'quest';
            inp_t.placeholder = 'Введите вопрос...';
            inp_t.required = true;
            inp_t.focus();
        div.appendChild(inp_b);
            inp_b.type = 'button';
            inp_b.value = 'Добавить ответы';
        var new_num = i;
            inp_b.onclick = function(){new_answer(ul, new_num);};
        div.appendChild(ul);
            ul.className = 'list_test_div_'+i;
        div.appendChild(inp_b_d);
            inp_b_d.type = 'button';
            inp_b_d.value = 'Удалить весь вопрос';
            inp_b_d.onclick = function(){div__test.removeChild(div);};
    i++;
}

function new_answer(list, num) {
    var ul_in_div = list,
        li_to_ul = document.createElement('li'),
        input_to_li_text = document.createElement('input'),
        input_to_li_button_del = document.createElement('input'),
        input_to_li_radio_r = document.createElement('input');
    input_to_li_radio_r.style.float = 'left';
    input_to_li_text.style.width = '250px';
    input_to_li_text.style.marginRight = '5px';
    input_to_li_text.style.float = 'left';
    input_to_li_button_del.className = 'btn btn-danger';
    li_to_ul.style.marginTop = '5px';
    ul_in_div.appendChild(li_to_ul);
        li_to_ul.type = '1';
        li_to_ul.appendChild(input_to_li_radio_r);
            input_to_li_radio_r.type = 'radio';
            input_to_li_radio_r.name = 'right_'+num;
        li_to_ul.appendChild(input_to_li_text);
            input_to_li_text.type = 'text';
            input_to_li_text.className = 'answer_'+num+' form-control';
            var t_i = document.querySelectorAll('.answer_'+num).length;
            input_to_li_text.name = 'answer_'+num;
            input_to_li_text.required = true;
            input_to_li_text.placeholder = 'Введите ответ...';
            input_to_li_text.focus();
            input_to_li_radio_r.value = ''+t_i;
            input_to_li_radio_r.checked = true;
        li_to_ul.appendChild(input_to_li_button_del);
            input_to_li_button_del.type = 'button';
            input_to_li_button_del.value = 'Удалить ответ';
            input_to_li_button_del.onclick = function(){ul_in_div.removeChild(li_to_ul);};
}
