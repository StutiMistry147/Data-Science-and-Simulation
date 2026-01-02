mtype = { buy, sell, confirmed, filled };

chan toExchange = [1] of { mtype, byte };
chan fromExchange = [1] of { mtype };

active proctype Trader() {
    toExchange ! buy, 150; 
    if
    :: fromExchange ? confirmed -> 
       printf("Order Acknowledged\n");
       fromExchange ? filled;
       printf("Order Executed\n");
    fi;
}

active proctype Exchange() {
    mtype msg;
    byte price;
    do
    :: toExchange ? msg, price -> 
       fromExchange ! confirmed;
       fromExchange ! filled;
    od
}
