$(document).ready(function() {
    var max_fields = 10;
    var wrapper = $(".container-ingredient");
    var add_button = $(".add_form_field_ingredient");
    var x = 1;
    $(add_button).click(function(e) {
        e.preventDefault();
        if (x < max_fields) {
                x++;
        console.log("Iteration: "+x);
                var div_str = '<div><input type="text" name="ingredient_'+x+'" placeholder="Extra Ingredient"/><a href="#" class="delete">Delete</a></div>'
                $(wrapper).append(div_str); //add input box
        } else {
                alert('You Reached the limits')
        }
    });

    $(wrapper).on("click", ".delete", function(e) {
        e.preventDefault();
        $(this).parent('div').remove();
        x--;
})
});

    $(document).ready(function() {
    var max_fields = 10;
    var wrapper = $(".container-directions");
    var add_button = $(".add_form_field_step");
    var x = 1;
    $(add_button).click(function(e) {
        e.preventDefault();
        if (x < max_fields) {
                x++;
                //var div_str = '<div><input type="textarea" name="step_'+x+'"/><a href="#" class="delete">Delete</a></div>'
                var div_str = '<div><textarea id="directions" name="directions_'+x+'" placeholder="And also this..." style="height:100px"></textarea><a href="#" class="delete">Delete</a></div>'
        $(wrapper).append(div_str); //add input box
        } else {
                alert('You Reached the limits')
        }
    });

    $(wrapper).on("click", ".delete", function(e) {
        e.preventDefault();
        $(this).parent('div').remove();
        x--;
})
});