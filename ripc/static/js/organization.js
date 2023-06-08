$(document).ready(function() {
  $("#org-form").submit(function(event) {
    event.preventDefault();

    $.ajax({
      type: "POST",
      url: $(this).attr("action"),
      data: $(this).serialize(),
      success: function(data) {
        window.location.href = "/organizations/";
      },
      error: function(data) {
        $("#form-errors").html(data.responseJSON.errors.name);
      }
    });
  });
});