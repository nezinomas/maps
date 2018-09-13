    $(function () {
        $('.com').on('click', function () {
            var post_link = $(this).attr("value1");
            var post_id = $(this).attr("value2");
            var click_status = $('#link_' + post_id).attr('value3')

            var get_remote = false;
            if (click_status == 'not-clicked') {
                get_remote = true;
            }
            $('.ajaxProgress').show();
            $.ajax({
                type: 'get',
                url: post_link,
                data: { post_id: post_id, get_remote: get_remote },
                success: function (data) {

                    if (click_status == 'not-clicked') {

                        $('#'+post_id).html(data.html);
                        $('#'+post_id).show();

                        $('#link_'+post_id).attr('value3', 'clicked');
                        $('#link_'+post_id).html('Slėpti komentarus')
                    } else {
                        $('#'+post_id).hide()

                        $('#link_'+post_id).attr('value3', 'not-clicked');
                        $('#link_'+post_id).html('Rodyti komentarus')
                    }
                    $('.ajaxProgress').hide();

                },
                error: function (xhr, status, error) {
                    // shit happens friends!
                }
            });
        });
    });

