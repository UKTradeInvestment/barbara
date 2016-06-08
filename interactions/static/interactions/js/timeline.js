/**
 *
 * Behold my Javascript, for it is frightening and terrible.
 *
 */

var accounting = [];
var shell = $("#cd-timeline");

function timeline_insert(interaction) {
    console.log("Inserting interaction " + interaction.id);
    var $moment = $("" +
        '<div class="cd-timeline-block">' +
            '<div class="cd-timeline-img cd-location">' +
                '<img src="' + Barbara.urls.static_files + 'contrib/icons/' + interaction.icon + '.svg" alt="' + interaction.icon + '">' +
            '</div>' +
            '<div class="cd-timeline-content">' +
                '<h2>' + interaction.subject + '</h2>' +
                '<p>' + interaction.body_html + '</p>' +
                '<a href="#" class="cd-read-more">Read more</a>' +
                '<span class="cd-date">' + moment(interaction.created).format('MMMM Do YYYY, h:mm:ss a') + '</span>' +
            '</div>' +
        '</div>' +
    '');
    shell.prepend($moment);
}

function timeline_fetch() {
    console.log("Querying the API");
    $.getJSON(Barbara.urls.api.interactions.list, function(data){
        for (var i = 0; i < data.results.length; i++){
            var interaction = data.results[i];
            if (accounting.indexOf(interaction.id) == -1) {
                timeline_insert(interaction);
                accounting.push(interaction.id);
            }
        }
        setTimeout(timeline_fetch, 5000);
    });
}

timeline_fetch();