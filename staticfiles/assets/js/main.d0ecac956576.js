jQuery(document).ready(function($) {
    $(".clickable-row").click(function() {
        var id = $(this).attr('id');
        $("a[id='" + id + "']")[0].click();
    });
});

// Sortable table
$(document).ready(function() {
    var table = $('.sortable').DataTable({
        "paging":   false,
        "dom":'lrtp'
    });
    
    $( '.platform-select', this ).on( 'change', function () {
        table.search(this.value).draw();
    });
});

// Read more
$('.readMore').click(function(){
    $('.read').toggleClass('reading-more');
    if($(this).text()=='Show Less') $(this).text('Show More'); 
    else  $(this).text('Show Less'); 
});

// Append to Amazon link
$('a').each(function(){
    if ($(this).attr('href').indexOf('amazon.com') > 0) {
        $(this).attr('href', $(this).attr('href').split('?')[0] + '?tag=austextbookex-22')
    }
});

