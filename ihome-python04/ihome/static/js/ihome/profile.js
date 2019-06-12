function showSuccessMsg() {
    $('.popup_con').fadeIn('fast', function() {
        setTimeout(function(){
            $('.popup_con').fadeOut('fast',function(){}); 
        },1000) 
    });
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}




    // $("form-avatar").submit(function (e) {
    //     console.log(123);
    // //    阻止表单的默认行为
    //     e.preventDefault();
    //     //利用jquery.form.min.js提供的ajax的submit对表单进行异步提交
    //     $(this).ajaxSubmit({
    //         url:'/api/v1.0/users/avatar',
    //         type:'post',
    //         dataType:'json',
    //         headers:{
    //             "X-CSRFToken":getCookie("csrf_token")
    //         },
    //         success:function (resp) {
    //             console.log(resp)
    //             if (resp.errno=="0"){
    //             //    上传成功
    //             var avatarUrl=resp.data.avatar_url;
    //             $("#user-avatar").attr("src",avatarUrl);
    //             }else{
    //                 alert(resp.errmsg);
    //             }
    //         }
    //
    //     });
    //
    // })
    // console.log($("#scBtn"));
    //
    // $("#scBtn").click(function () {
    //     var imgFile=$("input[type=file]").val();
    //     console.log(123);
    //     console.log(imgFile);
    //     $.ajax({
    //         url:"/api/v1.0/users/avatar",
    //         type:"POST",
    //         dataType:'json',
    //         headers:{
    //             "X-CSRFToken":getCookie("csrf_token")
    //         },
    //         data:{"avatar":imgFile},
    //         success:function (e) {
    //             console.log(e)
    //         }
    //     })
    // })





