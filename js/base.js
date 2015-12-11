/** google global namespace for Google projects. */
//var google = google || {};

/** appengine namespace for Google Developer Relations projects. */
//google.appengine = google.appengine || {};

/** samples namespace for App Engine sample code. */
//google.appengine.samples = google.appengine.samples || {};

/** hello namespace for this sample. */
//google.appengine.samples.hello = google.appengine.samples.hello || {};


/**Enables the event listener for that button
google.appengine.samples.hello.enableButtons = function() {
  var getGreeting = document.querySelector('#song_search'); // this will add then event listener for the search for songs button
  getGreeting.addEventListener('click', function(e) {
    google.appengine.samples.hello.getGreeting(
        document.querySelector('#id ').value);
  });

  var listGreeting = document.querySelector('#listGreeting');
  listGreeting.addEventListener('click',
      google.appengine.samples.hello.listGreeting);

};
*/

//sets the event listener to the form

var searchAlbums = function (query) {
  document.getElementById("results").classList.remove("dont_show");
    $.ajax({
        url: 'https://api.spotify.com/v1/search',
        data: {
            q: query,
            type: 'track',
            market: 'US',
            limit: '10'
        },
        success: function (response) {
          //we need to get the template
          $.get("")


        }
    });
};


document.getElementById("song_search").addEventListener("submit", function (e) {
    e.preventDefault();
    searchAlbums(document.getElementById("query").value);
    //searchAlbums(document.getElementById('query').value);
}, false);
