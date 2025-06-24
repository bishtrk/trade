import { NseIndia } from  "stock-nse-india";
const  nseIndia = new  NseIndia()
// To get all symbols from NSE
nseIndia.getAllStockSymbols().then(symbols  => {
console.log(symbols)
})

// To get equity details for specific symbol
nseIndia.getEquityDetails('IRCTC').then(details  => {
console.log(details)
})

// To get equity historical data for specific symbol
const range = {
    start: new Date("2010-01-01"),
    end: new Date("2021-03-20")
}
nseIndia.getEquityHistoricalData(symbol, range).then(data => {
    console.log(data)
})