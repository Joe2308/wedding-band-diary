$(document).ready(function () {
    $(".sidenav").sidenav({edge: "right"});
    $('.tooltipped').tooltip();
    $('select').formSelect();
    $('.modal').modal();
    $('.datepicker').datepicker({
        format: "mmm d, yy"
    });
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