$(document).ready(function () {
    $(".sidenav").sidenav({edge: "right"});
    $('.tooltipped').tooltip();
    $('select').formSelect();
});

$(function() { setTimeout(function() { 
    $("#form-alert").hide(1000); }, 2000); });

$(".field_icon").on("click", function () {
    $(this).toggleClass("fa-eye-slash fa-eye");
    var show = document.getElementById("password");
    if (show.type === "password") {
        show.type = "text";
    } else {
        show.type = "password";
    }
});