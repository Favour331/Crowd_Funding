function change() {
    $.ajax({
        type: "POST",
        url: "/backers/projects/see/{{ace.Id}}/like/{{ace.id}}",
        message: text,
        success: function(data){
            alert("Message sent");
        },
        error: function(xhr, status, error){
            alert("Error: " + error);
        }
    });
}