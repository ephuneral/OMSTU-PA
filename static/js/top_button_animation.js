      $(document).ready(function(){
              $("a[href*=#]").bind("click", function(e){
                      var anchor = $(this);
                      $('html, body').stop().animate({
                              scrollTop: $(anchor.attr('href')).offset().top-1 /* -30 – можно менять для учёта фиксированной шапки*/
                      }, 1000); /* 1000 – можно менять для желаемой скорости прокрутки*/
                        e.preventDefault();
                      return false;
              });
      });

$(function() {
    $(window).scroll(function() {
        if($(this).scrollTop() != 0) {
        $('#toTop').fadeIn();
        } else {
            $('#toTop').fadeOut();
        }
    });
$('#toTop').click(function() {
    $('body,html').animate({scrollTop:0},800);
    });
});