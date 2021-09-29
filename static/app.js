
// Add or remove stock from watchlist.
$("#add-stock").on("click", "p", async function(evt) {
    evt.preventDefault();
    
    let $ticker = $("#ticker").text();
    let $watchlistId = this.id;
    
    const res = await axios.request({
        method: 'POST',
        url: "http://127.0.0.1:5000/update-watchlist",
        params: {watchlist: $watchlistId, ticker: $ticker}})
    
});

// debouncing functino
const debounce = (func, delay) => {
    let debounceTimer
    return function() {
        const context = this
        const args = arguments
            clearTimeout(debounceTimer)
                debounceTimer
            = setTimeout(() => func.apply(context, args), delay)
    }
}

debounce($(function(){
    $('#search').autocomplete({
        source: async function (query, done) {
            // Do Ajax call or lookup locally, when done,
            // call the callback and pass your results:
            // let searchTerm = this.value;
            
            const res = await axios.request({
                method: 'GET',
                url: 'https://apidojo-yahoo-finance-v1.p.rapidapi.com/auto-complete',
                params: {q: query.term, region: 'US'},
                headers: {
                    'x-rapidapi-host': 'apidojo-yahoo-finance-v1.p.rapidapi.com',
                    'x-rapidapi-key': apiKey
                }
            })
            let stockSuggestions = res.data.quotes;
            let searchTerms = [];
            for (let stock of stockSuggestions) {
                if (stock.exchange == 'NMS' || stock.exchange == 'NYQ') {
                    searchTerms.push({ label : `${stock.shortname} | ${stock.symbol}`, value : stock.symbol })
                };
            };
    
    
            done(searchTerms);
        },
        
    });
}), 500);

// check price change and percent change and add classes based on color.

$(document).ready(function() {
    $(".price-change").each(function() {
        let num = this.innerText
        $(this).addClass( num < 0 ? "neg" : "pos");
    });
});

$(document).ready(function() {
    $(".percent-change").each(function() {
        let num = this.innerText
        $(this).addClass( num < 0 ? "neg" : "pos");
        $(this).append("%")
    });
});

// delete watchlist confirm

$(".wl-delete").on("click", function(evt) {
    evt.preventDefault();
    id = this.id
    const response = confirm("Are you sure you want to delete?");
    if (response == true) {
        window.location.replace(`http://127.0.0.1:5000/delete/watchlist/${id}`)
    } else {
        window.location.replace("https://www.w3schools.com/howto/howto_js_redirect_webpage.asp")
    }
});