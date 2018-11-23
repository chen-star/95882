$(document).ready(function () {
    updateComments();
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
        url: '/updatefollerstream',

        success: function (data) {
            $.each(data, function (index, post) {
                const str1 = "<div class=\"card flex-md-row mb-4 mt-4 box-shadow h-md-250\">" +
                    "<div class=\"card-body d-flex col-md-8 flex-column align-items-start\">" +
                    "<div class=\"row mb-1\">";
                var s2 = "";
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
                    "href=\"/profile?username=" + post.post_username + "\"><strong>" + post.post_username + "</strong></a>\n" +
                    "</div>\n" +
                    "<h4 class=\"mb-0\">\n" +
                    "<p class=\"text-dark\">" + post.post_title + "</p>\n" +
                    "</h4>\n" +
                    "<div class=\"mb-1 text-muted\">" + post.post_published_date + "</div>\n" +
                    "<p class=\"card-text mb-auto\">" + post.post_content + "</p><hr>\n" +
                    "                                <form id=\"" + post.post_id + "\" method=\"post\"\n" +
                    "                                      class=\"new_comment\">\n" +
                    "                                    <input type=\"text\" name=\"comment_content\" id=\"" + "new_input_comment" + post.post_id + "\"\n" +
                    "                                           placeholder=\"add comment here..\" required><br><br>\n" +
                    "                                    <input type=\"text\" name=\"post_id\" id=\"post_id\" value=\"" + post.post_id + "\"\n" +
                    "                                           hidden=\"hidden\">\n" +
                    "                                    <button class=\"btn btn-sm btn-primary\" type=\"submit\">Comment</button>\n" +
                    "                                </form><hr>" +
                    "<div class=\"panel-footer\" id=\"previous_comments" + post.post_id + "\">" +
                    "</div>" +
                    "</div>\n" +
                    "</div>"
                )
                ;
            });
        },
    });
}

function updateComments() {
    $(document).on('submit', 'form.new_comment', function (event) {
        console.log("!!!!");
        event.preventDefault();
        var post_id = $(this).attr('id');
        var comment_content = $("#new_input_comment" + post_id).val();
        $.ajax({
            async: false,
            cache: false,
            dataType: 'json',
            type: 'POST',
            url: '/add_comment',
            data: {'comment_content': comment_content, 'post_id': post_id},

            success: function (data) {
                console.log(data);
                var com = data;
                var str1 = "                                                <div class=\"row mb-1\">\n";
                var s2 = "";
                var img = new Image();
                if (com.com_img) {
                    s2 = com.com_img
                } else {
                    s2 = com.default_img
                }
                img.src = s2;
                img.height = 20;
                img.width = 20;
                $("#new_input_comment" + post_id).val('');
                console.log(post_id)
                $("#previous_comments" + post_id).append(
                    str1 + img.outerHTML +
                    "<a class=\"d-inline-block mb-1 ml-3 text-primary align-content-center\"\n" +
                    "href=\"/profile?username=" + com.com_username + "\"><strong>" + com.com_username + "</strong></a>\n" +
                    "                                                    <p align=\"right\" class=\"text-muted mr-2 pl-2\" size=\"\">\n" +
                    "                                                        <small>" + com.com_time + "</small>\n" +
                    "                                                    </p>\n" +
                    "                                                </div>\n" +
                    "                                                <p>" + com.com_content +
                    "                                                </p><hr>\n"
                );
            },
        });
    });
}