$(document).ready(function () {
    var makeItRain = function () {
        $('.rain').empty();
        var increment = 0;
        var drops = "";
        var backDrops = "";

        while (increment < 100) {
            var randoHundo = Math.floor(Math.random() * 98) + 1;
            var randoFiver = Math.floor(Math.random() * 4) + 2;
            increment += randoFiver;

            drops += `<div class="drop" style="left: ${increment}%; bottom: ${randoFiver + randoFiver - 1 + 100}%; animation-delay: 0.${randoHundo}s; animation-duration: 0.5${randoHundo}s;">
                        <div class="stem"></div>
                        <div class="splat"></div>
                      </div>`;

            backDrops += `<div class="drop" style="right: ${increment}%; bottom: ${randoFiver + randoFiver - 1 + 100}%; animation-delay: 0.${randoHundo}s; animation-duration: 0.5${randoHundo}s;">
                           <div class="stem"></div>
                           <div class="splat"></div>
                         </div>`;
        }

        $('.rain.front-row').append(drops);
        $('.rain.back-row').append(backDrops);
    };

    $(".splat-toggle.toggle").on("click", function () {
        $("body").toggleClass("splat-toggle");
        $(this).toggleClass("active");
        makeItRain();
    });

    $(".back-row-toggle.toggle").on("click", function () {
        $("body").toggleClass("back-row-toggle");
        $(this).toggleClass("active");
        makeItRain();
    });

    $(".single-toggle.toggle").on("click", function () {
        $("body").toggleClass("single-toggle");
        $(this).toggleClass("active");
        makeItRain();
    });

    makeItRain();
});




