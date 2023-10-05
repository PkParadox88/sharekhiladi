<script>
$(document).ready(function() {
    function updateTable() {
        // Retrieve the URL from the data-url attribute
        var updateDataUrl = $("#update-data").data("url");

        // Make an AJAX request to the URL
        $.ajax({
            url: updateDataUrl,
            method: "GET",
            dataType: "json",
            success: function(data) {
                // Clear the existing table rows
                $("#stockTableBody").empty();

                // Iterate through the received data and update the table
                $.each(data.stocks, function(index, stock) {
                    $("#stockTableBody").append(
                        "<tr>" +
                        "<td>" + (index + 1) + "</td>" +  // Display S.N.
                        "<td>" + stock.symbol + "</td>" +
                        "<td>" + stock.volume + "</td>" +
                        "<td>" + stock.ltp + "</td>" +
                        "<td>" + stock.percentChange + "</td>" +
                        "<td>" + stock.high + "</td>" +
                        "<td>" + stock.low + "</td>" +
                        "<td>" + stock.open + "</td>" +
                        "<td>" + stock.lastTradedVolume + "</td>" +
                        "<td>" + stock.lastTradedTime + "</td>" +
                        "<td>" + stock.change + "</td>" +
                        "<td>" + stock.previousClose + "</td>" +
                        "</tr>"
                    );
                });
            },
            error: function(xhr, status, error) {
                console.error("Error fetching data: " + error);
            }
        });
    }
    // Load the table immediately when the page is ready
    updateTable();

    // Periodically update the table every 1.5 seconds
    setInterval(updateTable, 1500);
});
</script>