$(document).ready(function() {
    $('a[href^="#"]').on('click', function(e) {
        e.preventDefault();
        
        var target = this.hash;
        var $target = $(target);
        
        $('html, body').stop().animate({
            scrollTop: ($target.offset().top - 50)
        }, 1000, 'swing');
    });
    
    $('.cta-button').on('click', function(e) {
        e.preventDefault();
        window.location.href = '/start_trading';
    });
});