// made by vladis 31.07.2017 (2:28)
// this uneversal code
// class_name_for_all = class name dragable list
// class_name_parent_all = parent class name 'class_name_for_all'
var class_name_for_all = 'lesson',
    name_id_parent_all = 'parent',
    class_name_for_place_div = 'place';
var all = document.getElementsByClassName(class_name_for_all),
    parent_all = document.getElementById(name_id_parent_all);
// get coord html element
function getCoords(elem) {
    var box = elem.getBoundingClientRect();
        return {
        top: box.top + pageYOffset,
        left: box.left + pageXOffset
        };
    }
// main func Drag'n'Drop
function DrugDrop() {
    for (var i = 0; i < all.length; i++) {
        (function (i) {
            var cur = all[i],
                place_div = document.createElement('div');
            cur.onmousedown = function (e) {
                if (e.which != 1) { // если клик правой кнопкой мыши
                    return; // то он не запускает перенос
                }
                cur.style.width = cur.clientWidth + 'px';
                cur.style.height = cur.clientHeight + 'px';
                // calc coord
                var coords = getCoords(cur);
                // var shiftX = e.pageX - coords.left;
                var shiftY = e.pageY - coords.top;
                if ( Math.abs(shiftY) < 5 ) {
                    return; // ничего не делать, мышь не передвинулась достаточно далеко
                }
                // begin remove
                cur.style.position = 'absolute';
                cur.style.zIndex = 9999;
                parent_all.appendChild(cur);
                moveAt(e);
                // begin insert place_div
                place_div.className = class_name_for_place_div;
                place_div.style.width = cur.clientWidth + 'px';
                place_div.style.height = cur.clientHeight + 'px';
                parent_all.insertBefore(place_div, all[i+1]);
                // func remove 'moveAt'
                function moveAt(e) {
                    //cur.style.left = coords.left + 'px';
                    cur.style.top = e.pageY - shiftY - 383 + 'px';
                }

                document.onmousemove = function (e) {
                    moveAt(e);
                    for (var j = 0; j < all.length; j++) {
                        if (parseInt(all[j].offsetTop) + 383 == e.pageY) {
                            if (j + 1 == all.length) {
                                parent_all.appendChild(place_div);
                            } else {
                                parent_all.insertBefore(place_div, all[j + 1]);
                            }
                        }
                        if (parseInt(all[j].offsetTop) + all[j].offsetHeight +383 == e.pageY) {
                            parent_all.insertBefore(place_div, all[j]);
                        }
                    }
                };
                cur.onmouseup = function () {
                    cur.style.position = '';
                    cur.style.zIndex = '';
                    cur.style.left = '';
                    cur.style.top = '';
                    parent_all.replaceChild(cur, place_div);
                    document.onmousemove = null;
                    cur.onmouseup = null;
                    all = document.getElementsByClassName(class_name_for_all);
                    DrugDrop();
                    // ajax
                    // place your code, if you can
                    change_content(all);

                };
            }
        })(i);
    }
}
DrugDrop();

function change_content(all) {
    var number_all = [];
    for (var g = 0; g<all.length; g++) {
        number_all.push(all[g].getAttribute('data-num_less'));
    }
    var id_course = parent_all.getAttribute('data-id_course');
    AJAX({url: "/course/"+id_course, data: {list: number_all}});
    var all_num = document.getElementsByClassName('number_less');
    for (var z = 0; z<all_num.length; z++) {
        all_num[z].innerHTML = z+1;
    }
}