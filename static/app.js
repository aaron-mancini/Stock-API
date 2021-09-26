searchTerms = ["NEE", "AAPL", "AMD", "MSFT"];
$( function() {
    $( "#search" ).autocomplete({source: searchTerms});
})

$("#add-stock").on("click", "p", async function(evt) {
    evt.preventDefault();
    let $stockName = $("#stock-name").text();
    let $ticker = $("#ticker").text();
    let $watchlistId = this.id;
    let $stockId = $("#stock-name").parent().attr('id')
    const res = await axios.request({
        method: 'POST',
        url: "http://127.0.0.1:5000/update-watchlist",
        params: {watchlist: $watchlistId, stock: $stockName, ticker: $ticker, stockId: $stockId}})
    if (res.data !== "OK") {
        $("#stock-name").parent().attr("id", `${res.data}`)
    }
});
