function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function(){
    // $('.popup_con').fadeIn('fast');
    // $('.popup_con').fadeOut('fast');
    // <option value="1">东城区</option>
    $.ajax("/api/v1.0/areas",function (res) {
        console.log(res)
    })
})