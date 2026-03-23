document.addEventListener("DOMContentLoaded", function () {

    // Handle all dual-list widgets on the page
    document.querySelectorAll(".dual-listbox").forEach(function(container){

        const left = container.querySelector(".dual-left");
        const right = container.querySelector(".dual-right");

        // Move buttons
        container.querySelectorAll(".dual-move").forEach(function(btn){
            btn.addEventListener("click", function(){
                const direction = btn.dataset.direction;

                if(direction === "right"){
                    Array.from(left.selectedOptions).forEach(function(opt){
                        opt.selected = false;   // deselect in left
                        right.appendChild(opt); // move to right
                    });
                }
                
                
                if(direction === "left"){
                    Array.from(right.selectedOptions).forEach(function(opt){
                        opt.selected = false;   // deselect in right
                        left.appendChild(opt);  // move back to left
                    });
                }
            });
        });

        // Optional: double-click to move quickly
        [left, right].forEach(function(select){
            select.addEventListener("dblclick", function(){
                const target = select === left ? right : left;
                Array.from(select.selectedOptions).forEach(function(opt){
                    opt.selected = false;
                    target.appendChild(opt);
                });
            });
        });

    });

    // On form submit: make sure right options are selected, left options deselected
    document.querySelectorAll("form").forEach(function(form){
        form.addEventListener("submit", function(){
            // Right options must be selected
            form.querySelectorAll(".dual-right option").forEach(function(opt){
                opt.selected = true;
            });
            // Left options must be deselected
            form.querySelectorAll(".dual-left option").forEach(function(opt){
                opt.selected = false;
            });
        });
    });

});
