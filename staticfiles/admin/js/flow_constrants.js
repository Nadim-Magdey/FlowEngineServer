document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".dual-listbox").forEach(function(container){

        const left = container.querySelector(".dual-left");
        const right = container.querySelector(".dual-right");

        container.querySelectorAll(".dual-move").forEach(function(btn){
            btn.addEventListener("click", function(){
                const direction = btn.dataset.direction;

                if(direction === "right"){
                    Array.from(left.selectedOptions).forEach(function(opt){
                        right.appendChild(opt);
                    });
                }

                if(direction === "left"){
                    Array.from(right.selectedOptions).forEach(function(opt){
                        left.appendChild(opt);
                    });
                }
            });
        });

    });
});
