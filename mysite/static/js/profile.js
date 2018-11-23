$(document).ready(function () {
    window.setInterval(updatePosts, 5000);

    // using jQuery
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    var csrftoken = getCookie('csrftoken');

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

});


function updatePosts() {
    $.ajax({
        async: false,
        cache: false,
        dataType: 'json',
        type: 'GET',
        url: '/updateProfilestream',

        success: function (data) {
            $.each(data, function (index, post) {
                const str1 = "<div class=\"card flex-md-row mb-4 mt-4 box-shadow h-md-250\">" +
                    "<div class=\"card-body d-flex col-md-8 flex-column align-items-start\">" +
                    "<div class=\"row mb-1\">"
                var s2 = ""
                var img = new Image();
                if (post.post_img) {
                    s2 = post.post_img
                } else {
                    s2 = "static/grumblr/img/profile1.jpg"
                }
                img.src = s2;
                img.height = 50;
                img.width = 50;
                $('#new_posts').prepend(
                    str1 +
                    img.outerHTML +
                    "<a class=\"d-inline-block mb-1 ml-3 text-primary align-content-center\"\n" +
                    "href=\"/profile?username={{ value.0 }}\"><strong>" + post.post_username + "</strong></a>\n" +
                    "</div>\n" +
                    "<h4 class=\"mb-0\">\n" +
                    "<p class=\"text-dark\" href=\"#\">" + post.post_title + "</p>\n" +
                    "</h4>\n" +
                    "<div class=\"mb-1 text-muted\">" + post.post_published_date + "</div>\n" +
                    "<p class=\"card-text mb-auto\">" + post.post_content + "</p>\n" +
                    "</div>\n" +
                    "</div>"
                )
                ;
            });
        },
    });
}