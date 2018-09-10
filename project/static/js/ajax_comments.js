    $(function () {
        $('.com').on('click', function () {
            var post_link = $(this).attr("value1");
            var post_id = $(this).attr("value2");

            $.ajax({
                type: 'get',
                url: post_link,
                data: { post_id: post_id },
                success: function (data) {

                    var v = $('#link_'+post_id).attr('value3')

                    if (v == 'not-clicked') {
                        $('#'+post_id).html(data.html);
                        $('#'+post_id).show();

                        $('#link_'+post_id).attr('value3', 'clicked');
                        $('#link_'+post_id).html('Slėpti komentarus')
                    } else {
                        $('#'+post_id).hide()

                        $('#link_'+post_id).attr('value3', 'not-clicked');
                        $('#link_'+post_id).html('Rodyti komentarus')
                    }

                },
            });
        });
    });

