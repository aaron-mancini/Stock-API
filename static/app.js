
// Add or remove stock from watchlist.
$("#add-stock").on("click", "p", async function(evt) {
    evt.preventDefault();
    let $ticker = $("#ticker").text();
    let $watchlistId = this.id;
    let $watchlistInfo = $(`#${$watchlistId}`)
    let wlname = $watchlistInfo.data().wlname
    if ($watchlistInfo.text().includes("Add")) {
        $watchlistInfo.text(`Remove from ${wlname}`)
    } else {
        $watchlistInfo.text(`Add to ${wlname}`)
    }
    
    const res = await axios.request({
        method: 'POST',
        url: "https://stock-watch-news.herokuapp.com/update-watchlist",
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

            const res = await axios.request({
                method: 'GET',
                url: "https://stock-watch-news.herokuapp.com/search",
                params: {query: query.term}})
            console.log(res)
            let stockSuggestions = res.data.quotes;
            let searchTerms = [];
            for (let stock of stockSuggestions) {
                if (stock.exchange == 'NMS' || stock.exchange == 'NYQ') {
                    searchTerms.push({ label : `${stock.shortname} | ${stock.symbol}`, value : stock.symbol })
                };
            };
    
    
            done(searchTerms);
        },
        minLength: 2,
        select: function(event, ui) {
            $("#search").val(ui.item.value)
            $("#search-form").submit();
        }
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
        window.location.replace(`https://stock-watch-news.herokuapp.com/delete/watchlist/${id}`)
    };
});

// delete user confirm

$(".user-delete").on("click", function(evt) {
    evt.preventDefault();
    id = this.id
    const response = confirm("Are you sure you want to delete your account? This cannot be undone.");
    if (response == true) {
        window.location.replace(`https://stock-watch-news.herokuapp.com/delete/user/${id}`)
    };
});

// remove flash message

$(".flash-delete").on("click", function(evt) {
    evt.preventDefault();
    $(this).parent().remove()
})

// remove a stock from watchlist page

$(".remove-stock").on("click", async function(evt) {
    evt.preventDefault();
    let row = $(this).parent().parent()
    let $ticker = this.id
    let $watchlistId = $(".wl-delete").attr("id")
    
    const res = await axios.request({
        method: 'POST',
        url: "https://stock-watch-news.herokuapp.com/update-watchlist",
        params: {watchlist: $watchlistId, ticker: $ticker}})

    row.remove()
    
})

// check price change and percent change, for stock info not watchlist info.

$(document).ready(function() {
    $(".stock-price-change").each(function() {
        let num = this.innerText
       
        $(this).addClass( num < 0 ? "neg" : "pos");  
    });
});

// try removing the each function. you only need one thing not multiple
$(document).ready(function() {
    $(".stock-percent-change").each(function() {
        let num = this.innerText;
        
        $(this).addClass( num < 0 ? "neg" : "pos");
        $(this).append("%")
    });
});

$("#search").css('max-width','7rem')