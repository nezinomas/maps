// prevent default form submission
$(document).on('submit', '.modal-form', function (e) {
    e.preventDefault();
});


// close modal on Close Buton
$(document).on('click', '.modal-close', function (e) {
    modal_hide($(this).data("dismiss"));
});


// close modal on ESC
$(document).keydown(function (event) {
    if (event.keyCode == 27) {
        $('.modal-close').each(function () {
            modal_hide($(this).data("dismiss"));
        })
    }
});


// close modal on outside (e.g. containerModal) click
window.onclick = function(event) {
    let containers = ['mainModalContainer'];

    if (containers.includes(event.target.id)) {
        // strip 'Container' prefix
        let target = event.target.id.replace('Container', '');
        modal_hide(target);
    }
}


// show modal on click button with hx-target="#mainModal"
htmx.on("htmx:afterSwap", (e) => {
    let target = e.detail.target.id;
    let modals = ['mainModal'];

    if (modals.includes(target)) {
        $(`#${target}`).parent().show();
    }
})


// reload modal form with error messages or reset fields and close modal form
htmx.on("htmx:beforeSwap", (e) => {
    let target = e.detail.target.id;

    if (target == "mainModal" && !e.detail.xhr.response) {
        /* find submit button id */
        let subbmiter = e.detail.requestConfig.triggeringEvent.submitter.id;

        if(subbmiter == '_close') {
            /* remove error messages */
            $('.invalid-feedback').remove();
            $('.is-invalid').removeClass('is-invalid');
        }

        modal_hide(target);
        e.detail.shouldSwap = false;
    }
})


function hx_trigger() {
    let form = $('.modal-form');
    let trigger_name = form.attr("data-hx-trigger-form");

    if (trigger_name === 'None' || trigger_name == undefined) {
        return;
    } else {
        htmx.trigger("body", trigger_name, { });
    }
}


// hide modal
function modal_hide(target) {
    $(`#${target}`).parent().hide();
    hx_trigger();
}
