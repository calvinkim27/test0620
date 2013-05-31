(function ($, undefined) {
    "use strict";

    // http://stackoverflow.com/a/487084/676818
    function insertUrlParameter(sourceUrl, parameterName, parameterValue) {
        var urlParts = sourceUrl.split("?");
        var newQueryString = "?" + parameterName + "=" + parameterValue;
        if (urlParts.length > 1) {
            newQueryString += "&" + urlParts[1];
        }
        return urlParts[0] + newQueryString;
    }

    var rails = $.rails;

    // Handles "data-method" on links such as:
    // <a href="/users/5" data-method="delete" rel="nofollow" data-confirm="Are you sure?">Delete</a>
    $.rails.handleMethod = function(link) {
        var method = link.data('method'),
            target = link.attr('target'),
            href = insertUrlParameter(rails.href(link), '_method', method),
            csrf_token = $('meta[name=csrf-token]').attr('content'),
            csrf_param = $('meta[name=csrf-param]').attr('content'),
            form = $('<form method="post" action="' + href + '"></form>'),
            metadata_input = '';

        if (csrf_param !== undefined && csrf_token !== undefined) {
            metadata_input += '<input name="' + csrf_param + '" value="' + csrf_token + '" type="hidden" />';
        }

        if (target) { form.attr('target', target); }

        form.hide().append(metadata_input).appendTo('body');
        form.submit();
    };
})(jQuery);
