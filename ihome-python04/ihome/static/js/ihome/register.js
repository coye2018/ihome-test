function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

var imageCodeId = "";


//生成UUID
function generateUUID() {
    var d = new Date().getTime();
    if(window.performance && typeof window.performance.now === "function"){
        d += performance.now(); //use high-precision timer if available
    }
    var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = (d + Math.random()*16)%16 | 0;
        d = Math.floor(d/16);
        return (c=='x' ? r : (r&0x3|0x8)).toString(16);
    });
    return uuid;
}


//形成图片验证码后端地址，设置到页面中，让浏览器请求验证码图片
function generateImageCode() {
    //1、生成验证码编号
    imageCodeId=generateUUID();
    var url='/api/v1.0/image_codes/'+imageCodeId
    $(".image-code>img").attr('src',url)
}


//点击发送短信验证码被执行的函数
function sendSMSCode() {
    $(".phonecode-a").removeAttr("onclick");
    var mobile = $("#mobile").val();
    if (!mobile) {
        $("#mobile-err span").html("请填写正确的手机号！");
        $("#mobile-err").show();
        $(".phonecode-a").attr("onclick", "sendSMSCode();");
        return;
    } 
    var imageCode = $("#imagecode").val();
    if (!imageCode) {
        $("#image-code-err span").html("请填写验证码！");
        $("#image-code-err").show();
        $(".phonecode-a").attr("onclick", "sendSMSCode();");
        return;
    }

    /*
    $.get("/api/smscode", {mobile:mobile, code:imageCode, codeId:imageCodeId},
        function(data){
            if (0 != data.errno) {
                $("#image-code-err span").html(data.errmsg); 
                $("#image-code-err").show();
                if (2 == data.errno || 3 == data.errno) {
                    generateImageCode();
                }
                $(".phonecode-a").attr("onclick", "sendSMSCode();");
            }   
            else {
                var $time = $(".phonecode-a");
                var duration = 60;
                var intervalid = setInterval(function(){
                    $time.html(duration + "秒"); 
                    if(duration === 1){
                        clearInterval(intervalid);
                        $time.html('获取验证码'); 
                        $(".phonecode-a").attr("onclick", "sendSMSCode();");
                    }
                    duration = duration - 1;
                }, 1000, 60); 
            }
    }, 'json'); */
    //构造向后端请求的参数
    var req_data={
        image_code:imageCode,//图片验证码的值
        image_code_id:imageCodeId,//图片验证码的编号（全局变量）
    }
    $.get("/api/v1.0/sms_codes/"+mobile,req_data,function (resp) {
    //    resp是后端返回的响应值，因为后端返回的是json字符串
    //    所以ajax帮助我们我们把这个json字符串转换为js对象，resp就是转换后的对象
        if (resp.errno=="0"){
        //    表示发送成功
            var phonecode_a=$(".phonecode-a");
            var durantion=60;
            var timer=setInterval(function () {
                if (durantion<=1){
                    clearInterval(timer);
                    phonecode_a.html("获取验证码");
                    phonecode_a.attr("onclick", "sendSMSCode();");
                } else{
                    phonecode_a.html(durantion+"秒");
                    durantion--;

                }
            },1000);
        }else{
        //    如果是错误的返回。。
            alert(resp.errmsg);
            $(".phonecode-a").attr("onclick", "sendSMSCode();");
        }
    })
}

$(document).ready(function() {

    //开场刷新给个图片验证码
    generateImageCode();
    $("#mobile").focus(function(){
        $("#mobile-err").hide();
    });
    $("#imagecode").focus(function(){
        $("#image-code-err").hide();
    });
    $("#phonecode").focus(function(){
        $("#phone-code-err").hide();
    });
    $("#password").focus(function(){
        $("#password-err").hide();
        $("#password2-err").hide();
    });
    $("#password2").focus(function(){
        $("#password2-err").hide();
    });

    //表单提交，把默认的关闭掉，为表单提交补充自定义的函数行为（提交事件e）
    $(".form-register").submit(function(e){
        //组织浏览器对于表单的默认自动提交行为
        e.preventDefault();
        mobile = $("#mobile").val();
        phoneCode = $("#phonecode").val();
        passwd = $("#password").val();
        passwd2 = $("#password2").val();
        if (!mobile) {
            $("#mobile-err span").html("请填写正确的手机号！");
            $("#mobile-err").show();
            return;
        } 
        if (!phoneCode) {
            $("#phone-code-err span").html("请填写短信验证码！");
            $("#phone-code-err").show();
            return;
        }
        if (!passwd) {
            $("#password-err span").html("请填写密码!");
            $("#password-err").show();
            return;
        }
        if (passwd != passwd2) {
            $("#password2-err span").html("两次密码不一致!");
            $("#password2-err").show();
            return;
        }

    //    调用ajax向后端发送注册请求
        var req_data={
            mobile:mobile,
            sms_code:phoneCode,
            password:passwd,
            password2:passwd2,
            // csrf_token:"xxxxx",
        };
        // request.data  表单验证的话这样取值
        //request.form.get("csrf_token")
        var req_json=JSON.stringify(req_data);
        $.ajax({
            url:"/api/v1.0/users",
            type:"post",
            data:req_json,
            contentType:"application/json",
            dataType:"json",
            headers: {
                //这里通过正则分割了拿到想要的cookie
                "X-CSRFToken":getCookie("csrf_token")
            },//请求头，将csrf_token值放到请求中，方便后端csrf进行验证
            success:function (res) {
                if (res.errno=="0"){
                    alert("注册成功");
                //    注册成功，跳转到主页
                    location.href="/index.html";
                } else{
                    alert(res.errmsg);
                }
            }
        })

    });
})