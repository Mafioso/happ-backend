$(document).ready(function(){
    $.get( "/api/v1/events.html", function( data ) {
      $( "#events_table tbody" ).html( data );
      alert( "Load was performed." );
    });
})
