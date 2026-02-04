document.getElementById("like-btn").onclick = function(){
    $.ajax({
        type: "POST",
        url: "/backers/projects/see/{{backer}}/like/{{ject}}",
        message: text,
        success: function(data){
            alert("Message sent");
        },
        error: function(xhr, status, error){
            alert("Error: " + error);
        }
    });
}